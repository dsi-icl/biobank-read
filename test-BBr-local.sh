
source activate py36
csvpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.csv'
htmlpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.html'
outpath='/media/storage/codes/BiobankRead-Bash/'
outname='testnewVARpartial_deaths'
filterconds='/media/storage/codes/BiobankRead-Bash/filters_test.txt'
varsList='/media/storage/codes/BiobankRead-Bash/vars.txt'
ICD10codes='/media/storage/codes/BiobankRead-Bash/ICD10_codes.txt'

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
python extract_death.py \
   	--csv $csvpath \
   	--html $htmlpath \
   	--codes $ICD10codes \
   	--primary True \
   	--secondary True \
     --out $outpath$outname

source deactivate 
