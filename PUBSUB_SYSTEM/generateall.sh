for file in $1
do
    cd $file/
    echo $file
	cat outfile* > all
	cd ../..
	python avg_calc.py $file/all
done
