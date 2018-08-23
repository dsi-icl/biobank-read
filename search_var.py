# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 09:55:52 2018

@author: wcrum
"""

import argparse
import pandas as pd
import numpy as np
import warnings
import re
import bs4

'''Example run:
    python search_var.py \
        --html x/y/z.html \
'''

parser = argparse.ArgumentParser(description="\n BiobankRead-Bash search_var. ")

in_opts = parser.add_argument_group(title='Input Files', description="Input files. The --html option is required")
in_opts.add_argument("--html", metavar="{File2}", type=str,required=True, help='Specify the html file associated with the UKB application.')
in_opts.add_argument("--match", type = str, default='or',help="and / or", nargs='+')
in_opts.add_argument("--keywords",default=[],help="one or more search terms", nargs='+')


def get_all_variables(soup):
    """Read all variable names in the table and return"""
    allrows = soup.findAll('tr')
    res = []
    data_type = []
    re_string = 'nowrap;\">(.*?)</span></td><td rowspan=\"(\d+)\">(.*?)</td></tr>'
    for t in allrows:
        #'</span></td><td rowspan=(.*?)>(.*?)</td></tr>'
        res1=re.search(re_string,str(t))
        if res1 is not None:
            res1 = res1.group(0)
            ## get variable data type xx1 between "nowrap;\" and "</span>"
            x1,y1,z1=res1.partition('nowrap;\">')            
            xx1,yy1,zz1=z1.partition('</span>')
            data_type.append(xx1)
            ## get variable name xx between '>' and '</td></tr>'
            x,y,z = zz1.partition('">')
            xx,yy,zz = z.partition('</td></tr>')
            ## check for trailing '<br>'
            t = xx.find('<br>')
            if t > -1:
                xx = xx[0:t]
            ## check for trailing '<br/>'
            ## NOTE - COULD PROBABLY COMBINE INTO A SINGLE TEST FOR '<br>' OR <br/>'
            ## BUT THE ORIGINAL LOGIC ALLOWED FOR '<br><br/>' SO I'M LEAVING IT
            t = xx.find('<br/>')
            if t >-1:
                xx = xx[0:t]
            res.append(xx)
    return {'names':res, 'types':data_type, 'allrows':allrows}

def get_all_related_vars(Vars, keyword=None, match='or'):
    '''
    Searches the variable list for variables which contain one or more supplied keywords.
    Returns the matching variables in a list.
    Note: case-insensitive
    
    Use for browsing the variable list wethout extracting data.
    -Bill Crum
    '''
    keywordlist = keyword
    if isinstance(keyword, str):
        keywordlist = [keyword]
    nkeywords = len(keywordlist)        
        
    varlist = []
    if match == 'or':
        for keyword in keywordlist:
            keyword = keyword.lower()
            stuff = [t for t in Vars if keyword in t.lower()]
            if len(stuff) > 0:
                varlist = varlist+stuff
    elif match == 'and':
        varlist = [t for t in Vars if len([k for k in keywordlist if k in t.lower()]) == nkeywords]
            
    return varlist

# MAIN
if __name__ == '__main__':
    
    # Get command-line arguments
    args = parser.parse_args()
    namehtml=args.html
    searchlist = args.keywords
    match = args.match
    
    
    
    print('Searching for', searchlist);
    print('Matching criterion is"', match, '"')

    # Get variable list    
    f = open(namehtml, 'r').read()
    soup = bs4.BeautifulSoup(f, 'html.parser')
    vardict = get_all_variables(soup)
    allvars = vardict['names']
    alltypes = vardict['types']
    
    # Perform the search
    thesevars = get_all_related_vars(allvars, searchlist, match)
    
    # Output the results
    for var in thesevars:
        ivar = allvars.index(var)
        vartype = alltypes[ivar]
        print(var, vartype)

