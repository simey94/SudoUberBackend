"""Class that is used as a Load Balancer"""
import random
import sys
import time
from collections import defaultdict
from subprocess import Popen
from pysimplesoap.client import SoapClient
from BaseHTTPServer import HTTPServer
from pysimplesoap.server import SoapDispatcher, SOAPHandler
import configuration as conf

sys.path.append("..")
query_to_lbs = defaultdict(list)

class LoadBalancerServer:
    """Load Balancer"""

    def __init__(self, port):
        """
        Creates SOAP dispatcher
        """

        self.port = port

        self.dispatcher = SoapDispatcher(
            name="Load Balancer %s" % self.port,
            location=conf.hostname % self.port,
            action=conf.hostname % self.port,
            trace=True,
            ns=True)

        self.dispatcher.register_function('poll', self.poll,
            returns={'response': str},
            args={})

    def poll(self, query):
        if query not in query_to_lbs:
            node_token = 8000 + int(50 * random.random())
            Popen(["python", "node.py", str(node_token)])

            client = SoapClient(
                location="http://localhost:%s" % str(node_token),
                action="http://localhost:%s" % str(node_token),
                soap_ns="soap",
                trace=False,
                ns=False)
            query_to_lbs[query].append(client)
            time.sleep(1)
        response = query_to_lbs[query][0].poll()

        return {'response': {"data": response.response}}


    def run(self):
        """Runs the server"""
        httpd = HTTPServer(( "", self.port), SOAPHandler)
        httpd.dispatcher = self.dispatcher
        httpd.serve_forever()

if len(sys.argv) < 2:
    print "Need a token for a lb"
    sys.exit(0)

lb_token = int(sys.argv[1])

if __name__ == '__main__':
    server = LoadBalancerServer(lb_token)
    server.run()
