#!/bin/bash


# Where the data is store'
CSV_path=$WORK/UkBiobank/Application_236/R4528/ukb4528.csv
HTML_path=$WORK/UkBiobank/Application_236/R4528/ukb4528.html

# Variables and conditions
varList=$WORK/BBR/vars_test.txt ##("'Age assessment'" "'BMI'") ###$WORK/BBR/vars_test.txt 
filterList=$WORK/BBR/filters_test.txt  #("Age assessment>50" "Age assessment<70" "BMI>=23" "BMI<=30")

# Output
outname=test_hpc

# Construct script path and arguments
cd $WORK/BBR
module load anaconda3/personal
source activate py36

python extract_variables.py \
	--csv $CSV_path \
	--html $HTML_path \
	--vars $varList \
	--out $PWD/$outname &	

	#--filter $filterList \
	#--remove_outliers 'True' \
	#--baseline_only 'False' &
            


