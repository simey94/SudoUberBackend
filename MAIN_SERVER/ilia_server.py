import sys
sys.path.append("..")

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
import random


def publish(publisher_id, message):
    return "CAT"

def subscribe(username, password):
    "Return subscriber id"
    return {'response':{"subscriber_id":str(random.random())}}

def poll(token):
    return {'response':{"data":str(random.random())}}


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
            args={'token': str})

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



