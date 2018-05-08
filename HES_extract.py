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


out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')
out_opts.add_argument("--codes", nargs='+', type=str, help='Specify disease codes to extract', required=True)