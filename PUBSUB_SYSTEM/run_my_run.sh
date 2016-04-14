ulimit -v hard
ulimit -t hard
ulimit -u hard

mkdir -p datasets

#client_sizes=( 0 1 2 3 4 5 10 15 20 )
client_sizes=(15)
for i in "${client_sizes[@]}"
do
    . ./run.sh $i
    mkdir -p datasets/dir$i
    mv ./CLIENT/outfile* ./datasets/dir$i/
done
