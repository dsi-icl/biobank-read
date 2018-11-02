#!/usr/bin/env python

import sys
import os
import glob
import itertools

#import setuptools
from setuptools import setup

#######
# authored by Dr A. Berlanga 
#####

# Get location to this file:
here = os.path.abspath(os.path.dirname(__file__))
print(here)
funct=["extract_death.py","extract_HES.py","extract_SR.py","extract_variables.py"]

def get_cli_scripts(): 
    files = []
    for filename in funct:
        scripts = [fn for fn in glob.glob(os.path.join('Scripts/**', filename),
                                          recursive = True)
                   if not os.path.basename(fn).startswith('__init__')
                   ]
        files.append(scripts)
    flatten_list = list(itertools.chain.from_iterable(files))
    return(flatten_list)

Scripts = get_cli_scripts() 

# Python version needed:
major, minor1, minor2, s, tmp = sys.version_info

if (major < 3) or (major==3 and minor1<6):
    raise SystemExit("""Python 3.6 or later required, exiting.""")
######
# Thanks Antonio
######

setup(name='BiobankRead2',
      version='3.0',
      description='Python scripts for UKB data',
      author='Deborah Schneider-Luftman',
      author_email='ds711@ic.ac.uk',
      license ='GNU GPL v3',
      packages=['BiobankRead2'],
      #package_dir={'': 'Biobankread2'},
      install_requires=[
	"bs4", "numpy", "pandas", "urllib3", "regex", "seaborn"
	],
      include_package_data = True,
      package_data={'BiobankRead2': ['data/*.tsv','data/*.csv']},
      scripts=Scripts)
