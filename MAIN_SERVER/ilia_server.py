import sys
sys.path.append("..")

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
import random

def publish(publisher_id, message):
    return "CAT"

dispatcher = SoapDispatcher(
        'my_dispatcher',
        location="http://localhost:8008",
        action="http://localhost:8008",
        trace=False,
        ns=False)

def subscribe(username, password):
    return {'response':{"subscriber_id":str(random.random())}}

def poll(token):
    return {'response':{"data":str(random.random())}}

dispatcher.register_function('publish', publish, returns={'response': str},
        args={'publisher_id': int, 'message': str})

dispatcher.register_function('subscribe', subscribe,
        returns={'response': {"subscriber_id": str}},
        args={'username':str, 'password': str})

dispatcher.register_function('poll', poll,
        returns={'response': {"data": str}},
        args={'token': str})

subscribers = {}


print "Starting the server"

httpd = HTTPServer(("", 8008), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()
