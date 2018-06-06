# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 18:29:00 2018

@author: Deborah
"""

import argparse
import pandas as pd
import numpy as np
import warnings
import re

'''Example run:
    python extract_SR.py \
'''

parser = argparse.ArgumentParser(description="\n BiobankRead HES_extract. Extracts data from HES records as made available within UKB")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --csv and --html option are required")
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=True, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=True, help='Specify the html file associated with the UKB application.')

out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')
out_opts.add_argument("--codes", nargs='+', type=str, default='All', help='Specify cause of death codes to extract')

options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--primary", type=str2bool, nargs='?', const=True, default=True,  help="Primary cause of death")
options.add_argument("--secondary", type=str2bool, nargs='?', const=True, default=False,  help="Secondary cause of death")
############################################################################################################


class Object(object):
   pass
args = Object()
args.out='D:\MSc projects\\2018\\Confounders\death_lungCancer'
args.html=r'D:\UkBiobank\Application 10035\\21204\ukb21204.html'
args.csv=r'D:\UkBiobank\Application 10035\\21204\ukb21204.csv'
args.codes=['C34']
args.primary=True
args.secondary=True
###################

def getcodes(args):
    if UKBr.is_doc(args.codes):
        Codes=UKBr.read_basic_doc(args.codes)
    else:
        Codes = args.codes
    Codes = UKBr.find_ICD10_codes(select=Codes)
    return Codes

def count_codes(df,args):
    tmp1=getcodes(args)
    ids = list(set(df['eid'].tolist()))
    cols = ['eid']+tmp1
    df_new=pd.DataFrame(columns=cols)
    j=0
    for i in ids:
        df_sub=df[df['eid']==i]
        tmp2=list(df_sub.iloc[0][1:len(df_sub.columns)-1])
        res = [x in tmp2 for x in tmp1]
        res = [1*(x>0) for x in res]
        res = [i]+res
        df_new.loc[j]=res
        j += 1
    return df_new

def extractdeath(args):
    All_vars = UKBr.Vars
    if args.secondary and args.primary:
        SR = [x for x in All_vars if 'of death: ICD10' in str(x)]
        dead_df = UKBr.extract_many_vars(SR,baseline_only=False)
    else:
        string = 'Underlying (primary) cause'*args.primary + 'Contributory (secondary) causes'*args.secondary
        SR = [x for x in All_vars if string+' of death: ICD10' in str(x)]
        dead_df = UKBr.extract_variable(SR[0],baseline_only=False)
    dead_df.dropna(axis=0,how='all',subset=dead_df.columns[1::],inplace=True)
    df = count_codes(dead_df,args)
    df['all_cause'] = df[df.columns[1::]].sum(axis=1)
    df=df[df.all_cause !=0]
    return df

def dates_died(df):
    dates='Date of death'
    dates_df = UKBr.extract_variable(dates,baseline_only=False)
    dates_df=UKBr.rename_columns(df=dates_df,key='death_date')
    dates_df.dropna(axis=0,how='all',subset=dates_df.columns[1::],inplace=True)
    dates_df['death_date']=dates_df[dates_df.columns[1::]].replace(np.nan,UKBr.end_follow_up).min(axis=1)
    df2=pd.merge(dates_df[['eid','death_date']],df,on='eid',how='inner')
    return df2

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
        raise ImportError('UKBr could not be loaded properly')
    Df = extractdeath(args)
    Df = dates_died(Df)
    final_name = args.out+'.csv'
    Df.to_csv(final_name,sep=',',index=None)