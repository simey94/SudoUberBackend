cd SERVER/
timeout -sTERM 4m python server.py &
cd ..
sleep 2

cd SERVICES/
timeout -sTERM 4m python ilia_test_service.py &
cd ..
sleep 2

cd CLIENT/

for i in `seq 1 $1`;
do
timeout -sTERM 4m python client.py &
done
timeout -sTERM 4m python client.py
cd ..
