"""File contains the code to run the client"""
import sys
sys.path.append("../..")
sys.path.append("..")

import global_configuration as globalconf
import global_utils as utils
import time
from random import randint, random
from threading import Lock

_username = utils.generate_username()
_password = utils.generate_password()
_port = utils.generate_port()

mfile = open("outfile"+str(_port), "w")
file_lock = Lock()

def receive(client_message_id, message):
    global mfile, file_lock
    now = time.time()
    print "Message:", message
    print "Reply time:", (now-messages[int(client_message_id)])
    file_lock.acquire()
    value = str(now-messages[int(client_message_id)])
    mfile.write( value + "\n")
    mfile.flush()
    file_lock.release()
    return {"ack": "I feel the bern"}

print "Username:%s, Password:%s, Port:%s" %(_username, _password, _port)
client = utils.client(globalconf.location)
response = client.subscribe(username=_username, password=_password, port=_port)

token = response.token
alloc_server = response.server

dispatcher = utils.dispatcher("Client Username:%s, Password:%s, Port:%s" % (_username, _password, _port), globalconf.hostname % str(_port))
dispatcher.register_function('receive', receive, returns={"ack":str}, args={"client_message_id": int, "message": str})

thread = utils.open_server_thread(globalconf.http_hostname, _port, dispatcher)
#print "ASSIGNED TOKEN:%s" % token

time.sleep(5)

server_client = utils.client(alloc_server)

server_client.notify(user_token=token, hostname=globalconf.hostname % _port)

messages = {}
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
        time_sent = time.time()
        response = server_client.service(client_message_id=message_id, user_token=token, service_token=ctoken, additional_info="3")

        if int(response.errorcode) == globalconf.REPETITION_CODE:
            message_id = int(response.message_id)
        else:
            messages[message_id] = time_sent
            if random() > globalconf.accuracy:
                message_id += randint(1, 7)
            else:
                message_id += 1
    else:
        print "No services found."
        pass

    time.sleep(3)
    #print "-"*10

thread.join()
