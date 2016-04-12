"""File contains the code to run the client"""
import sys
sys.path.append("../..")
sys.path.append("..")

import global_configuration as globalconf
import global_utils as utils
import time

def receive(message):
    print message
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
while(True):
    services = server_client.request_services(user_token=token).services
    print "Available services", services
    time.sleep(3)

thread.join()