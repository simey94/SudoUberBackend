from pysimplesoap.client import SoapClient, SoapFault
import time

myid = None


def join(client):
    global myid

    response=client.subscribe()
    my_id = response.subscriber_id

def poll(client):
    global myid

    response=client.poll()
    recieved = response.data
    print recieved

client = SoapClient(
        location="http://localhost:8008",
        action="http://localhost:8008",
        soap_ns="soap",
        trace=False,
        ns=False)

join(client)

while(True):
    poll(client)
    time.sleep(5)

