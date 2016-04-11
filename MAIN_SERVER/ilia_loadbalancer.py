"""Class that is used as a Load Balancer"""
import sys
sys.path.append("..")

import time
from collections import defaultdict
from subprocess import Popen
from pysimplesoap.client import SoapClient
from BaseHTTPServer import HTTPServer
from pysimplesoap.server import SoapDispatcher, SOAPHandler
import configuration as conf

from collections import defaultdict
from threading import Thread

node_to_connect = defaultdict(list)

class LoadBalancerServer:

    def __init__(self, port, query):
        """ Creates SOAP dispatcher """

        self.port = port
        self.query = query

        self.messages = defaultdict(list) # usertoken -> messages
        self.last_send_nonce = defaultdict(int)

        self.dispatcher = SoapDispatcher(
            name="Load Balancer %s, %s" % (self.port, self.query),
            location=conf.hostname % self.port,
            action=conf.hostname % self.port,
            trace=True,
            ns=True)

        self.dispatcher.register_function('poll', self.poll, returns={'response': str}, args={})

    def poll(self, user_token):
        if user_token in self.messages:
            return {'data': self.messages[user_token], 'response_code': conf.SUCCESS_CODE}
        else:
            return {'data': None, 'response_code': conf.ERROR_CODE}

    def publish(self, p_message):
        for user_token in self.messages:


    def run(self):
        """Runs the server"""

        httpd = HTTPServer((conf.http_hostname, self.port), SOAPHandler)
        httpd.dispatcher = self.dispatcher
        httpd.serve_forever()

if len(sys.argv) < 2:
    print "Need a token for a lb"
    sys.exit(0)

lb_token = int(sys.argv[1])
query = sys.argv[2]

if __name__ == '__main__':
    server = LoadBalancerServer(lb_token, query)
    server.run()
