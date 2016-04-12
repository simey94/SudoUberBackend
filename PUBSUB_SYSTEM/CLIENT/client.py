"""File contains the code to run the client"""
import sys
sys.path.append("../..")
sys.path.append("..")

import global_configuration as globalconf
import global_utils as utils
import time
from random import randint, random

def receive(message):
    print "ANSWER:", message
    return {"ack": "I feel the bern"}

_username = utils.generate_username()
_password = utils.generate_password()
_port = utils.generate_port()

print "Username:%s, Password:%s, Port:%s" %(_username, _password, _port)
client = utils.client(globalconf.location)
response = client.subscribe(username=_username, password=_password, port=_port)

token = response.token
alloc_server = response.server

dispatcher = utils.dispatcher("Client Username:%s, Password:%s, Port:%s" % (_username, _password, _port), globalconf.hostname % str(_port))
dispatcher.register_function('receive', receive, returns={"ack":str}, args={"message": str})

thread = utils.open_server_thread(globalconf.http_hostname, _port, dispatcher)
print "ASSIGNED TOKEN:%s" % token

time.sleep(5)

server_client = utils.client(alloc_server)

server_client.notify(user_token=token, hostname=globalconf.hostname % _port)

message_id = 1
while(True):
    print "Looking for available services..."
    services = str(server_client.request_services(user_token=token).services)

    if services != "":
        print "Services:", services
        a_services = services.split(",")

        if len(a_services) == 1:
            ctoken = a_services[0]
        else:
            index = randint(0, len(a_services)-1)
            ctoken = a_services[index]

        print "Requesting:", str(ctoken)

        response = server_client.service(client_message_id=message_id, user_token=token, service_token=ctoken, additional_info="London")

        if int(response.errorcode) == globalconf.REPETITION_CODE:
            message_id = int(response.message_id)
        else:
            if random() > 0.8:
                message_id += randint(1, 7)
            else:
                message_id += 1
    else:
        print "No services found."

    time.sleep(3)
    print "-"*10

thread.join()