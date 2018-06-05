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
out_opts.add_argument("--codes", nargs='+', type=str, help='Specify cause of death codes to extract', required=True)

options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--primary", type=str2bool, nargs='?', const=True, default=True,  help="Primary cause of death")
options.add_argument("--secondary", type=str2bool, nargs='?', const=True, default=False,  help="Secondary cause of death")
############################################################################################################


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



def extractdeath(args):
    All_vars = UKBr.Vars
    if args.SRCancer:
        SR = [x for x in All_vars if 'Cancer code, self-reported' in str(x)]
    else:
        SR = [x for x in All_vars if 'Non-cancer illness code, self-reported' in str(x)]
    SR_df = UKBr.extract_variable(SR[0],baseline_only=args.baseline_only)
    codes=num_codes(args)
    return SR_df


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
