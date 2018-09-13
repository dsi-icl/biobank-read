
source activate py36
csvpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.csv'
htmlpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.html'
tsvpath='/media/storage/UkBiobank/HESdata/ukb_HES_236.tsv'
outpath='/media/storage/codes/BiobankRead-Bash/'
outname='testnewVARpartial_HES'
##
filterconds='/media/storage/codes/BiobankRead-Bash/filters_test.txt'
varsList='/media/storage/codes/BiobankRead-Bash/vars.txt'
ICD10codes='/media/storage/codes/BiobankRead-Bash/ICD10_codes.txt'
SRpath='/media/storage/codes/BiobankRead-Bash/SR_disease.txt'


echo "Output destination: " $oupath$outname

#python extract_variables.py \
#        	--csv $csvpath \
# 	--html $htmlpath \
# 	--vars $varsList \
# 	--remove_outliers True \
#         --baseline_only False \
# 	--filter $filterconds \
# 	--combine partial \
# 	--cov_corr True \
#         --out $outpath$outname
# 
#python extract_death.py \
#   	--csv $csvpath \
#   	--html $htmlpath \
#   	--codes $ICD10codes \
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


python HES_extract.py \
       --csv $csvpath \
       --html $htmlpath \
       --out $oupath$outname \
   --tsv $tsvpath \
   --codes $ICD10codes \
   --codeType ICD10 \
   --dateType epistart \
   --firstvisit True \
   --baseline True

source deactivate 
