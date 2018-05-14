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
options.add_argument("--firstvisit",default=False,type=bool,help="Only keep earliest visit for each subjects")
options.add_argument("--baseline",default=False,type=bool,nargs='+',help="Keep visits before or after baseline assessment only")




###################
def getcodes(args):
    if UKBr.is_doc(args.codes):
        Codes=UKBr.read_basic_doc(args.codes)
    else:
        Codes = args.codes
    return Codes

def extract_disease_codes(Df,args):
    HFs=getcodes(args)
    df = UKBr.HES_code_match(df=Df, icds=HFs, which=args.codeType)
    if args.fistvisit:
        print('Keeping 1st visits only')
        date = args.dateType
        df = UKBr.HES_first_time(df,date)
    if args.baseline:
        print('Keeping visits before or after baseline assessment only')
        df_sub=UKBr.HES_first_time(df)
        df_ass=UKBr.Get_ass_dates()
        if args.baseline in ['after','After']:
            df=UKBr.HES_after_assess(df=df_sub,assess_date=df_ass)
        else:
            df=UKBr.HES_before_assess(dates=df_sub)
    return df

###################
class Object(object):
   pass
args = Object()
args.out='test1'
args.html=r'D:\UkBiobank\Application 10035\\21204\ukb21204.html'
args.csv=r'D:\UkBiobank\Application 10035\\21204\ukb21204.csv'
args.tsv=r'D:\UkBiobank\Application 10035\HES\ukb.tsv'
args.codes=['I110','I132','I500','I501','I509']
args.dateType='epistart'
args.firstvisit=False
args.baseline=False
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
