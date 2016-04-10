"""Class that is used as a Load Balancer"""

import sys
sys.path.append("..")

from BaseHTTPServer import HTTPServer
from pysimplesoap.server import SoapDispatcher, SOAPHandler

class LoadBalancerServer:
    """Load Balancer"""

    def __init__(self, port):
        """
        Creates SOAP dispatcher
        """

        self.port = port
        self.dispatcher = SoapDispatcher(
            name="Load Balancer",
            location="http://localhost:%s" % self.port,
            action="http://localhost:%s" % self.port,
            trace=True,
            ns=True)

        self.dispatcher.register_function('poll', self.poll,
            returns={'response': str},
            args={})

    def poll(self):
        return {'response': "HEEEEY"}

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
