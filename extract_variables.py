# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 16:12:24 2018

@author: Deborah
"""

import argparse
import __builtin__
import pandas as pd
import numpy as np
import logging

parser = argparse.ArgumentParser(description="\n BiobankRead Extract_Variable. Does what it says hehe")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --csv and --html option are required")
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=False, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=False, help='Specify the html file associated with the UKB application.')


out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')


options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--baseline_only",default=False,type=bool,help="Only keep data from baseline assessment centre")
options.add_argument("--remove_missing",default=False,type=bool,help="Remove subjects with values -3 or -7 for any variable")
options.add_argument("--remove_outliers",default=None,type=str,action='store',help="Remove subjects with values beyond x std dev for any cont. variable")

sums = parser.add_argument_group(title="Optional request for basic summary", description="Perform mean /cov/ corr/ dist plots for the data")
sums.add_argument("--aver_visits",default=False,type=bool,help="get average measurement per visit")
sums.add_argument("--cov_corr",default=False,type=bool,help="Produce extra file of cov/corr between variables. Will have same location and similar name to main output file")


def extract_the_things(args):
        print(args.out)
        print(args.csv)
        print(args.html)
        if args.baseline_only:
            print('baseline visit data only')
        if args.remove_missing:
            print('remove all values marked as "-3" and "-7"')
        if args.cov.corr:
            print('produce covariance/corr of variables')

if __name__ == '__main__':
    args = parser.parse_args()
    __builtin__.namehtml=args.html
    __builtin__.namecsv=args.csv
    ### import Biobankread package
    import BiobankRead2.BiobankRead2 as UKBr
    UKBr = UKBr.BiobankRead()
    try:
        extract_the_things(args)
    except Exception as e:
        logging.error(e,exc_info=True)
        logging.info('Script did not work')