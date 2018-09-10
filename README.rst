################################
Biobank Read - Bash callable 
################################

BiobankRead-Bash is a package that pulls out data from UKBiobank files and turns it into readily usable data-frames for any specified variables, with the option of filtering based on user-specified conditions.
It provides faster and easier pre-processing tools in Python of UKBiobank clinical and phenotypical data, which is otherwise known for its intricate complexity. The functionalities of this package support both main project data and HES records data.

This package is written in python 3 and wrapped in callable scripts, and is intended to be usable as part of processing and analysis pipelines. 

################################
Overview
################################
BiobankRead aims to provide python-based tools for the extraction, cleaning and pre-processing of UK Biobank data.
(UKBiobank_). Approved researchers will have the ability to access the data through the dedicated online portal_ .
The package takes avantage of the data frame tools in pandas and of the regex facilities in re.

Biobankread is also a ressourceful tool for creating custom variables , using existing ones, HES records for any disease / groups of diseases, and any data frame manipulation in Pandas.

################################
Citation
################################
To use this package in published work, please cite us using the following DOI:

.. image:: https://zenodo.org/badge/73500060.svg
   :target: https://zenodo.org/badge/latestdoi/73500060

################################
UKBiobank data
################################
Approved investigators will have access to data, as part of a project, which they have to download in .enc format. The .enc file (enc for encrypted) has to be unpacked locally using helper programs that can be downloaded from the same webpage. Detailed instructions are available on the portal_ ("Data Collection", "Essential Information", "Accessing your data", "Downloading, converting and using your dataset").

After the data has been unpacked locally, there should be two resulting files, a .csv file and a .hmtl file. The csv file contains all the data associated with the project the investigator is working on. The html file explains how that csv file is structured. Conventionally, researchers would open and read the html file, search for a variable, look up its corresponding column number, then extract that column number using STATA, R , Python or similar program.

For each variable, there is between 1 to 28 measurements, across three assessment centre days (baseline, first  and second re-visits). So for one variable, there can be up to 84 associated columns. 

This python package was created with the idea of easing the intricacy of extracting, sorting and analysing such type of data.

HES data
=========
HES (Hospital Episode Statistics) data refers to incidence of hospitalisation anywhere in England for subjects in UKBiobank, as far back as 1997. It contains information about dates of admission/release/operation, diagnosis coded in ICD10 (or ICD9 if prior to 2000), as well as operations & procedure (OPCS) codes when applicable.

This data can be accessed through the portal_ in the following pathway: "Data Collection", "Downloads", "Data Portal", "Connect". This gives access to a database where the data is kept, and has to be queried using SQL.

################################
Installation
################################
Simply Download the files and run from the command line -- in the correct syntax. 
First add the full path to BiobankRead-Bash to your PYTHONPATH environment variable.

You must have the following installed to execute the files:

- Python 3.6 or later
- Pandas
- BeautifulSoup4
- re
- Urllib3
- Seaborn

You are strongly adviced to use this package as part of an anaconda_ environment formatted to run python 3.6 with all the aformentioned dependencies.

############
Usage
############
There are 4 files in BiobankRead-bash, all aimed at data extraction, each specialised in a data type:

- extract_variables.py: for generic clinical / phenotype data
- extract_death.py: for mortality data only
- extract_SR.py: for self-reported illnesses data
- extract_HES.py: for illnesses/ incidents recorded in HES data

These files are designed to be called from a command line terminal as follow:
::
     python extract_variables.py \
        --csv x/y/z.csv \
        --html x/y/z.html \
        --excl x/y/z.csv \
        --vars <list of variables>, in .txt file \
        --out <directory name> x1\y1 \
        #### (optionally)
        --baseline_only True\False (default=True)\
        --remove_missing True\False \
        --filter <list of conditions on variables in vars>, in .txt file \
        --aver_visits True\False \
        --cov_corr True\False \
        --combine  inner\partial\outer (default=outer) &
        
     python extract_death.py \
        --csv <csv file> \
        --html <html file> \
        --excl x/y/z.csv \
        --out <results folder> \
        --codes <any ICD10 code, in .txt file> \ ## Default is 'All', returns all deaths by any cause in UKB
        --primary True \ ## parse primary cause 
        --secondary False & ## parse contributing causes 
        
     python extract_SR.py \
        --csv <csv file> \
        --html <html file> \
        --excl x/y/z.csv \
        --out <results folder> \
        --disease '<something, in .txt file>' \ ## which self-reported diseases to extract
        --SRcancer True \ ## parse self-repoted cancer OR non-cancer diseases
        --baseline_only False & ## Only keep data from baseline assessment centre
        
     python HES_extract.py \
        --csv <csv file> \
        --html <html file> \
        --excl x/y/z.csv \
        --tsv <tsv file> \
        --out <results folder> \
        --codes <disease codes, in .txt file> \
        --codeType <ICD10 or ICD9> \
        #### optionally
        --dateType <type> \ ### epistart or admidate
        --firstvisit True \ ### Default: True, Mark earliest/latest visit for each subjects
        --baseline True & ### Mark visits before and after baseline assessment 
 
For ease of use, the --csv, --html, --excl and --tsv filepaths can be put in a text file called UKBBpaths.txt
in the current directory or in the user home directory. This file is automatically read when any of the scripts are run.
An example is below:
::
      csv      Z:\EABOAGYE\Users\wcrum\Projects\UKBB\UKBB-data-2018\ukb21204.csv
      html   Z:\EABOAGYE\Users\wcrum\Projects\UKBB\UKBB-data-2018\ukb21204.html
      excl    Z:\EABOAGYE\Users\wcrum\Projects\UKBB\UKBB-data-2018\w10035_20180503_exclusions.csv
      tsv      Z:\EABOAGYE\Users\wcrum\Projects\UKBB\UKBB-data-2018\ukb.tsv


It is best to call these functions within executable files - such as in the test_ script here - to ensure alll input variables are well specified.
        

############
Example
############
We aim to extract all data regarding lung cancer in UkBiobank, using the data associated to a specific application. For this purpose, we look through the following:

- HES data: any hospital admission marked with the following ICD10 codes:  C34, C340, C341, C342, C343, C348, C349, or ICD9 codes: 162 (162.0, 2, 3, 4, 5, 8, or 9)
- Self reported data: anyone who reported having the illnesses # 1001, 1027 and/or 1028 in questionaires (data field 20001_)
- Mortality data: anyone who had one of the following codes listed as primary_ and/or secondary_ cause(s) of death: C34, C340, C341, C342, C343, C348, C349

Note that some subjects will have records appearing in several or all of these fields.

We proceed by extracting data with the desired specifications as follows:

- python extract_HES.py .... --codes ICD10LC.txt (ICD10LC.txt contains C34, C340, C341, C342, C343, C348, C349) --codeType ICD10 ....
- python extract_HES.py .... --codes ICD9LC.txt (ICD9LC.txt contains 1620, 1622, 1623, 1624, 1625, 1628, 1629) --codeType ICD9 ....
- python extract_SR.py .... --disease SRLC.txt (ICD9LC.txt contains 1001, 1027, 1028) --SRcancer True ...
- python extract_death.py .... --codes ICD10.txt --primary True --secondary True ....

Make sure to specify all other necessary input variables before running the scripts.

Each of these script calls will return an output file, each of these will have one common column: eid - the anonymised IDs of the UKB subjects. Using this, all of the output files can be merged together around their 'eid' columns using any conventional data analysis software (R, python, SAS, ...)

That's it - in a few easy steps we extracted all information on lung cancer available in UKBiobank!

############
Notes
############

extract_variables.py
Use --combine to control how the data is output.
--combine  inner only outputs cases (eids) which have a valid entry for all extracted variables
--combine  outer output all cases (eids) regardless of the validity of the extracted variables
--combine  partial outputs cases (eids) which have at least one valid entry in the extracted variables


=====   =====  ====== 
eid     A      B
=====   =====  ======
0		  2		3
1		  NaN	   4
2		  5		NaN
3		  NaN	   NaN
=====   =====  ====== 



In the above NaN (Not-a-Number) is an invalid entry.

--combine  outer would result in the following:
eid		A		B
0		2		3
1		NaN		4
2		5		NaN
3		NaN		NaN

--combine  partial would result in the following:
eid		A		B
0		2		3
1		NaN		4
2		5		NaN

--combine  inner would result in the following:
eid		A		B
0		2		3



################################
Acknowledgement
################################
BiobankRead was developed as part of the ITMAT Data Science Group and the Epidemiology & Biostatistics department at Imperial College London. 

################################
Thanks
################################
Much gratitude is owed to Dr Bill Crum, who contributed to this project and co-authored its related papers


“On the planet Earth, man had always assumed that he was more intelligent than dolphins because he had achieved so much—the wheel, New York, wars and so on—whilst all the dolphins had ever done was muck about in the water having a good time. But conversely, the dolphins had always believed that they were far more intelligent than man—for precisely the same reasons.”


.. _UKBiobank: http://www.ukbiobank.ac.uk/
.. _portal: https://amsportal.ukbiobank.ac.uk/
.. _zonodo: https://zenodo.org/badge/73500060.svg
.. _testpy: https://github.com/saphir746/BiobankRead/blob/master/test-class.py
.. _testHFpy: https://github.com/saphir746/BiobankRead/blob/master/test_HF.py
.. _anaconda: https://conda.io/docs/user-guide/tasks/manage-environments.html
.. _test: https://github.com/saphir746/BiobankRead-Bash/blob/dev/test-BBr-script.sh
.. _20001: http://biobank.ndph.ox.ac.uk/showcase/field.cgi?id=20001
.. _primary: http://biobank.ndph.ox.ac.uk/showcase/field.cgi?id=40001
.. _secondary: http://biobank.ndph.ox.ac.uk/showcase/field.cgi?id=40002
