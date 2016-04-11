"""File contains the code to run the client"""
import sys
sys.path.append("../..")
sys.path.append("..")

import configuration as localconf
import global_configuration as globalconf
import global_utils as utils

def receive(message):
    print message
    return {"ack": "I feel the bern"}

_username = utils.generate_username()
_password = utils.generate_password()
_port = utils.generate_port()

print "Username:%s, Password:%s, Port:%s" %(_username, _password, _port)

client = utils.client(globalconf.location)

dispatcher = utils.dispatcher("Client Username:%s, Password:%s, Port:%s" % (_username, _password, _port), globalconf.hostname % str(_port))
dispatcher.register_function('receive', receive, returns={"ack":str}, args={"message": str})

thread = utils.open_server_thread(globalconf.http_hostname, _port, dispatcher)

token = client.subscribe(username=_username, password=_password, port=_port).subscriber_id
print "ASSIGNED TOKEN:%s" % token

thread.join()