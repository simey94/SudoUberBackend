"""File contains the code to run the client"""
import sys
sys.path.append("../..")
sys.path.append("..")

import configuration as localconf
import global_configuration as globalconf
import global_utils as utils

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from pysimplesoap.client import SoapClient

import time
from threading import Thread
from BaseHTTPServer import HTTPServer

def start_server(port, dispatcher):
    httpd = HTTPServer((globalconf.http_hostname, port), SOAPHandler)
    httpd.dispatcher = dispatcher
    print "Registring at %s " % (globalconf.http_hostname+str(port))
    httpd.serve_forever()

def receive(message):
    print message
    return {"ack": "I feel the bern"}

_username = utils.generate_username()
_password = utils.generate_password()
_port = utils.generate_port()

print "Username:%s, Password:%s, Port:%s" %(_username, _password, _port)

client = SoapClient(location=globalconf.location, action=globalconf.location, soap_ns="soap", trace=False, ns=False)

dispatcher = SoapDispatcher(
    name="Client Username:%s, Password:%s, Port:%s" %(_username, _password, _port),
    location=globalconf.hostname % _port,
    action=globalconf.hostname % _port,
    documentation="doc",
    trace=True,
    ns=True)

dispatcher.register_function('receiveArabMoney', receive, returns={"ack":str}, args={"message": str})

thread = Thread(target = start_server, args=(_port, dispatcher ))
thread.start()

token = client.subscribe(username=_username, password=_password, port=_port).subscriber_id
print "ASSIGNED TOKEN:%s" % token

thread.join()