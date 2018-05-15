# -*- coding: utf-8 -*-
"""
Created on Tue May  8 17:53:41 2018

"""

import argparse
import pandas as pd
import numpy as np
import warnings
import re

'''Example run:
    python HES_extract.py \
'''

parser = argparse.ArgumentParser(description="\n BiobankRead HES_extract. Extracts data from HES records as made available within UKB")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --csv and --html option are required")
in_opts.add_argument("--tsv", metavar="{File1}", type=str,required=True, help='Specify the tsv HES data file.')
in_opts.add_argument("--codeType", type=str,required=True, help='ICD10, ICD9 or OPCS')
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=True, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=True, help='Specify the html file associated with the UKB application.')

out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')
out_opts.add_argument("--codes", nargs='+', type=str, help='Specify disease codes to extract', required=True)

options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--dateType",default='epistart',type=str,help="epistart or admidate")
options.add_argument("--firstvisit",default=True,type=bool,help="Only keep earliest visit for each subjects")
options.add_argument("--baseline",default=True,type=bool,nargs='+',help="Keep visits before or after baseline assessment only")




###################
def getcodes(args):
    if UKBr.is_doc(args.codes):
        Codes=UKBr.read_basic_doc(args.codes)
    else:
        Codes = args.codes
    return Codes

def extract_disease_codes(Df,args):
    HFs=getcodes(args)
    ## get all associated codes ##
    Codes = UKBr.find_ICD10_codes(select=HFs)
    df = UKBr.HES_code_match(df=Df, icds=Codes, which=args.codeType)
    df_new = count_codes(df,args)
    if args.firstvisit:
        print('Marking 1st ever and latest visits')
        date = args.dateType
        df_1st = UKBr.HES_first_last_time(df,date)
        df_new = pd.merge(df_new,df_1st,on=['eid'],how='outer')
    if args.baseline:
        print('Marking visits before & after baseline assessment')
        df_ass=UKBr.Get_ass_dates()
        df_ass=df_ass[df_ass.columns[0:2]]
        df_ass.rename(columns={df_ass.columns[1]: 'assess_date'},inplace=True)
        df2=UKBr.HES_after_assess(df=df,assess_dates=df_ass,date=date)
        df_sub=UKBr.HES_first_last_time(df,date)
        df_sub=pd.merge(df_sub,df_ass,on='eid')
        df3=UKBr.HES_before_assess(df_sub)
        df_new =pd.merge(df_new,df2,on=['eid'],how='outer')
        df_new = pd.merge(df_new,df3,on=['eid'],how='outer')
    return df_new

def count_codes(df,args):
    code_conv = re.match('ICD(\d+)',args.codeType).group(1)
    tmp1=list(set(df['diag_icd'+code_conv].tolist()))
    ids = list(set(df['eid'].tolist()))
    cols = ['eid']+tmp1
    df_new=pd.DataFrame(columns=cols)
    j=0
    for i in ids:
        df_sub=df[df['eid']==i]
        tmp2=list(set(df_sub['diag_icd'+code_conv].tolist()))
        res = [x in tmp2 for x in tmp1]
        res = [1*(x>0) for x in res]
        res = [i]+res
        df_new.loc[j]=res
        j += 1
    return df_new

###################
class Object(object):
   pass
args = Object()
args.out='test1'
args.html=r'D:\UkBiobank\Application 10035\\21204\ukb21204.html'
args.csv=r'D:\UkBiobank\Application 10035\\21204\ukb21204.csv'
args.tsv=r'D:\UkBiobank\Application 10035\HES\ukb.tsv'
args.codes=['I110','I132','I500','I501','I509']
args.codeType='ICD10'
args.dateType='epistart'
args.firstvisit=True
args.baseline=True
###################

if __name__ == '__main__':
    args = parser.parse_args()
    namehtml=args.html
    namecsv=args.csv
    nametsv=args.tsv
    ### import Biobankread package
   # sys.path.append('D:\new place\Postdoc\python\BiobankRead-Bash')
    try:
        import biobankRead2.BiobankRead2 as UKBr
        UKBr = UKBr.BiobankRead(html_file = namehtml, csv_file = namecsv)
        print("BBr loaded successfully")
    except:
        raise ImportError('UKBr could not be loaded properly')
    HES_records=UKBr.HES_tsv_read(filename=nametsv)
    HES_df = extract_disease_codes(HES_records,args)
