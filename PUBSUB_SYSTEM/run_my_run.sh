mkdir -p datasets

client_sizes=(1 5 10 15 20 )
for i in "${client_sizes[@]}"
do
    . ./run.sh $i
    mv ./CLIENT/outfile ./datasets/outfile$i
done
