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

interest = defaultdict(list) # user_token -> tags

def subscribe(username, password, port):
    token = utils.generate_token(username, password, port)
    client = SoapClient(location=globalconf.hostname % str(port), action=globalconf.hostname % str(port), soap_ns="soap", trace=True, ns=True)
    subscribers[token] = client
    return {"subscriber_id": token}

def subscribe_to_tags(token, tags):
    interest[token] += tags
    return {"errorcode": globalconf.SUCCESS_CODE}

def register_publisher(service_name, port, tags):
    token = utils.generate_token(service_name, service_name, port)
    client = SoapClient(location=globalconf.hostname % str(port), action=globalconf.hostname % str(port),
                        soap_ns="soap", trace=True, ns=True)
    publishers[token] += tags
    return {"errorcode": globalconf.SUCCESS_CODE}

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

dispatcher.register_function('subscribe_to_tags', subscribe_to_tags,
                             returns={"errorcode": int},
                             args={"token": str, "tags": list})

dispatcher.register_function('publish', publish,
                             returns={"errorcode": int},
                             args={"service_token":str, "message":str})

dispatcher.register_function('register_publisher', register_publisher,
                             returns={"errorcode": int},
                             args={"service_name": str, "port": str, "tags": list})

httpd = HTTPServer((globalconf.http_hostname, globalconf.s_port), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()