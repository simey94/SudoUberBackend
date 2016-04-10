"""Class that is used as a  service node"""

import sys
sys.path.append("..")
import logging

from BaseHTTPServer import HTTPServer
from pysimplesoap.server import SoapDispatcher, SOAPHandler

logging.basicConfig(level=logging.INFO)

class ServiceNodeServer:
    """Service Node"""

    def __init__(self, port):
        """
        Creates SOAP dispatcher
        """
        self.port = port
        self.dispatcher = SoapDispatcher(
            name="Service Node",
            location="http://localhost:%s" % self.port,
            action="http://localhost:%s" % self.port,
            trace=True,
            ns=True)

        self._log = logging.getLogger(__name__)

        self.dispatcher.register_function('poll', self.poll,
            returns={'response': str},
            args={})

    def poll(self):
        return {'response': "YOLO"}

    def run(self):
        """Runs the server"""
        httpd = HTTPServer(("", self.port), SOAPHandler)
        httpd.dispatcher = self.dispatcher
        httpd.serve_forever()

if len(sys.argv) < 2:
    print "Need a token for a Service Node"
    sys.exit(0)

lb_token = int(sys.argv[1])

if __name__ == '__main__':
    server = ServiceNodeServer(lb_token)
    server.run()
