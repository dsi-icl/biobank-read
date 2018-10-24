
source activate py36
csvpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.csv'
htmlpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.html'
tsvpath='/media/storage/UkBiobank/Application_10035/HES/ukb.tsv'
outpath='/media/storage/UkBiobank/Application_236/'
outname='VeganVars_2_236'
##
filterconds='/media/storage/codes/BiobankRead-Bash/filters_test.txt'
varsList='/media/storage/UkBiobank/Application_236/R4528/VeganVars_2.txt'
withdrawn='/media/storage/UkBiobank/Application_236/withdrawn_236_oct2018.csv'
#'/media/storage/codes/BiobankRead-Bash/vars.txt'
ICD10codes='/media/storage/codes/BiobankRead-Bash/ICD10_codes.txt'
SRpath='/media/storage/codes/BiobankRead-Bash/SR_disease.txt'


echo "Output destination: " $oupath$outname

python extract_variables.py \
        --csv $csvpath \
 	--html $htmlpath \
 	--vars $varsList \
	--baseline_only False \
	--combine outer \
	--excl $withdrawn \
	--out $outpath$outname
## 	--remove_outliers True \
## 	--filter $filterconds \
## 	--cov_corr True \


#python extract_death.py \
#   	--csv $csvpath \
#   	--html $htmlpath \
#   	--codes 'All' \
#   	--primary True \
#   	--secondary True \
#        --out $outpath$outname

#python extract_SR.py \
#	--csv $csvpath \
#        --html $htmlpath \
#        --out $oupath$outname \
#        --disease $SRpath \
#        --SRcancer False \
#        --baseline_only False


#python HES_extract.py \
#       --csv $csvpath \
#       --html $htmlpath \
#       --out $oupath$outname \
#   --tsv $tsvpath \
#   --codes $ICD10codes \
#   --codeType ICD10 \
#   --dateType epistart \
#   --firstvisit True \
#   --baseline True
#
source deactivate 
