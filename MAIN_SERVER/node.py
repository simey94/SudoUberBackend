# To run it type "python node.py 9000 price_estimator.py"
import sys
import md5
import imp
import glob
sys.path.append("..")

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer
import random


def load_module(code_path):
    """Loads a python module with a specific path to it"""
    try:
        try:
            fin = open(code_path, 'rb')
            return imp.load_source(
                md5.new(code_path).hexdigest(),
                code_path,
                fin)
        finally:
            try:
                fin.close()
            except:
                pass
    except ImportError:
        raise
    except:
        raise

def calculate(location):
    return {'response':{load_module(sys.argv[2]).calculate(location)}}

class Server:
    """
    Main server
    """

    def __init__(self):
        """
        Creates SOAP dispatcher
        """

        self.dispatcher = SoapDispatcher(
            name="Node Server",
            location="http://localhost:"+str(sys.argv[1]),
            action="http://localhost:"+str(sys.argv[1]),
            documentation = "CS3301 Pseudo-Uber service-oriented system",
            trace=True,
            ns=True)

        self.dispatcher.register_function('calculate', calculate, 
            returns={'response': str},
            args={'location': str})


    def run(self):
        """
        Runs the server
        """
        self.subscribers = {}

        httpd = HTTPServer(("", int(sys.argv[1])), SOAPHandler)
        httpd.dispatcher = self.dispatcher
        httpd.serve_forever()

if __name__ == '__main__':
    server = Server()
    server.run()


