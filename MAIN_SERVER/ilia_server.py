import sys
sys.path.append("..")

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from pysimplesoap.client import SoapClient, SoapFault
from BaseHTTPServer import HTTPServer
from subprocess import Popen
from collections import defaultdict
import random
import time

query_to_lbs = defaultdict(list)

def publish(publisher_id, message):
    return "CAT"

def subscribe(username, password):
    return {'response':{"subscriber_id":str(random.random())}}

def poll(token, query):
    if query not in query_to_lbs:
        lb_token = 8000 + int(50*random.random())
        Popen(["python", "ilia_loadbalancer.py", str(lb_token)])

        client = SoapClient(
                location="http://localhost:%s" % str(lb_token),
                action="http://localhost:%s" % str(lb_token),
                soap_ns="soap",
                trace=False,
                ns=False)
        query_to_lbs[query].append(client)
        time.sleep(1)
    response = query_to_lbs[query][0].poll()

    return {'response':{"data": response.response}}

class Server:
    """
    Main server
    """

    def __init__(self):
        """
        Creates SOAP dispatcher
        """
        self.dispatcher = SoapDispatcher(
            name="Main Server",
            location="http://localhost:8008",
            action="http://localhost:8008",
            documentation = "CS3301 Pseudo-Uber service-oriented system",
            trace=True,
            ns=True)

        self.dispatcher.register_function('publish', publish,
            returns={'response': str},
            args={'publisher_id': int, 'message': str})

        self.dispatcher.register_function('subscribe', subscribe,
            returns={'response': {"subscriber_id": str}},
            args={'username':str, 'password': str})

        self.dispatcher.register_function('poll', poll,
            returns={'response': {"data": str}},
            args={'token': str, 'query': str})

    def run(self):
        """
        Runs the server
        """
        self.subscribers = {}

        httpd = HTTPServer(("", 8008), SOAPHandler)
        httpd.dispatcher = self.dispatcher
        httpd.serve_forever()

if __name__ == '__main__':
    server = Server()
    server.run()
