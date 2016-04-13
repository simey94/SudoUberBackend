cd SERVER/
timeout -sTERM 1m python server.py &
cd ..

cd SERVICES/
timeout -sTERM 1m python ilia_test_service.py &
cd ..

cd CLIENT/

for i in `seq 1 $1`;
do
timeout -sTERM 1m python client.py &
done
timeout -sTERM 1m python client.py
cd ..
