# -*- coding: utf-8 -*-
"""
Created on Tue May  8 17:53:41 2018

"""

import argparse
import pandas as pd
import re

'''Example run:
    python HES_extract.py 
    --csv  ukb21204.csv  
    --html ukb21204.html 
    --excl x/y/z.csv \
    --tsv ukb.tsv 
    --codes C49 
    --codeType ICD10 
    --baseline True 
    --dateType epistart 
    --out test
'''

parser = argparse.ArgumentParser(description="\n BiobankRead HES_extract. Extracts data from HES records as made available within UKB")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --csv and --html option are required")
in_opts.add_argument("--tsv", metavar="{File1}", type=str,required=True, help='Specify the tsv HES data file.')
in_opts.add_argument("--csv", metavar="{File1}", type=str,required=True, help='Specify the csv file associated with the UKB application.')
in_opts.add_argument("--html", metavar="{File2}", type=str,required=True, help='Specify the html file associated with the UKB application.')

out_opts = parser.add_argument_group(title="Output formatting", description="Set the output directory and common name of files.")
out_opts.add_argument("--out", metavar='PREFIX', type=str, help='Specify the name prefix to output files')
out_opts.add_argument("--codes",  metavar="{File3}",nargs='+',required=True, type=str, help='Specify disease codes to extract')
out_opts.add_argument("--codeType", type=str,required=True, help='ICD10, ICD9 or OPCS')

options = parser.add_argument_group(title="Optional input", description="Apply some level of selection on the data")
options.add_argument("--dateType",default='epistart',type=str,help="epistart or admidate")
options.add_argument("--firstvisit",default=True,type=bool,help="Mark earliest/latest visit for each subjects")
options.add_argument("--baseline",default=True,type=bool,nargs='+',help="Mark visits before and after baseline assessment ")
options.add_argument("--excl", metavar="{File5}", type=str, default=None, help='Specify the csv file of EIDs to be excluded.')

###################
def getcodes(UKBr, args):
    if UKBr.is_doc(args.codes[0]):
        Codes=UKBr.read_basic_doc(args.codes[0])
    else:
        Codes = args.codes
    return Codes

def extract_disease_codes(UKBr, Df, args):
    # Get the codes either directly from args.codes or from a file
    # Df = HES dataframe
    HFs=getcodes(UKBr, args)
    ## get all associated ICD10 codes ##
    if args.codeType == 'ICD10':
        Codes = UKBr.find_ICD10_codes(select=HFs)
    else:
        Codes = UKBr.find_ICD9_codes(select=HFs)
    # Get dataframe of those subjects which match any of the extracted codes
    df = UKBr.HES_code_match(df=Df, icds=Codes, which=args.codeType)
    df_new = count_codes(UKBr, df,args)
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
        # After
        df2=UKBr.HES_after_assess(df=df,assess_dates=df_ass,date=date)
        df_sub=UKBr.HES_first_last_time(df,date)
        df_sub=pd.merge(df_sub,df_ass,on='eid')
        # Before (just a binary flag)
        df3=UKBr.HES_before_assess(df_sub)
        df_new = pd.merge(df_new,df2,on=['eid'],how='outer')
        df_new = pd.merge(df_new,df3,on=['eid'],how='outer')
    return df_new

def count_codes(UKBr, df, args):
    """
    Args:
        df = data frame of UKBB subjects who matched an ICD10 HES code search.
        
    """
    # e.g. code_conv = 10
    code_conv = re.match('ICD(\d+)',args.codeType).group(1)
    code_str = 'diag_icd'+code_conv
    # e.g. tmp1 = ['C498', 'C499', 'C496', 'C494', 'C495', 'C492', 'C493', 'C490', 'C491']
    codes_list=list(set(df['diag_icd'+code_conv].tolist()))
    # All the patient ids
    ids = list(set(df['eid'].tolist()))
    # e.g. cols = ['eid', 'C498', 'C499', 'C496', 'C494', 'C495', 'C492', 'C493', 'C490', 'C491']
    cols = ['eid']+codes_list
    df_new=pd.DataFrame(columns=cols)
    j=0
    for i in ids:
        # Get the current id
        df_sub=df[df['eid']==i]
        # ICD10 codes belonging to this subject
        codes_this=list(set(df_sub[code_str].tolist()))
        # Codes which match the search list
        res = [i]+[int(x in codes_this) for x in codes_list]
        # Insert in data-frame
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
    nameexcl = args.excl
    nametsv=args.tsv
    
    ### import Biobankread package
    # sys.path.append('D:\new place\Postdoc\python\BiobankRead-Bash')
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
            
    # Read the HES data-file
    HES_records=UKBr.HES_tsv_read(filename=nametsv)
    
    # Find matching disease codes
    HES_df = extract_disease_codes(UKBr, HES_records,args)

    # Optional but nicer
    final_name = args.out+'.csv'
    print("Outputting to", final_name)
    HES_df.to_csv(final_name,sep=',',index=None)
    