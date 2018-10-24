# -*- coding: utf-8 -*-
"""
Created Jan 27 2017
Edited 01/06/2017 

@author: Deborah Schneider-Luftman, ICL (UK),
@contact: ds711@ic.ac.uk

"""

import pandas as pd
import bs4 #beautifulsoup4 package
import re # RegEx 
import urllib3
import numpy as np
import os
import os.path
import sys
from datetime import datetime

## Required input: files location of the .csv and .html files
# .csv: ukb<release_code>.csv, the main data file produced after extraction from 
#       the .enc file
# .html: associated information file, generated alongside the.csv file with all
#       references to varaibles available 


class BiobankRead():
    """ A class to parse data from UK BioBank archives.
    
    usage:
    initialise
        bb = BiobankRead()

    class variables
        html_file = path to html
        soup = parsed tables from html
        Vars = all variables extracted in data frame
        Eids_all 
    
    class methods
        status()
        files_path([opt='html' or 'csv']) return path to file
        results = All_variables() read all variables in the table and return
                (used to set Vars as part of initialisation)
        
    """
    
    # needed to handle some funny variable names
    special_char = "~`!@#$%^&*()-+={}[]:>;',</?*-+" 
    
    defloc = os.path.join('Uk Biobank', 'Application ')
    
    # No longer required - URL extracted directly from data-set
    #sub_link  = 'http://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id='
    #code_link = 'http://biobank.ctsu.ox.ac.uk/crystal/coding.cgi?id='

    @staticmethod
    def clean_columns(df):
        '''
        Remove any "special_char"s in either dataframe columns or a string.
        
        Return original column name(s) and stripped versions 
        
        -Bill Crum.
        
        '''
        add_char = '. '
        if type(df) is str:
            dforig = df
            dfstrip = df.strip().lower()
            for ch in BiobankRead.special_char+add_char:
                dfstrip = dfstrip.replace(ch, '')
        else:
            dforig = df.columns
            dfstrip = df.columns.str.strip().str.lower()
            for ch in BiobankRead.special_char+add_char:
                dfstrip = dfstrip.str.replace(ch, '')
        return [dforig, dfstrip]        


    def  getfilenames(self, html_file=None,csv_file=None, csv_exclude=None, tsv_file=None):
        fpname = 'UKBBpaths.txt'
        filedict = {'html' : html_file, 'csv': csv_file, 'excl' : csv_exclude, 'tsv' : tsv_file}
        fpdir1 = os.getcwd() # current working directory
        fpdir2 = os.path.expanduser('~') # cross-platform home directory
        # Try each directory in turn until we find match
        foundsomething = False
        for fpdir in [fpdir1, fpdir2]:
            fpfile = os.path.join(fpdir, fpname)
            if os.path.isfile(fpfile):
                with open(fpfile) as f:
                    content = f.readlines() 
                    for line in content:
                        sline = str.split(line)
                        # Line format is:
                        # key  filepath
                        if len(sline) == 2:
                            (key, fp) = sline
                            if os.path.isfile(fp) and (key in filedict) and (filedict[key] == None):
                                filedict[key] = fp
                                print(' Found file', key, 'is', fp)
                                foundsomething = True
            if foundsomething:
                break
        
        return filedict
        
    def __init__(self, html_file = None, csv_file = None, csv_exclude = None):
        
        # Look for file containing file-paths
        # Search priority is:
        #       function arguments override everything else
        #       current directory
        #       home directory
        filedict = self.getfilenames(html_file=html_file, csv_file=csv_file, csv_exclude=csv_exclude)
                    
        # Construct the path to the html file
        self.html_file = filedict['html']
        self.csv_file  = filedict['csv']
        self.csv_exclude = filedict['excl']
        self.hes_file  = filedict['tsv']

        if (self.html_file == None) or (self.csv_file == None):
            print
            print(' CLASS NOT INITIALISED')
            print()
            print(' To initialise this class, please use')
            print(' bbclass(html_file = namehtml, csv_file = namecsv, [csv_exclude = excludecsv])')
            print()
            print(" namehtml='<file_location>.html'")
            print(" namecsv='<file_location>.csv'")
            print(" excludecsv='<file_location>.csv'")
            print(' where')
            print(' ukb<release_code>.csv = the main data file')
            print('                         produced from the .enc file')
            print(' something.html = information file, generated')
            print('                  alongside the.csv file')
            print(' exclusions.csv = CSV with single \'eid\' column of cases to exclude')
            print()
            print(' ALTERNATIVELY')
            print(' Create a file called UKBBpaths.txt in your home directory as follows')
            print(' csv  path/to/csv/file')
            print(' html path/to/html/file')
            print(' excl path/to/exclusion/file')
            print(' hes  path/to/hesfile')
            print(' NB csv and html paths are required in general')
            print()
            self.OK = False
            return

        if not os.path.isfile(self.html_file):
            print
            print(' INITIALISATION ERROR: html_file =', html_file, 'not found')
            print
            self.OK = False
            return 
            
        if not os.path.isfile(self.csv_file):
            print
            print(' INITIALISATION ERROR: csv_file =', csv_file, 'not found')
            print
            self.OK = False
            return None

        print(' OK, initialising class now ... ')

        #HES file processing variables
        this_dir, this_filename = os.path.split(__file__)
        self.DATA_PATH      = os.path.join(this_dir, "data", "coding19.tsv")
        self.DATA_PATH_2    = os.path.join(this_dir, "data", "ICD9_codes.csv") 
        self.DATA_PATH_SR   = os.path.join(this_dir, "data", "coding3.tsv") 
        self.DATA_PATH_SR_2 = os.path.join(this_dir, "data", "coding6.tsv") 
        
        # Parse html 
        print(' Making soup')
        self.soup = self.makeSoup()
        
        #Time/date variables
        self.date_format = "%Y-%m-%d"
        self.end_follow_up = "2026-02-15"
        self.start_follow_up = "2006-05-10"
        self.Time_end = datetime.strptime(self.end_follow_up, self.date_format)
        
        # Variables in table
        # Populate by calling self.All_variables()
        print(' Loading variables')
        allvars = self.All_variables()
        self.Vars = allvars['names']
        self.data_types = allvars['types']
        self.allrows = allvars['allrows']
                
        # All EIDS
        self.Eids_all = self.GetEIDs()

        # This appears clumsy but is because None can't be compared to a data frame
        # http://stackoverflow.com/questions/36217969/how-to-compare-pandas-dataframe-against-none-in-python
        self.OK = False
        self.N = -1
        if self.Eids_all is not None:
            self.OK = True
        if not self.OK:
            print('error - failed to get Eids')
            self.OK = False
            return
        self.N = len(self.Eids_all)
        print(' Found', self.N, 'EIDS')
        
        # Excluded EIDS
        self.Eids_exclude = None
        if csv_exclude != None:
            self.Eids_exclude = self.GetEIDs(csv_exclude)
            self.Nexcl = len(self.Eids_exclude)
            print(' Found', self.Nexcl, 'potential EIDS to exclude')
            
        # Apply exclusions to EID list
        if type(self.Eids_exclude) == pd.DataFrame:
            df = pd.merge(self.Eids_all, self.Eids_exclude, how='outer', indicator=True)
            self.Eids_all = df.loc[df['_merge'] == 'left_only']['eid']
            Nold = self.N
            self.N = len(self.Eids_all)
            print( ' ', Nold-self.N, 'matched exclusions were made')
            if Nold > self.N:
                print(' ', self.N, 'EIDS remain')

        print('Done');

        # All attendance dates
        # QUERY - WHERE IS N SET?
        #self.assess_dates = self.Get_ass_dates()
        
    def status(self):
        print('html:', self.html_file)
        print('Record number', self.N)
        return

    def makeSoup(self):
        """Parse the html into a nested data structure"""
        f = open(self.html_file, 'r').read()
        soup = bs4.BeautifulSoup(f, 'html.parser')
        return soup
        
    def is_doc(self,doc):
        """
        Return True if doc is of the form 'something.txt'
        doc is expected to be either a list of strings or a filename
        """
        #if type(doc) is list:
        if type(doc) is list:
            if len(doc)>1:
                return False        
            else:
                doc=doc[0]
        b=doc.find('.txt')
        return (b>-1)
    
    def read_basic_doc(self,doc):
        if type(doc) is list and len(doc)==1:
            doc = doc[0]
        try:
           with open(doc) as f:
                variable=f.read()
        except:
            raise IOError('Input file is not a .txt file')
        lst =[str(line) for line in open(doc).read().splitlines()]#.readlines()] 
        if lst is None:
            raise IOError('Input file formatted wrong, needs to be new-line-break separated')
        return lst
    
    #############################################################
    
    def All_variables(self):
        """Read all variable names in the table and return"""
        allrows = self.soup.findAll('tr')
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
        '''
        # This logic now incorporated in loop above
        # -Bill Crum
        res2 = []
        for x in res:
            t = x.find('<br/>')
            if t >-1:
                 res2.append(x[0:t])
            else:
                 res2.append(x)
        res = res2
        '''
        return {'names':res, 'types':data_type, 'allrows':allrows}
    
    def GetEIDs(self, filename=None):
        """Return all the EIDs"""
        # data frame of EIDs
        if filename is None: 
            filename = self.csv_file 
        if filename is None:
            return None
        EIDs = pd.read_csv(filename, usecols=['eid'])
        return EIDs
    
    def Get_ass_dates(self, dropNaN=False, baseline_only=False):
        '''
        Convenience function for assessment dates.
        '''
        # data frame of EIDs
        var = 'Date of attending assessment centre'
        Ds = self.extract_variable(var)
        #Ds = self.rename_columns(Ds, var, baseline_only=baseline_only)
        #Ds['eid']=[str(e) for e in Ds['eid']]
        return Ds   

    def extract_variable(self, variable=None, baseline_only=False, dropNaN=False):
        '''
        Extracts a single specified variable  (input)
        Returns data for first visit only if baseline_only == True
        dropNan=True only returns records without Nan entries
        This function updated by Bill Crum 13/02/2018
        '''
        
        # extract fields 
        allrows = self.allrows
        
        # Deal with special symbols in variable name
        symbols = BiobankRead.special_char
        varlist = list(variable)
        newvar = []
        for v in varlist:
            if v in symbols:
                newvar.extend(['\\', v])
            else:
                newvar.extend([v])
        variable = ''.join(newvar)
        
        # FIND VARIABLES IN MASTER LIST
        # Find variable embedded like this:
        # ... <td rowspan="1">Heel ultrasound method<br> ...
        # Or this:
        # ... <td rowspan="1">Heel ultrasound method.<br> ...
        searchvar = '>'+variable+'(.?)<'
        userrows = [t for t in allrows if re.search(searchvar, str(t))]
        if not userrows:
            raise Exception('The input variable is not in the files')
        if len(userrows) > 1:
            print('warning - more than one variable row found')
            print('warning - returning first instance only')
        userrows_str = str(userrows[0])

        # extract IDs related to variables
        # extract all variable names
        match1 = re.search('id=(\d+)',userrows_str)
        if match1:
            idx = match1.group(1)
        else:
            print('warning - index for', variable, 'not found')
            return None
            
        # FIND MATCHING COLUMNS FOR VARIABLES AND READ IN FROM FILE
        ## Retrieve all associated columns with variables names 
        # Encoded anonymised participant ID
        key = ['eid']
	  # explicit href search deprecated
        #for link in self.soup.find_all('a', href=BiobankRead.sub_link+idx):
        columns =  self.soup.find_all("a", href = re.compile("field.cgi\?id="+idx+"$"))
        for link in columns:
            tmp = str(link.contents[0])#.encode('utf-8'))
            key.append(tmp) 
        everything = pd.read_csv(self.csv_file, usecols=key, nrows=self.N)
        
        #na_filter=False)
        # drop columns of data not collected at baseline 
        if baseline_only:
            cols = everything.columns
            keep = ['0.' in x for x in cols]
            keep[0] = True # always keep eid column
            everything = everything[cols[keep]]
            
        if dropNaN:
            #tmp = ~everything.isnull().any(axis=1)
            #everything = everything[tmp]
            everything.dropna(axis=0,how='all',subset=everything.columns[1::],inplace=True)

        return everything
        
    def variable_type(self,var_names):
        """Returns the type of variable for any variable name"""
        allrows = self.soup.findAll('tr')
        # Deal with special symbols in variable name
        symbols = BiobankRead.special_char
        varlist = list(var_names)
        newvar = []
        for v in varlist:
            if v in symbols:
                newvar.extend(['\\', v])
            else:
                newvar.extend([v])
        variable = ''.join(newvar)
        searchvar = '>'+variable+'(.?)<'
        userrows = [t for t in allrows if re.search(searchvar,str(t))]
        userrows_str = str(userrows[0])
        match1 = re.search('<span style=\"white-space: nowrap;\">(.*?)</span></td>',userrows_str)
        if match1:
            idx = match1.group(1)
        else:
            print('warning - index for', variable, 'not found')
            return None
        return idx
        
        
    def illness_codes_categories(self, data_coding=6):
        """Returns data coding convention from online page"""
        
        ## Get dictionary of disease codes
        # Get generic coding link - new April 2018
        linkstr = self.soup.find_all("a", href = re.compile("coding.cgi\?id="+str(data_coding)+"$"))
        if len(linkstr) == 0:
            return None
        if not isinstance(linkstr, str):
            linkstr = linkstr[0]
            link = linkstr['href']
								            
        # explicit link search deprecated
        #link = BiobankRead.code_link+str(data_coding)

        http = urllib3.PoolManager()
        response = http.request('GET', link)
        #response = urllib2.urlopen(link)
        html = response.data
        soup = bs4.BeautifulSoup(html,'html.parser')
        allrows = soup.findAll('tr')
        
        ## find all categories of illnesses
        userrows = [t for t in allrows if t.findAll(text='Top')]
        userrows_str = [] # convert to string
        for j in userrows:
            userrows_str.append(str(j))
        Group_codes, Group_names = [], []
        for line in userrows_str:
                match1 = re.search('class="int">(\d+)',line)
                Group_codes.append(match1.group(1))
                b,k,a = line.partition('</td><td class="txt">No')
                bb,kk,aa = b.partition('"txt">')
                Group_names.append(aa)
        Groups = pd.Series(data=Group_codes,index=Group_names)
        return Groups
        

    def list_all_related_vars(self, keyword=None):
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
        varlist = []
        for keyword in keywordlist:
            keyword = keyword.lower()
            stuff = [t for t in self.Vars if keyword in t.lower()]
            if len(stuff) > 0:
                varlist = varlist+stuff
        return varlist

    def all_related_vars(self, keyword=None, dropNaN=True):
        '''
        Extracts all variables related to a keyword variable (input)
        Returns a df with eids for each variable in a dictionary
        This function updated by Bill Crum 13/02/2018
        '''
        
        if keyword is None:
            print(' (all_related_vars) supply keyword to search over')
            return None
            
        stuff = self.list_all_related_vars([keyword])
        stuff_var = {}
        if len(stuff) > 0:
            for var in stuff:
                DBP = self.extract_variable(variable=var)
                if dropNaN:
                    # drop subjects with no reported illness
                    DBP = DBP[DBP.drop('eid', axis=1).notnull().any(axis=1)]
                stuff_var[var] = DBP
        else:
            print('No match for', keyword, 'found')
        return stuff_var, stuff


    def extract_many_vars(self, varnames=None,
                          dropNaN=False,spaces=False,baseline_only=False, combine='outer'):
        '''
        Extract variables for several pre-specified variable names 
        Supply these as keywords=[var1, var2, ...]
        Returns one single df with eids and each variables as columns
        dropNaN = True/False = whether to ignore NaN entries
        spaces = drop variable name after first space when labelling columns
        
        combine='outer' will inclusively merge each variable into the master list
        combine='inner' will only retain cases where data exists for all variables
        combine='partial' retains cases where data exists in at least one variable        
        
        '''
        if varnames is None:
            print(' (extract_many_vars) supply [varnames] to search over')
            return None
            
        # Convert single argument to list
        # This because len(string) > 1
        if isinstance(varnames, str):
            varnames = [varnames]

        # Process combine option for how to merge variables
        combine0 = combine
        if combine == 'partial':
            combine0 = 'outer'

        main_Df = pd.DataFrame()
        main_Df['eid'] = self.Eids_all['eid']
        for var in varnames:
            print(var)
            # Get variable
            DBP = self.extract_variable(variable=var, baseline_only=baseline_only, dropNaN=dropNaN)

            # Partition name for column naming
            if spaces:
                b,k,a = var.partition(' ')
                var = b
            DBP = self.rename_columns(DBP, var, baseline_only=baseline_only)
            
            # Get rid of NaNs
            if dropNaN:
                # drop subjects with no reported illness in any variable
                # Get a boolean series with True where all fields present
                # Search for any null field then negate with ~
                ##
                #DBP = DBP[DBP.drop('eid', axis=1).notnull().any(axis=1)]
                DBP.dropna(axis=0,how='all',subset=DBP.columns[1::],inplace=True)
                
            # Add variable to returned data-frame    
            main_Df = pd.merge(main_Df,DBP,on='eid',how=combine0)
            
        # if combine == 'partial', we require at least one entry to be valid for each eid
        # if combine == 'inner', all entries must be valid
        if combine == 'partial':
            main_Df = main_Df[main_Df.drop('eid', axis=1).notnull().any(axis=1)]
            
        return main_Df

    def df2csv(self, df=None, csvfile=None, force=False):
        '''
        Save a supplied data-frame as a csv file
        '''
        if df is None:
            print(' supply a data-frame')
            return
        if csvfile is None:
            print(' supply filename.csv')
            return
        if os.path.isfile(csvfile) and not force:
            print(' %s exists and won\'t be overwritten' % csvfile)
            print('use force=True to override')
            return
        df.to_csv(csvfile,index=None)
        

    def correlate_varlist(self, varlist, cortype='pearson', dropNaN=False):
        '''
        Pairwise correlation between selected variables.
        cortype = correlation type = one of ['pearson','kendall', 'spearman']
        dropNaN = True/False = whether to ignore NaN entries
        '''
        corrList = ['pearson','kendall', 'spearman']
        if cortype not in corrList:
            print('argument cortype must be one of:')
            print(corrList)
            return None
        df = self.extract_many_vars(varlist, dropNaN=dropNaN)
        # Exclude eid column from correlation
        df = df.drop(['eid'], axis=1)
        correlation = df.corr(method='pearson');
        return correlation, df
        
        
    def covariance_varlist(self, varlist, dropNaN=False):
        '''
        Pairwise covariance between selected variables.
        dropNaN = True/False = whether to ignore NaN entries
        '''
        df = self.extract_many_vars(varlist, dropNaN=dropNaN)
        # Exclude eid column from covariance
        df = df.drop(['eid'], axis=1)
        covariance = df.cov();
        return covariance, df
        
         

    def Mean_per_visit(self, df=None,dropNaN=False):
        '''
        Average of variables at each visit
        i.e. when multiple measurements per visit
        input = df with variables of interest
        dropNaN = True/False = whether to ignore NaN entries
        only relevant if multiple measurements available
        NOTE: Bill Crum changed '_' date delimiter to '-'
        NOTE (27/04): Deb S-L changed '-' to regex expression to extract '-' OR '_'
        '''
        
        # e.g.  Tmp = ['eid', '4080-0.0', '4080-0.1', '4080-1.0', '4080-1.1', '4080-2.0', '4080-2.1']
        Tmp = list(df.columns.tolist())
        # Get time-field root
        # e.g. tmp2 = ['4080']
        ### find separation type###
        match1 = re.search('.*?(.)\d.\d',Tmp[1]) # finds what's next to 0.0, 0.1, 1.0 et....
        ###
        mychar=match1.group(1)
        tmp2 = list(set([x.partition(mychar)[0] for x in Tmp]))
        tmp2 = [y for y in tmp2 if 'eid' not in y] # remove eid column
        # initiate output
        new_df = pd.DataFrame(columns=['eid'])
        new_df['eid']=df['eid']
        # for each variable in df
        for var in tmp2:
            # e.g. sub = ['4080-0.0', '4080-0.1', '4080-1.0', '4080-1.1', '4080-2.0', '4080-2.1']
            sub = [x for x in Tmp if var+mychar in x]
            # e.g. sub_rounds = ['0.0', '0.1', '1.0', '1.1', '2.0', '2.1']
            sub_rounds = [x.partition(mychar)[2] for x in sub]
            # e.g. ['0', '0', '1', '1', '2', '2']
            rounds = [x.partition('.')[0] for x in sub_rounds]
            df_sub = pd.DataFrame(columns=['eid'])
            df_sub['eid']=df['eid']
            # for each visit
            for t in range(int(max(rounds))+1):
                per_round = [x for x in sub if mychar+str(t) in x]
                if dropNaN:
                    df_sub[var+'_mean_'+str(t)] = df[per_round].mean(axis=1,skipna=False)
                else:
                    df_sub[var+'_mean_'+str(t)] = df[per_round].mean(axis=1)
            new_df = pd.merge(new_df,df_sub,on='eid')
        return new_df
    
    
    def confounders_gen(self, more_vars = [], baseline_only=False):
        # creates a dictionary of conventional confounding variables
        # more can be added through the 'more_vars' input 
        # output = dictionary with dfs, 1 df per variable
        # output dfs need to be further processed before analysis

        conf_names = ['Body mass index (BMI)','Age when attended assessment centre','Ethnic background','Sex']
        # Convert single argument to list
        # This because len(string) > 1
        if isinstance(more_vars, str):
            more_vars = [more_vars]
            
        # Add optional extras to confound list
        for items in more_vars:
            conf_names.append(items)
            
        # Create dictionary of variable values and names
        df_new = {}
        for var in conf_names:
            tmp = self.extract_variable(variable=var)
            tmp = self.rename_columns(df=tmp,key=var, baseline_only=baseline_only)
            df_new[var] = tmp
            
        return df_new,conf_names
        
    
    def rename_conf(self, df=None):
        # rename columns of confounders df with sensible stuff
        ###### 21-03-2018 : 
        #### keep this function? 
        names_in = df.columns.tolist()
        names_out = []
        for n in names_in:
            b,k,a = n.partition('_')
            res=re.search('\((.*?)\)',str(b)) # search for abbrev in brackets
            if not res is None:
                s = res.group(1)
            else: #fill spaces
                res = [m.start() for m in re.finditer(' ', b)]
                s = list(b)
                if len(res) > 0:
                    for tmp in res:
                        s[tmp] = '_'
                s = "".join(s)
            names_out.append(s)
        df.columns = names_out
        return df,names_out

    
#    def df_mean(self, df=None,key=None):
#        '''
#        df_mean(df=None,key=None):
#        returns mean of data values as a new data-frame
#        df = data frame containing variables
#        key = name of mean in new dataframe
#        
#        (I suspect this isn't used any more.)
#       21-03-18 : no that prob right
#        '''
#        if df is None:
#            print ' (df_mean) supply dataframe with variables of interest'
#            return None
#        if key is None:
#            print ' (df_mean) supply key as name of created mean'
#            return None
#        cols = df.columns.tolist()
#        new_df = pd.DataFrame(columns=['eid',key])
#        new_df['eid'] = df['eid']
#        new_df[key] = df[cols[1::]].mean(axis=1)
#        return new_df
    
    def vars_by_visits(self, col_names=None, visit=0):
        '''
        vars_by_visits(col_names=None, visit=0)
        returns variables in col_names associated with specified visit
        e.g. bbclass.vars_by_visits(col_names=['4080-0.0', '4080-0.1', '4080-2.0'], visit=0)
        returns ['4080-0.0', '4080-0.1']
        '''
        ###### 21-03-2018 : 
        #### what does this do again?
        ###### 11-04-2018
        #### used by other functions that feed into extract_variables()
        if col_names is None:
            print(' (vars_by_visits) supply variable names in col_names')
            return None
        # Convert single argument to list
        # This because len(string) > 1
        if isinstance(col_names, str):
            col_names = [col_names]
        V1 =[]
        for var in col_names:
            # \d match any decimal digit
            # . match any character
            # * match previous character 0 or more times
            # + matches one or more times
            # ? matches zero or one time
            # Matches things like 'something-X.Y or 'something-X_Y'
            # Where X == visit
            res = re.search('(.*?)-'+str(visit)+'.(\d+)', var)
            if not res is None:
                V1.append(res.group(0))
        return V1
    

    def rename_columns(self, df=None,key=None,option_str=True, baseline_only=False):
        # rename the columns of a data frame with something sensible
        col_names = df.columns.tolist()
        col_new = ['eid']
        nvisits = 1 if baseline_only else 3
        for k in range(nvisits):
            V0 = self.vars_by_visits(col_names,k)
            if len(V0) > 0:
                match1 = re.search('.*?(.)\d.\d',V0[0]) #
                mychar=match1.group(1)
                for v in V0:
                    b,k,a = v.partition(mychar)
                    if option_str:
                        col_new.append(key+'_'+a)
                    else:
                        col_new.append(key)
        df_new = pd.DataFrame(columns=col_new)
        for c in range(len(col_new)):
            df_new[col_new[c]] = df[col_names[c]]
        return df_new
        
    def find_DataCoding(self, variable=None):
        ### extract fields 
        soup = self.soup
        allrows = soup.findAll('tr')
        ## search variable string for shitty characters
        symbols = BiobankRead.special_char
        
        # DOES THIS WORK THE SAME AS THE NEXT SECTION?        
        varlist = list(variable)
        lvarlist = len(varlist)
        newvar = []
        for v in range(0, lvarlist):
            if varlist[v] in symbols:
                newvar.extend(['\\', varlist[v]])
            else:
                newvar.extend([varlist[v]])
        variable = ''.join(newvar)
        
        '''
        is_symbol = False
        where =[]
        for x in symbols:
            t = variable.find(x)
            if t >-1:
                is_symbol = True
                where.append(t)
        if is_symbol:
            new_var = ""
            for i in variable:
                lim = variable.index(i)            
                if lim in where:
                    i= "\%s" % (variable[lim])
                new_var += i
            variable = new_var
        '''
        
        ##
        userrows = [t for t in allrows if re.search('>'+variable+'<',str(t))]
        row_str = str(userrows[0])
        foo = row_str.find('Uses data-coding')
        if foo < 0:
            print('No data coding associated with this variable')
            return None
        test = re.search('coding <a href=\"(.?)*\">',row_str)
        res = test.group(0)
        x,y,z=res.partition('href="')
        link,y,u=z.partition('">')
        http = urllib3.PoolManager()
        response = http.request('GET', link)
        #response = urllib2.urlopen(link)
        html = response.data
        soup = bs4.BeautifulSoup(html,'html.parser')
        allrows = soup.findAll('tr')
        rows_again = [t for t in allrows if re.search('class=\"int\">(.?)*</td><td class=\"txt\">(.?)*</td>',str(t))]
        schema = pd.DataFrame(columns=['key','value'])
        u = 0
        for item in rows_again:
            item = str(item)
            x,y,z = item.partition('</td><td class="txt">')
            xx,xy,xz = x.partition('<td class="int">') # number key
            zx,zy,zz = z.partition('</td>') # value 
            schema.loc[u] = [xz,zx]
            u += 1
        return schema
        
    def re_wildcard(self, strs=None):
        # inserts a regex wildcard between two keywords
        if not type(strs) is list:
            print('Input not a list')
            return None
        n = len(strs)
        if n < 2:
            print('Not enough words to collate')
            return None
        res = strs[0]
        for word in strs[1::]:
            res = res+'(.?)*'+word
        return res
        
    def Datacoding_match(self, df=None,key=None,name=None):
        # find key din df with known data coding
        # find datacoding with find_DataCoding() before using this funct.
        if type(key) == str:
            key = int(key)
        cols = self.get_cols_names(df)
        # remove eids
        cols = cols[1::]
        new_df = pd.DataFrame(columns=cols)
        new_df['eid'] = df['eid']
        for col in cols:
            res_tmp1 = [x==key for x in df[col]]
            new_df[col]=res_tmp1
        new_df2 = pd.DataFrame(columns=['eid',name])
        new_df2[name] = new_df[cols].sum(axis=1)
        new_df2['eid'] = df['eid']
        return new_df2
        
    def remove_outliers(self, df=None,cols=None,lim=4,one_sided=False):
        # remove outliers from data frame, for each variable
        # cols= specify which variables
        # lim = how many std away
        # one_sided: trim both small/large values, or only large varlues
        if cols is None:
            cols = df.columns
            cols = cols[1::] # remove eids
        new_Df = df
        for var in cols:
            if not one_sided:
                new_Df=new_Df[((new_Df[var]-new_Df[var].mean())/new_Df[var].std()).abs()<lim]
            else:
                new_Df=new_Df[((new_Df[var]-new_Df[var].mean())/new_Df[var].std())<lim]
        return new_Df
    
    def find_SR_codes(self,select=None,cancer=True):
        if cancer:
            tmp = self.HES_tsv_read(self.DATA_PATH_SR)
        else:
            tmp = self.HES_tsv_read(self.DATA_PATH_SR_2)
        descr = tmp['meaning'].tolist()
        find =[x for x in descr if select in x]
        SR_cancer = []
        for d in find:
            ## get 1st order codes
            c = tmp[tmp.meaning==d]['coding']
            SR_cancer.append(c.iloc[0])
            ## get higher order codes
            node_id = tmp[tmp.meaning==d]['node_id'].iloc[0]
            sub = tmp[tmp.parent_id==node_id]
            Nsub = len(sub)
            while Nsub > 0:
                codes_sub = sub['coding'].tolist()
                SR_cancer = SR_cancer +codes_sub
                ## 
                node_id = sub['node_id'].tolist()
                sub = tmp[[x in node_id for x in tmp.parent_id]]
                Nsub = len(sub)
        SR_cancer = list(set(SR_cancer))
        return SR_cancer
###################################################################################
################## HES data extraction + manipulation ##############################
###################################################################################
     
    def HES_tsv_read(self,filename=None,var='All',n=None):
        ## opens HES file, usually in the form of a .tsv file
        ## outputs a pandas dataframe
        everything_HES = pd.read_csv(filename,delimiter='\t',nrows=n)
        #everything_HES=everything_HES.set_index('eid')
        if var == 'All':    
            return everything_HES
        else:
           sub_HES = everything_HES[var]
           return sub_HES

    def find_ICD10_codes(self,select=None):
        # extract ICD10 codes from a large, complete dictionary of ICD10 codes
        #          of all diseases known to medicine
        #
        # https://en.wikipedia.org/wiki/ICD-10
        #
        # input: select - general code for one class of deseases
        # output: icd10 - codes of all deseases associated with class
        #
        # e.g. select = 'C49' (Malignant neoplasm of other connective and soft tissue)
        # returns ['C49', 'C490', 'C491', 'C492', 'C493', 'C494', 'C495', 'C496', 'C498', 'C499']
        # which constitute the original disease class and all the subclasses
        tmp = self.HES_tsv_read(self.DATA_PATH)
        codes_all = tmp['coding'].tolist()
        icd10 = []
        if type(select) is str:
            select = [select]
        for categ in select:
            tmp = [x for x in codes_all if categ in x]
            for y in tmp:
                icd10.append(y)
        icd10 = [x for x in icd10 if 'Block' not in x]
        icd10 = [x for x in icd10 if 'Chapter' not in x]
        return icd10
        
    def find_ICD9_codes(self,select=None):
        ## extract ICD9 codes from a large, complete dictionary of ICD9 codes
        ##          of all diseases known to medicine
        ## input: select - general code for one class of deseases
        ## output: icd9 - codes of all deseases associated with class
        tmp = pd.read_csv(self.DATA_PATH_2)
        codes_all = tmp['DIAGNOSIS CODE']
        icd9 = []
        for categ in select:
            Ns = [str(categ) in str(y)[0:len(str(categ))] for y in codes_all]
            tmp = codes_all[Ns]
            for y in tmp:
                icd9.append(y)
        return icd9
    
    ##### example: ICD10 codes associated with Cardiovasculas incidents
        ### input: desease classes I2, I6, I7 and G4
        ### t=['I2','I7','I6','G4']
        ### codes_icd10 = find_ICD10_codes(t)
         
    def HES_code_match(self,df=None,icds=None,which='ICD10'):
        # find input ICDs & OPCS codes in specified columns from input HES data frame
        # USe only on'HES' extracted directly from HES.tsv file
        # which: 'diagnosis', 'oper4' or 'diag_icd9'
        if type(icds) is pd.core.series.Series:
            icds = icds.tolist()
            icds = [x for x in icds if str(x) != 'nan']
        cols = df.columns.tolist()
        # remove eids
        cols = cols[1::]
        whichdict = {'ICD10' : 'diag_icd10', 'OPCS' : 'oper4', 'ICD9' : 'diag_icd9'}
        if which not in whichdict:
            print(' (HES_code_match) unrecognised diagnosis code')
            return None
        icd = whichdict[which]
        # Get all the ICD10 diagnosis codes
        df_mini = df[icd].tolist()
        #print df_mini
        res_tmp =[ x in icds for x in df_mini]
        new_df_2 = df[res_tmp]
        #new_df_2 = df.isin(df_mini)
        new_df_2.loc[:,'eid'] = df['eid']
        return new_df_2
            
        
    def OPCS_code_match(self,df=None,icds=None):
        # find input OPCS codes in input HES data frame
        HES_10 = self.HES_code_match(df,icds,which='OPCS')
        return HES_10
        
    def SR_code_match(self,df=None,cols=None,icds=None):
        # find input SR desease codes in specified columns from input dataframe
        # type = (self reported)
        # insert disease codes as numbers not as strings! ex: 1095, not '1095'
        df = df.fillna(value=0) # replace nan by a non-disease code
        if type(icds) is pd.core.series.Series:
            icds = icds.tolist()
        icds = [int(x) for x in icds if str(x) != 'nan']
        # if columns not specified use all columns except eids
        if cols is None:
            cols = df.columns.tolist()
            # remove eids
            cols = cols[1::]
        #new_df = pd.DataFrame(columns=cols)
        #new_df['eid'] = df['eid']
        df = df.replace(np.nan,' ', regex=True)
        new_df = df.isin(icds)
        new_df.insert(0, 'eid', df['eid'])
        #Replaced by Pandas function isin above
        #for col in cols:
        #    res_tmp1 =[ x in icds for x in df[col]]
        #    new_df[col]=res_tmp1
        new_df2 = pd.DataFrame(columns=['eid','SR_res'])
        new_df2['SR_res'] = new_df[cols].sum(axis=1)
        new_df2['eid'] = df['eid']
        return new_df2
        
    def ICD_code_match(self,df=None,cols=None,icds=None):
        # find input ICD desease codes in input 'Mortality' dataframe'
        df = df.fillna(value=0) # replace nan by a non-disease code
        if type(icds) is pd.core.series.Series:
            icds = icds.tolist()
        icds = [x for x in icds if str(x) != 'nan']
        if cols is None:
            cols = df.columns.tolist()
            # remove eids
            cols = cols[1::]
        #new_df = pd.DataFrame(columns=cols)
        #new_df['eid'] = df['eid']
        df = df.replace(np.nan,' ', regex=True)
        new_df = df.isin(icds)
        new_df.insert(0, 'eid', df['eid'])
        #Replaced by Pandas function isin above
        #for col in cols:
        #    res_tmp1 =[ x in icds for x in df[col]]
        #    new_df[col]=res_tmp1
        new_df2 = pd.DataFrame(columns=['eid','ICD_res'])
        new_df2['ICD_res'] = new_df[cols].sum(axis=1)
        new_df2['eid'] = df['eid']
        return new_df2
      
    def HES_first_last_time(self,df=None,date='epistart'):
        # finds the earliest admission date in HES data for each subject
        #   df should be HES file dataframe outout from "HES_code_match"
        eids_unique = list(set(df['eid'].tolist()))
        #cols = get_cols_names(df)
        new_Df = pd.DataFrame(columns=['eid','first_admidate','latest_admidate'])
       #new_Df['eid']=df['eid']
        res = []
        for ee in eids_unique:
            tmp =  df[df['eid']==ee]
            res.append(len(tmp))
            #tmp['admidate'] = pd.to_datetime(tmp['admidate'])
            x = tmp[date].replace(np.nan,self.end_follow_up).min()
            z = tmp[date].replace(np.nan,self.end_follow_up).max()
            df2=pd.DataFrame([[ee,x,z]],columns=['eid','first_admidate','latest_admidate'])
            new_Df=new_Df.append(df2)#,ignore_index=True)
        return new_Df
        
    def HES_after_assess(self,df=None,assess_dates=None,date='epistart'):
        # returns boolean : subject had HES records after baseline
        # input dates needs to come from HES_first_time()
        #   df should be HES file dataframe
        eids = list(set(df['eid'].tolist()))
        DF = pd.DataFrame(columns=['eid','After','first_date_aft'])
        for ee in eids:
            tmp =  df[df['eid']==ee]
            tmp_ass_date = assess_dates[assess_dates['eid']==ee]['assess_date'].iloc[0]
            tmp2= tmp[tmp[date]>tmp_ass_date]
            if len(tmp2)>0:
                oo = 1
                #tmp2['admidate'] = pd.to_datetime(tmp2['admidate'])
                x = tmp2[date].replace(np.nan,self.end_follow_up).min()
            else:
                oo = 0
                x = np.nan
            df2 = pd.DataFrame([[ee,oo,x]],columns=['eid','After','first_date_aft'])
            DF = DF.append(df2)
        return DF
        
    def HES_before_assess(self,dates=None):
        # returns boolean : subject had HES records before baseline
        # input dates needs to come from HES_first_time()
        DF = pd.DataFrame(columns=['eid','Before'])
        DF['eid'] = dates['eid']
        assess_date = dates['assess_date'].tolist()
        admit_date  = dates['first_admidate'].tolist()
        res=[int(asd>add) for (asd,add) in zip(assess_date,admit_date)]
        DF['Before'] = res
        return DF
    
