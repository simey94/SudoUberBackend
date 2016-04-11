"""File contains the code to run the server"""
import sys
sys.path.append("../..")
sys.path.append("..")

import configuration as localconf
import global_configuration as globalconf
import global_utils as utils
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from collections import defaultdict
from BaseHTTPServer import HTTPServer

subscribers = {} # user_token -> client
publishers = {} # service_token -> client

publishers_tags = defaultdict(list) # service_token -> tags
interest = defaultdict(list) # user_token -> tags


def subscribe(username, password, port):
    token = utils.generate_token(username, password, port)

    client = utils.client(globalconf.hostname % str(port))

    subscribers[token] = client
    return {"subscriber_id": token}


def subscribe_to_tags(token, tags):
    interest[token] += tags # TODO: check if that works
    #TODO: migrate that to the load balancers
    return {"errorcode": globalconf.SUCCESS_CODE}


def register_publisher(service_name, port, tags):
    token = utils.generate_token(service_name, service_name, port)

    client = utils.client(globalconf.hostname % str(port))

    publishers[token] = client
    publishers_tags[token] += tags #TODO: check if this works
    return {"errorcode": globalconf.SUCCESS_CODE}


def publish(service_token, message):
    #TODO: add publishing capability based on a set of tags
    pass


"""Server Dispatcher code"""
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

# dispatcher.register_function('subscribe_to_tags', subscribe_to_tags,
#                              returns={"errorcode": int},
#                              args={"token": str, "tags": str})
#
# dispatcher.register_function('publish', publish,
#                              returns={"errorcode": int},
#                              args={"service_token":str, "message":str})
#
# dispatcher.register_function('register_publisher', register_publisher,
#                              returns={"errorcode": int},
#                              args={"service_name": str, "port": str, "tags": str})

print "Running the server at %s:%s" % (globalconf.http_hostname, globalconf.s_port)
httpd = HTTPServer((globalconf.http_hostname, globalconf.s_port), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()