mkdir -p datasets

client_sizes=( 0 1 5 10 15 20 )
for i in "${client_sizes[@]}"
do
    . ./run.sh $i
    mkdir -p datasets/dir$i
    mv ./CLIENT/outfile* ./datasets/dir$i/
done
