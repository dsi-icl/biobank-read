#!/bin/bash

#PBS -l walltime=06:00:00
#PBS -l select=1:ncpus=4:mem=64gb
#PBS -q med-bio
#PBS -k oe
#PBS -N BBR

# Where the data is store'
CSV_path=$WORK/UkBiobank/Application_236/R4528/ukb4528.csv
HTML_path=$WORK/UkBiobank/Application_236/R4528/ukb4528.html
TSV_path=$WORK/UkBiobank/HES_data/ukb_HES_236.tsv
# Variables and conditions
varList=$WORK/BBR/vars_test.txt ##("'Age assessment'" "'BMI'") ###$WORK/BBR/vars_test.txt 
filterList=$WORK/BBR/filters_test.txt  #("Age assessment>50" "Age assessment<70" "BMI>=23" "BMI<=30")
HES_codes=$WORK/BBR/ICD10_codes.txt
Death_codes=$HES_codes
SR_things=$WORK/BBR/SR_disease.txt
# Output
outname=test_hpc
outname_HES=test_hpc_HES
outname_death=test_hpc_dead
outname_SR=test_hpc_SR
# Construct script path and arguments

cp $WORK/BBR/* $TMPDIR
module load anaconda3/personal
source activate py36

python extract_variables.py \
	--csv $CSV_path \
	--html $HTML_path \
	--vars $varList \
        #--filter $filterList \
        #--remove_outliers 'True' \
        #--baseline_only 'False' \
	--out $WORK/results/$outname &

python HES_extract.py \
	--csv $CSV_path \
        --html $HTML_path \
	--tsv $TSV_path \
	--codes $HES_codes \
	--codeType 'ICD10' \
	--dateTpe 'epistart' \
	##--firstvisit 'True' \
        ##--baseline 'True' \
	--out $WORK/results/$outname_HES &

python extract_death.py \
        --csv $CSV_path \
        --html $HTML_path \
	--codes $Death_codes \
	##--primary 'True' \
        ##--secondary 'False' \
	--out $WORK/results/$outname_death &


python extract_SR.py \
        --csv $CSV_path \
        --html $HTML_path \
	--disease $SR_things \
	--SRcancer 'True' \
	--out $WORK/results/$outname_SR &







