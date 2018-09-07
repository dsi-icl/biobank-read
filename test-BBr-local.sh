
source activate py36
csvpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.csv'
htmlpath='/media/storage/UkBiobank/Application_236/R4528/ukb4528.html'
outpath='/media/storage/codes/BiobankRead-Bash/'
outname='testnewVARpartial'
varsList='/media/storage/codes/BiobankRead-Bash/vars.txt'

python extract_variables.py \
       	--csv $csvpath \
	--html $htmlpath \
	--vars $varsList \
	--remove_outliers True \
        --baseline_only False \
	--combine partial \
        --out $outpath$outname

