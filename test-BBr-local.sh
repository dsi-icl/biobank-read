
source activate py36
folder='/media/storage/UkBiobank/Application_236/R4528/'
csvpath=$folder'ukb4528.csv'
htmlpath=$folder'ukb4528.html'
tsvpath='/media/storage/UkBiobank/HESdata/ukb_HES_236.tsv'
outpath='/media/storage/UkBiobank/Cardiac_GWAS/Extended_data/26k/'
outname='excl_atrial_SR'
##
filterconds='/media/storage/codes/BiobankRead-Bash/filters_test.txt'
varsList=$folder'gen_corr_variable.txt'
#'/media/storage/UkBiobank/Application_236/R4528/VeganVars_2.txt'
withdrawn='/media/storage/UkBiobank/Application_18545/withdrawn_18545_oct2018.csv'
#'/media/storage/codes/BiobankRead-Bash/vars.txt'
ICD10codes='/media/storage/UkBiobank/Cardiac_GWAS/Extended_data/26k/excl_atrial_icd10.txt'
SRpath='/media/storage/UkBiobank/Cardiac_GWAS/Extended_data/26k/excl_atrial_SR.txt'


echo "Output destination: " $oupath$outname

#python  Scripts/extract_variables.py \
#        --csv $csvpath \
# 	--html $htmlpath \
# 	--vars $varsList \
#	--visit 0 \
#	--combine outer \
#	--excl $withdrawn \
#	--out $outpath$outname
## 	--remove_outliers True \
## 	--filter $filterconds \
## 	--cov_corr True \


#python  Scripts/extract_death.py \
#   	--csv $csvpath \
#   	--html $htmlpath \
#   	--codes 'All' \
#   	--primary True \
#   	--secondary True \
#        --out $outpath$outname

python  Scripts/extract_SR.py \
	--csv $csvpath \
        --html $htmlpath \
        --out $oupath$outname \
        --disease $SRpath \
        --SRcancer False \
        --visit 'all'
#

#python  Scripts/extract_HES.py \
#       --csv $csvpath \
#       --html $htmlpath \
#       --out $oupath$outname \
#       --tsv $tsvpath \
#       --codes $ICD10codes \
#       --codeType ICD10 \
#       --dateType epistart 
#       --firstvisit False \
#       --baseline False
#
source deactivate 
