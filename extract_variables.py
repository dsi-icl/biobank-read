# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 16:12:24 2018

@author: Deborah
"""

import argparse
import pandas as pd
import numpy as np
import warnings
import re
import sys


'''Example run:
    python extract_variables.py \
        --csv x/y/z.csv \
        --html x/y/z.html \
        --excl x/y/z.csv \
        --vars <list of variables>, as is or in .txt file \
        --out <directory name> x1\y1 \
(optionally)
    	--visit 0/1/2/'all/ \ # Default: all. Keep all visits, or just baseline, 1st or 2nd revisit
        --remove_outliers True\False \
        --filter <list of conditions on variables in vars>, as is or in .txt file \
        --aver_visits True\False \
        --cov_corr True\False \
        --combine  inner\partial\outer (default=outer) \
                    inner = all extracted variables valid for each eid
                    outer = values for all eids returned
                    partial = at least one extracted variable must be valid
'''

# Function to deal nicely with Boolean parser options
# https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def str2boolorlist(v):
    if type(v) == str:
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    elif type(v) == list:
        return v
    else:
        raise argparse.ArgumentTypeError('Boolean value or list expected.')

parser = argparse.ArgumentParser(description="\n BiobankRead Extract_Variable. Does what it says hehe")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --csv and --html option are required")
in_opts.add_argument("--csv", metavar="{File1}", type=str, required=False, default=None, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=False, default=None, help='Specify the html file associated with the UKB application.')


out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--vars", metavar="{File3}", type=str, nargs='+', help='Specify variables to extract', required=True)
out_opts.add_argument("--out", metavar='PREFIX', type=str, required=True, help='Specify the name prefix to output files')


options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--remove_outliers", type=str2bool, default=False, nargs='+',action='store',help="Remove subjects with values beyond x std dev for any cont. variable. Format:[std.dev,one-sided,vars names...]")
options.add_argument("--filter", default=False, nargs='+', metavar="{File4}",type=str,action='store',help="Filter some variables based on conditions. Keep your requests simple ")
options.add_argument("--excl", metavar="{File5}", type=str, default=None, help='Specify the csv file of EIDs to be excluded.')
options.add_argument("--visit", metavar="0/1/2/all", default='all', help='Extract data for all visits, or baseline, 1st or 2nd re-visit only.')
options.add_argument("--combine", metavar="inner/partial/outer", type=str, default='outer', help='Specify how extracted variable data is combined for output.')

sums = parser.add_argument_group(title="Optional request for basic summary", description="Perform mean /cov/ corr/ dist plots for the data")
sums.add_argument("--aver_visits",default=False,type=str2boolorlist,help="get average measurement per visit")
sums.add_argument("--cov_corr",default=False,type=str2bool,help="Produce extra file of cov/corr between variables. Will have same location and similar name to main output file")

########################################################


def whitespace_search(smth,lst):
    smth = re.findall(r"[\w']+", smth)
    res = [c for c in lst if all(v in c for v in smth)]
    return res


def actual_vars(UKBr, smth):
    '''to use with :
        args.vars
        args.remove_missing if  > 1
        args.remove_outliers if  > 1
        args.aver_visit if  > 1
        args.cov_corr if  > 1
        '''
    actual_vars_list = []
    All=UKBr.Vars
    # turn strings to list
    if type(smth) is str:
        smth = [smth]
    for V in smth:
        if type(V) is not str:
            ValueError('Variables need to be strings')
            return None
        if ' ' in V: 
            res = whitespace_search(V,All)
        else:
            res = [x for x in All if V in x]
        for i in res:
            actual_vars_list.append(i)
    if len(actual_vars_list)==0: 
        ValueError('Variables names wrong. Go back to app documents and double-check what you actually have')
        return None
    actual_vars_list=list(set(actual_vars_list))
    return actual_vars_list
   
def bad_chars(UKBr, df):
    ''' Remove bad chars from Df column names '''
    special_char = UKBr.special_char
    for c in df.columns.tolist()[1::]:
        res =list(set(c) & set(special_char))
        if len(res)>0:
            C=c
            for u in res:
                C=C.replace(u,"")
            df.rename(columns={c: C},inplace=True)
    return df

def remove(UKBr, Df,args):
    if args.remove_missing:
        Df.replace(to_replace=-7,value=np.nan,inplace=True)
        Df.replace(to_replace=-3,value=np.nan,inplace=True)
        Df.dropna(inplace=True)
    else:
        vars_missing = actual_vars(UKBr, args.remove_missing).tolist()
        Df.replace(to_replace=-7,value=np.nan,subset=vars_missing,inplace=True)
        Df.replace(to_replace=-3,value=np.nan,subset=vars_missing,inplace=True)
        Df.dropna(subset=args.remove_missing,inplace=True)
    return Df

def average_visits(UKBr, Df,args):
    if type(args.aver_visits) == list:
        var_names = actual_vars(UKBr, args.aver_visits)
    else:
        var_names = actual_vars(UKBr, args.vars)
        
    types=[]
    for v in var_names:
        t=UKBr.variable_type(v)
        types.append(t)
    df_temp=pd.DataFrame(data={'vars':var_names, 'types': types})
    ## only for cont variables ##
    df_temp=df_temp[(df_temp['types']=='Continuous')|(df_temp['types']=='Integer')]
    if len(df_temp)==0:
        raise TypeError('Selected variables are not continuous')
    stuff=df_temp['vars'].tolist()
    for Y in stuff:
        cols = [x for x in Df.columns.tolist() if Y in x]
        if len(cols)==1:
            warnings.warn('Only one entry for variable '+str(Y)+'. Mean is redundant but OK')
        cols = ['eid']+cols ### this first
        df_sub = bad_chars(UKBr, Df[cols])
        Df_tmnp=UKBr.Mean_per_visit(df=df_sub)
    Df = pd.merge(Df,Df_tmnp,on='eid')
    return Df

def outliers(UKBr, Df, args):
    ''' Remove outliers from cont variables'''
    onesided=False
    if (type(args.remove_outliers) == list) and (len(args.remove_outliers) > 2):
        var_names = actual_vars(UKBr, args.remove_outliers[2::])
        std = args.remove_outliers[0]
        if len(args.remove_outliers) > 1:
            onesided = args.remove_outliers[1]
    else:
        var_names = actual_vars(UKBr, args.vars)
        std=4
    types=[]
    for v in var_names:
        t=UKBr.variable_type(v)
        types.append(t)
    df_temp=pd.DataFrame(data={'vars':var_names, 'types': types})
    ## only for cont variables ##
    df_temp=df_temp[(df_temp['types']=='Continuous')|(df_temp['types']=='Integer')]
    if len(df_temp)==0:
        warnings.warn('Selected variables are not continuous')
    stuff=df_temp['vars'].tolist()
    for Y in stuff:
        cols = [x for x in Df.columns.tolist() if Y in x]
        Df=UKBr.remove_outliers(df=Df,cols=cols,lim=std,one_sided=onesided) 
    return Df

def filter_vars(df,args):
    df_sub=pd.DataFrame(columns={'Vars','conds'})
        
    for cond in args.filter:
        #\S{1, 2} = 1-2 non-whitespace characters
        print(cond)
        match=re.search('([a-zA-Z0-9\s]+)(\S{1,2}\d+)',cond)
        match=re.search(r'([^=<>]*)([<=>][=]?[0-9]+(.[0-9]+)?)',cond)
        thevar=match.group(1)
        condition=match.group(2)
        # This adds rows under specified column headings
        #         Vars    Conds
        #    0    BMI     >34
        #    1    BMI     <99
        # etc
        df_sub=df_sub.append({'Vars':thevar,'conds':condition},ignore_index=True)
    print df_sub    
    # sanity check - make sure condition vars match extracted vars
    overlap=list(set(df_sub['Vars'])&set(args.vars))
    if len(overlap)==0:
        raise NameError('Conditional filtering does not match extracted variables')
    # Select condition rows where variables have been extracted
    df_sub=df_sub[[x in overlap for x in df_sub['Vars']]]
    # Apply filter
    
    rowslist = list(df_sub.index)
    for i in rowslist:
        # Get cases for this variable
        Ys = [x for x in df.columns.tolist() if df_sub['Vars'].loc[i] in x]
        if len(Ys)==0:
            Ys = whitespace_search(df_sub['Vars'].loc[i],df.columns.tolist())
        # Apply condition
        for y in Ys:
            evalstring = '(df["'+str(y)+'"]'+df_sub['conds'].loc[i]+') | (df["'+str(y)+'"].isnull())'
            print evalstring
            df = df[eval(evalstring)] # avoids dropping Na systematically
        


    return df


def filter_vars2(df, args):
    '''
    filter_vars2 applys conditions to extracted variables
    
    This is a rewrite of filtervars which takes advantage of the
    pandas.dataFrame.eval functionality
    
    The columns of the dataframe and the names of the variables are
    systematically renamed, to remove any characters which might break
    the query, using UKBr2.BiobankRead.clean_columns
    
    -Bill Crum
    '''
    
    # Temporarily rename columns to avoid problems with spaces
    [dfcolorig, df.columns] = UKBr2.BiobankRead.clean_columns(df)
    dfcol = df.columns.tolist()
    # Deal with conditions one at a time
    for cond in args.filter:
        # Extract the variable and condition
        # Format is: 'variable>=number'
        # ([^=<>]*) = string of any chars *except* =, <, >
        # [<=>][=] = any of >, <, = followed by optional =
        # [0-9]+ = any length string of digits 
        # (.[0-9]+)?) = 0 or 1 '.' + string of digits
        match=re.search(r'([^=<>]*)([<=>][=]?[0-9]+(.[0-9]+)?)',cond)
        if match is None:
            print('error processing condition', cond, '- skipping')
            continue
        #match=re.search('.*[=<>][0-9])
        thevar=match.group(1)
        [dummy, thevar] = UKBr2.BiobankRead.clean_columns(thevar)
        condition=match.group(2)
        # Get matching variables in main dataframe for this condition
        # NBNBNB THE CONDITION VARIABLE CAN BE A SUBSTRING OF THE FULL VARIABLE NAME
        # EG. BMI will match "Body mass index (BMI)"
        matchvars = [x for x in dfcol if thevar in x]
        # Apply the condition
        for match in matchvars:
            # Apply condition
            thiscondition = match+condition
            try:
                df = df[(df.eval(thiscondition)) | df.isna()]
                print('Applied condition', thiscondition)
            except Exception as e:
                print('condition', thiscondition, 'not found/evaluated in dataframe')    
                print('exception', e);
    # Restore columns
    df.columns = dfcolorig
    return df
   

def extract_the_things(UKBr, args):
    """
    Extract variables, apply options, return data-frame.
    
    Args:
    UKBr = UkBiobankRead class instance
    args = command-line args, specifically
            args.remove_missing
            args.remove_outliers
            args.aver_visits
            args.filter
            
    Returns:
    Df = data-frame
    
    """
    if UKBr.is_doc(args.vars[0]):
        args.vars=UKBr.read_basic_doc(args.vars[0])
#    if args.baseline_only:
#        print('Baseline visit data only')
    # Does keyword translation and returns actual variable names
    stuff=actual_vars(UKBr, args.vars)
    Df = UKBr.extract_many_vars(stuff,baseline_only=False, combine=args.combine)
    args.visit=str(args.visit)
    if args.visit in ['0','1','2']:
        tmp=UKBr.vars_by_visits(col_names=Df.columns.tolist(), visit=int(args.visit))
        tmp=['eid']+tmp
        Df=Df[tmp]
    if args.remove_outliers:
        print('Remove outliers for cont variables')
        Df = outliers(UKBr, Df,args)
    if args.aver_visits:
        print('Compute visit mean for cont variables')
        Df = average_visits(UKBr, Df,args)
    if args.filter:
        print('Filter variables based on condition')
        if UKBr.is_doc(args.filter):
            args.filter=UKBr.read_basic_doc(args.filter)
        Df = filter_vars(Df,args)#filter_vars2 - Bill's
    return Df


def float_to_cat(UKBr, df):
    var = df.columns.tolist()[1::]
    var = [x.split('_')[0] for x in var]
    types=lambda t: UKBr.variable_type(t)
    Types=[types(x) for x in var]
    cats = [Types.index(x) for x in Types if 'Categorical' in x]
    for i in cats:
        df[df.columns[i]]=df[df.columns[i]].astype('category')
    return df

def produce_plots(df,args):
    ''' stuff to make nice plots'''
    #### corr plot
    sns.set()
    df2=df[df.columns[1::]] # remove eid
        ## filter out shit variables
    Corr = df2.corr(min_periods=5)
    Corr.dropna(axis=0,how='all',inplace=True)
    Corr.dropna(axis=1,how='all',inplace=True)
    Corr=Corr[Corr.dropna(axis=1,how='any').columns.tolist()]
    colss=Corr.dropna(axis=1,how='any').columns.tolist()
    Corr=Corr.loc[colss]
    ##
    used_networks = [1, 5, 6, 7, 8, 12, 13, 17]
    network_pal = sns.husl_palette(8, s=.45)
    network_lut = dict(zip(map(str, used_networks), network_pal))
    networks = Corr.columns.get_level_values(0)
    network_colors = pd.Series(networks, index=Corr.columns).map(network_lut)
    sns_plot=sns.clustermap(Corr, center=0, cmap="vlag",
               row_colors=network_colors, col_colors=network_colors,
               linewidths=.75, figsize=(13, 13))
    sns_plot.savefig(args.out+'_corrPlot.png')
    return 

##### for testing on desktop ONLY!! #####
class Object(object):
    pass
args = Object()
args.out='test1'
args.vars=['Sex','Age assessment','BMI']#['Pulse rate']#
args.visit=0#'all'
args.aver_visits=False
args.remove_outliers=True#False#
args.filter=False#['Age assessment<70','Age assessment>=40','BMI>=25']#
args.html='/media/storage/UkBiobank/Application_10035/21204/ukb21204.html'
args.csv='/media/storage/UkBiobank/Application_10035/21204/ukb21204.csv'
args.cov_corr=False
args.excl=None
args.combine='outer'
###
###

if __name__ == '__main__':
    
    args = parser.parse_args()
    namehtml=args.html
    namecsv=args.csv
    nameexcl = args.excl


    ### import Biobankread package
    sys.path.append('BiobankRead-Bash')
    # Note some issues with case of directory names on different systems
    try:
        import biobankRead2.BiobankRead2 as UKBr2
        UKBr = UKBr2.BiobankRead(html_file = namehtml, csv_file = namecsv, csv_exclude = nameexcl)
        print("BBr loaded successfully")
    except:
        try:
            import BiobankRead2.BiobankRead2 as UKBr2
            UKBr = UKBr2.BiobankRead(html_file = namehtml, csv_file = namecsv, csv_exclude = nameexcl)
            print("BBr loaded successfully")
        except:
            raise ImportError('UKBr could not be loaded properly')
    Df=extract_the_things(UKBr, args)
    Df=float_to_cat(UKBr, Df)
    
    if Df.shape[0] == 0:
        print("ERROR - result data-frame has zero rows")
        print("No ouput - please check variable selection and conditions")
    else:
        final_name = args.out+'.csv'
        print("Outputting to", final_name)
        Df.to_csv(final_name,sep=',',index=None)
    #    except Exception as e:
    #        logging.error(e,exc_info=True)
    #        logging.info('Script did not work')
        if args.cov_corr:
            import seaborn as sns
            print('produce covariance/corr of variables in nice plots')
            produce_plots(Df,args)
