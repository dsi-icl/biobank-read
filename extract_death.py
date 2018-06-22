# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 18:29:00 2018

@author: Deborah
"""

import argparse
import pandas as pd
import numpy as np
import re

'''Example run:
    python extract_death.py \
        --csv <csv file> \
        --html <html file> \
        --out <results folder> \
        --codes ['C34'] \ ## death by lung cancer. Default is 'All', returns all deaths by any cause in UKB
        --primary True \ ## parse primary cause of death
        --secondary False \ ## parse contributing causes to death
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
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=True, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=True, help='Specify the html file associated with the UKB application.')

out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')
out_opts.add_argument("--codes", metavar="{File3}", nargs='+', type=str, default='All', help='Specify cause of death codes to extract')

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
args.codes='All'#['C34']
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
    # Loop over eids
    for i in ids:
        # Select this eid
        df_sub=df[df['eid']==i]
        # tmp2 = data columns for this eid
        tmp2=list(df_sub.iloc[0][1:len(df_sub.columns)-1])
        # Get columns with matching codes as Boolean vector
        # Note - C34 also matches C340 C341 etc
        # Is this intended?
        res = [x in tmp2 for x in tmp1]
        res = [int(x) for x in res]
        res = [i]+res
        df_new.loc[j]=res
        j += 1
    return df_new

def merge_primary(df):
    cols = df.columns.tolist()[1::]
    primary = [x for x in cols if '(primary)' in x]
    ids = list(set(df['eid'].tolist()))
    res=[]
    for i in ids:
        df_sub=df[df['eid']==i]
        res.append(df_sub[primary].values.any())
    df['primary cause of death']=res
    df.drop(primary, axis=1, inplace=True)
    return df

def rename_cols_death(df):
    cols = df.columns.tolist()[1::]
    secondary = [x for x in cols if '(secondary)' in x]
    for c in secondary:
        [a,b]=c.split('-')
        x = 'secondary cause of death-'+b
        df.rename(columns={c: x},inplace=True)
    return df

def extractdeath(args):
    All_vars = UKBr.Vars
    if args.secondary and args.primary:
        SR = [x for x in All_vars if 'of death: ICD10' in str(x)]
        dead_df = UKBr.extract_many_vars(SR,baseline_only=False, dropNaN=True)
    else:
        string = 'Underlying (primary) cause'*args.primary + 'Contributory (secondary) causes'*args.secondary
        SR = [x for x in All_vars if string+' of death: ICD10' in str(x)]
        dead_df = UKBr.extract_variable(SR[0],baseline_only=False, dropNaN=True)
    dead_df.dropna(axis=0,how='all',subset=dead_df.columns[1::],inplace=True)
    if args.codes[0] != 'All':
        dead_df = count_codes(dead_df,args)
        dead_df['all_cause'] = dead_df[dead_df.columns[1::]].sum(axis=1)
        dead_df=dead_df[dead_df.all_cause !=0]
    else:
        dead_df=merge_primary(dead_df)
        dead_df=rename_cols_death(dead_df)
    return dead_df

def dates_died(df):
    dates=['Date of death','Age at death']
    dates_df = UKBr.extract_many_vars(dates,baseline_only=False, dropNaN=True)
    dates = [x for x in dates_df.columns.tolist()[1::] if 'Date' in x]
    ages = [x for x in dates_df.columns.tolist()[1::] if 'Age' in x]
    dates_df.dropna(axis=0,how='all',subset=dates_df.columns[1::],inplace=True)
    dates_df['death_date']=dates_df[dates].replace(np.nan,UKBr.end_follow_up).min(axis=1)
    #dates_df['death_date']=dates_df[dates].replace(np.nan,2199).min(axis=1)
    dates_df['death_age']=dates_df[ages].replace(np.nan,150).min(axis=1)
    # This fixes the type but doesn't fix the problem!
    df[['eid']] = df[['eid']].astype(np.int64)
    df2=pd.merge(dates_df[['eid','death_date','death_age']],df,on='eid',how='inner')
    return df2

if __name__ == '__main__':
    args = parser.parse_args()
    namehtml=args.html
    namecsv=args.csv
    ### import Biobankread package
    # sys.path.append('D:\new place\Postdoc\python\BiobankRead-Bash')
    # Note some issues with case of directory names on different systems
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
    Df = extractdeath(args)
    Df = dates_died(Df)
    final_name = args.out+'.csv'
    Df.to_csv(final_name,sep=',',index=None)