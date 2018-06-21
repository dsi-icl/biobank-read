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

'''Example run:
    python extract_variables.py \
        --csv x/y/z.csv \
        --html x/y/z.html \
        --vars <list of variables>, as is or in .txt file \
        --out <directory name> x1\y1 \
(optionally)
        --baseline_only True\False (default=True)\
        --remove_missing True\False \
        --filter <list of conditions on variables in vars>, as is or in .txt file \
        --aver_visits True\False \
        --cov_corr True\False \
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
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=True, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=True, help='Specify the html file associated with the UKB application.')


out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--vars", metavar="{File3}", type=str, help='Specify variables to extract', required=True)
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')


options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--baseline_only", type=str2bool, nargs='?', const=True, default=True,  help="Only keep data from baseline assessment centre")
options.add_argument("--remove_missing", default=False, nargs='+', type=str,help="Remove subjects with values nan, -3 or -7 for any variable. Can specify which variables to perform that for")
options.add_argument("--remove_outliers", type=str2bool, default=False, nargs='+',action='store',help="Remove subjects with values beyond x std dev for any cont. variable. Format:[std.dev,one-sided,vars names...]")
options.add_argument("--filter", default=False, nargs='+', metavar="{File4}",type=str,action='store',help="Filter some variables based on conditions. Keep your requests simple ")

sums = parser.add_argument_group(title="Optional request for basic summary", description="Perform mean /cov/ corr/ dist plots for the data")
sums.add_argument("--aver_visits",default=False,type=str2boolorlist,help="get average measurement per visit")
sums.add_argument("--cov_corr",default=False,type=str2bool,help="Produce extra file of cov/corr between variables. Will have same location and similar name to main output file")

########################################################


def whitespace_search(smth,lst):
    smth = re.findall(r"[\w']+", smth)
    res = [c for c in lst if all(v in c for v in smth)]
    return res


def actual_vars(smth):
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
            print(res)
	else:
            res = [x for x in All if V in x]
            print(res) 
	for i in res:
            actual_vars_list.append(i)
        if len(actual_vars_list)==0: 
            ValueError('Variables names wrong. Go back to app documents and double-check what you actually have')
            return None
    actual_vars_list=list(set(actual_vars_list))
    return actual_vars_list
   
def bad_chars(df):
    ''' Remove bad chars from Df column names '''
    for c in df.columns.tolist()[1::]:
        res =list(set(c) & set(UKBr.special_char))
        if len(res)>0:
            C=c
            for u in res:
                C=C.replace(u,"")
            df.rename(columns={c: C},inplace=True)
    return df

def remove(Df,args):
    if args.remove_missing:
        Df.replace(to_replace=-7,value=np.nan,inplace=True)
        Df.replace(to_replace=-3,value=np.nan,inplace=True)
        Df.dropna(inplace=True)
    else:
        vars_missing = actual_vars(args.remove_missing).tolist()
        Df.replace(to_replace=-7,value=np.nan,subset=vars_missing,inplace=True)
        Df.replace(to_replace=-3,value=np.nan,subset=vars_missing,inplace=True)
        Df.dropna(subset=args.remove_missing,inplace=True)
    return Df

def average_visits(Df,args):
    if type(args.aver_visits) == list:
        var_names = actual_vars(args.aver_visits)
    else:
        var_names = actual_vars(args.vars)
        
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
        df_sub = bad_chars(Df[cols])
        Df_tmnp=UKBr.Mean_per_visit(df=df_sub)
    Df = pd.merge(Df,Df_tmnp,on='eid')
    return Df

def outliers(Df,args):
    ''' Remove outliers from cont variables'''
    if type(args.remove_outliers) == list:
        var_names = actual_vars(args.remove_outliers[2::])
        std = args.remove_outliers[0]
        onesided = args.remove_outliers[1]
    else:
        var_names = actual_vars(args.vars)
        std=4
        onesided=False
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
    Df2=pd.DataFrame(data=Df['eid'])
    for Y in stuff:
        cols = [x for x in Df.columns.tolist() if Y in x]
        cols = ['eid']+cols ### this first
        Df2=UKBr.remove_outliers(df=Df,cols=cols,lim=std,one_sided=onesided) 
    return Df2

def filter_vars(df,args):
    df_sub=pd.DataFrame(columns={'Vars','conds'})
    for cond in  args.filter:
        match=re.search('([a-zA-Z0-9\s]+)(\S{1,2}\d+)',cond)
        thevar=match.group(1)
        condition=match.group(2)
        df_sub=df_sub.append({'Vars':thevar,'conds':condition},ignore_index=True)
    # sanity check #
    overlap=list(set(df_sub['Vars'])&set(args.vars))
    if len(overlap)==0:
        raise NameError('Conditional filtering does not match extracted variables')
    #
    df_sub=df_sub[[x in overlap for x in df_sub['Vars']]]
    for i in range(len(df_sub)):
        Ys = [x for x in df.columns.tolist() if df_sub['Vars'].loc[i] in x]
        if len(Ys)==0:
            Ys = whitespace_search(df_sub['Vars'].loc[i],df.columns.tolist())
        for y in Ys:
            df = df[eval('df["'+str(y)+'"]'+df_sub["conds"].loc[i])]
    return df

def extract_the_things(args):
        if UKBr.is_doc(args.vars):
            print('doc detected')
            args.vars=UKBr.read_basic_doc(args.vars)
            print(args.vars)
	if args.baseline_only:
            print('Baseline visit data only')
        stuff=actual_vars(args.vars)
	print(stuff)
        Df = UKBr.extract_many_vars(stuff,baseline_only=args.baseline_only)
        if args.remove_missing:
            print('Remove all values marked as "nan", "-3" and "-7"')
            Df = remove(Df,args)
        if args.remove_outliers:
            print('Remove outliers for cont variables')
            Df = outliers(Df,args)
        if args.aver_visits:
            print('Compute visit mean for cont variables')
            Df = average_visits(Df,args)
        if args.filter:
            print('Filter variables based on condition')
            if UKBr.is_doc(args.filter):
                args.filter=UKBr.read_basic_doc(args.filter)
            Df = filter_vars(Df,args)
        return Df


def float_to_cat(df):
    var = df.columns.tolist()[1::]
    var = [x.split('_')[0] for x in var]
    types=lambda t: UKBr.variable_type(t)
    Types=[types(x) for x in var]
    cats = [Types.loc[x] for x in Types if 'Categorical' in x]
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

###### for testing on desktop ONLY!! #####
#class Object(object):
#    pass
#args = Object()
#args.out='test1'
#args.vars=['Sex','Age assessment','BMI']#['Pulse rate']#
#args.baseline_only=False
#args.remove_missing=True
#args.aver_visits=False
#args.remove_outliers=True
#args.filter=['Age assessment<70','Age assessment>=40','BMI>=25']#False#
#args.html='D:\UkBiobank\Application 10035\\21204\ukb21204.html'
#args.csv='D:\UkBiobank\Application 10035\\21204\ukb21204.csv'
#args.cov_corr=False
#####
import sys
if __name__ == '__main__':
    args = parser.parse_args()
    
    namehtml=args.html
    namecsv=args.csv
    ### import Biobankread package
    # sys.path.append('D:\new place\Postdoc\python\BiobankRead-Bash')
    try:
        import biobankRead2.BiobankRead2 as UKBr
        UKBr = UKBr.BiobankRead(html_file = namehtml, csv_file = namecsv)
        print("BBr loaded successfully")
    except:
        try:
            import BiobankRead2.BiobankRead2 as UKBr
            UKBr = UKBr.BiobankRead(html_file = namehtml, csv_file = namecsv)
            print("BBr loaded successfully")
        except:
            raise ImportError('UKBr could not be loaded properly')
    Df=extract_the_things(args)
    Df=float_to_cat(Df)
    final_name = args.out+'.csv'
    Df.to_csv(final_name,sep=',',index=None)
#    except Exception as e:
#        logging.error(e,exc_info=True)
#        logging.info('Script did not work')
    if args.cov_corr:
        import seaborn as sns
        import matplotlib.pyplot as plt
        print('produce covariance/corr of variables in nice plots')
        produce_plots(Df,args)
