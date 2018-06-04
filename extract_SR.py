# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 17:47:20 2018

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
out_opts.add_argument("--codes", nargs='+',required=True, type=str, help='Specify disease codes to extract', required=True)
out_opts.add_argument("--SRCancer", default=False,type=str2bool, help='Cancer or Non-cancer')

options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--baseline_only", type=str2bool, nargs='?', const=True, default=True,  help="Only keep data from baseline assessment centre")

def num_codes(args):
    codes = [float(x) for x in args.codes]
    return codes

def extract_SR_stuff(args):
    All_vars = UKBr.Vars
    if args.SRCancer:
        SR = [x for x in All_vars if 'Cancer code, self-reported' in str(x)]
    else:
        SR = [x for x in All_vars if 'Non-cancer illness code, self-reported' in str(x)]
    SR_df = UKBr.extract_variable(SR[0],baseline_only=args.baseline_only)
    codes = num_codes(args)
    SR_df=SR_df[[x in codes for x in SR_df[SR_df.columns[1]]]]
    SR_df.dropna(axis=1,how='all',inplace=True)
    #SR_df = SR_df.fillna(value=0)
    return SR_df



###################
class Object(object):
   pass
args = Object()
args.out='D:\MSc projects\\2018\\Confounders\SR_lungCancer'
args.html=r'D:\UkBiobank\Application 10035\\21204\ukb21204.html'
args.csv=r'D:\UkBiobank\Application 10035\\21204\ukb21204.csv'
args.codes=['1004','1007','1009']
args.SRCancer=True
args.baseline_only=False
###################


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
    SR_df = extract_SR_stuff(args)
    final_name = args.out+'.csv'
    SR_df.to_csv(final_name,sep=',',index=None)