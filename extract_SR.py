# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 17:47:20 2018

@author: Deborah
"""

import argparse
import pandas as pd

'''Example run:
    python extract_SR.py \
        --csv <csv file> \
        --html <html file> \
        --excl x/y/z.csv \
        --out <results folder> \
        --disease 'lung cancer' \ ## which self-reported diseases to extract
        --SRcancer True \ ## parse self-repoted cancer OR non-cancer diseases
        --baseline_only False \ ## Only keep data from baseline assessment centre
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

parser = argparse.ArgumentParser(description="\n BiobankRead HES_extract. Extracts data from HES records as made available within UKB")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --csv and --html option are required")
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=False, default=None, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=False, default=None, help='Specify the html file associated with the UKB application.')

out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')
out_opts.add_argument("--disease",  metavar="{File3}",nargs='+',required=True, type=str, help='Specify disease or code to extract')
out_opts.add_argument("--SRcancer", default=False, type=str2bool, help='Cancer or Non-cancer')

options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--baseline_only", type=str2bool, nargs='?', const=True, default=True,  help="Only keep data from baseline assessment centre")
options.add_argument("--excl", metavar="{File5}", type=str, default=None, help='Specify the csv file of EIDs to be excluded.')

def num_codes(UKBr, args):
    if UKBr.is_doc(args.disease):
        args.disease=UKBr.read_basic_doc(args.disease)
    if type(args.disease) is str:
        tmp=UKBr.find_SR_codes(select=args.disease,cancer=args.SRcancer)
    elif type(args.disease) is list:
        tmp = []
        for x in args.disease:
            if type(x) is str:
                Y = UKBr.find_SR_codes(select=x,cancer=args.SRcancer)
                tmp = tmp+Y
            else:
                Y = x
                tmp = tmp.append(Y)
    codes = [float(x) for x in tmp]
    return codes

def first_visit(df):
    cols_1st = [x for x in df.columns.tolist() if '0.' in x]
    return cols_1st

def extract_SR_stuff(UKBr, args):
    """
    Return a data-frame of Self-Reported cases
    
    Args:
        UKBr
        args
        
    Returns:
        SR_df: a dataframe containing self-reported cases
    """
    All_vars = UKBr.Vars
    if args.SRcancer:
        val = 'Cancer code, self-reported'
    else:
        val = 'Non-cancer illness code, self-reported'
    SR = [x for x in All_vars if val in str(x)]
    print(SR)
    if SR is None:
        raise ValueError('Variable '+val+' not present in application file')
    SR_df = UKBr.extract_variable(SR[0], baseline_only=args.baseline_only,dropNaN=True)
    print('Df extracted')
    SR_df.dropna(axis=0,how='all',subset=SR_df.columns[1::],inplace=True)
    print(len(SR_df))
    SR_df=count_codes(UKBr, SR_df,args)
    SR_df['all'] = SR_df[SR_df.columns[1::]].sum(axis=1)
    SR_df=SR_df[SR_df['all'] !=0]
    return SR_df

def count_codes(UKBr, df,args):
    tmp1=num_codes(UKBr, args)
    print(args.disease)
    print('codes found')
    print(tmp1)
    df_new=pd.DataFrame(columns=['eid']+tmp1)
    for c in df.columns[1::]:
        new_ymp=pd.DataFrame(columns=['eid'])
        for d in tmp1:
            ymp=df[df[c]==d]
            if(len(ymp)>0):
                ymp_sub=pd.DataFrame()
                ymp_sub['eid']=ymp['eid'].tolist()
                ymp_sub[d]=1
                new_ymp=pd.merge(new_ymp,ymp_sub,on='eid',how='outer')
            if(len(new_ymp)>0):
                df_new=pd.merge(df_new,new_ymp,on='eid',how='outer')
        #df_new=pd.concat([df_new,new_ymp],ignore_index=False,sort=True)
    for d in tmp1:
        cols = [c for c in df_new.columns if str(d) in str(c)]
        df_new[d]=df_new[cols].fillna(value=0).sum(axis=1)
        df_new[d]=[1*(V>0) for V in df_new[d]]
    df_new=df_new[['eid']+tmp1]
   #for i in ids:
   #     df_sub=df[df['eid']==i]
   #     tmp2=list(df_sub.iloc[0][1:len(df_sub.columns)-1])
   #     #tmp2=[x for x in tmp2 if str(x) != 'nan']
   #     res = [i]+[int(x in tmp2) for x in tmp1]
   #     df_new.loc[j]=res
   #     j += 1
    return df_new

#def clean_up(df):
#    df['SR_codes']=df[df.columns.tolist()[1::]].sum(axis=1)
#    everyone=UKBr.GetEIDs()
#    df2=pd.merge(everyone,df[['eid','SR_disease']],on='eid',how='outer')
#    df2.fillna(value=0,inplace=True)
#    return df2

###################
#class Object(object):
#   pass
#args = Object()
#args.out='/media/storage/codes/BiobankRead-Bash'
#args.html=r'/media/storage/UkBiobank/Application_236/R4528/ukb4528.html'
#args.csv=r'/media/storage/UkBiobank/Application_236/R4528/ukb4528.csv'
#args.disease='asbestosis'
#args.SRcancer=False
#args.baseline_only=False
###################


if __name__ == '__main__':
    args = parser.parse_args()
    namehtml=args.html
    namecsv=args.csv
    nameexcl = args.excl
    
    #print args
    #sys.exit()
     
    ### import Biobankread package
    # sys.path.append('D:\new place\Postdoc\python\BiobankRead-Bash')
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
    SR_df = extract_SR_stuff(UKBr, args)
    # Optional but nicer
    final_name = args.out+'.csv'
    print("Outputting to", final_name)
    SR_df.to_csv(final_name,sep=',',index=None)
