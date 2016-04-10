"""File contains the code to run the server"""
import sys
sys.path.append("../..")
sys.path.append("..")

import configuration as localconf
import global_configuration as globalconf
import global_utils as utils
from threading import Thread
import time
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from pysimplesoap.client import SoapClient
from collections import defaultdict
from BaseHTTPServer import HTTPServer

subscribers = {} # user_token -> client
publishers = defaultdict(list) # service_token -> tags

interest = defaultdict(list)

def subscribe(username, password, port):
    token = utils.generate_token(username, password, port)
    client = SoapClient(location=globalconf.hostname % str(port), action=globalconf.hostname % str(port), soap_ns="soap", trace=True, ns=True)
    subscribers[token] = client
    return {"subscriber_id": token}

def register_publisher(service_name, port, tags):
    token = utils.generate_token(service_name, service_name, port)
    client = SoapClient(location=globalconf.hostname % str(port), action=globalconf.hostname % str(port),
                        soap_ns="soap", trace=True, ns=True)
    publishers[token] += tags
    return {"service_id": token}

def publish(service_token, message):
    pass

dispatcher = SoapDispatcher(
    name="Main Server",
    location=globalconf.location,
    action=globalconf.location,
    documentation="doc",
    trace=True,
    ns=True)

dispatcher.register_function('subscribe', subscribe,
                                  returns={"subscriber_id": str},
                                  args={"username": str, "password":str, "port": str})

httpd = HTTPServer((globalconf.http_hostname, globalconf.s_port), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()