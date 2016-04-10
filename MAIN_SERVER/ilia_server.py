import sys

sys.path.append("..")

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from pysimplesoap.client import SoapClient
from BaseHTTPServer import HTTPServer
from subprocess import Popen
from collections import defaultdict
import configuration as conf
import server_utils as utils
import time

query_to_lbs = defaultdict(list)


def subscribe(username, password):
    return {'response': {"subscriber_id": str(username)+str(password)}}


def poll(token, query):
    if query not in query_to_lbs:
        usertoken = utils.generate_token()
        fport = utils.generate_port(usertoken)
        Popen([conf.runner_loadbalancer, conf.file_loadbalancer, str(fport)])

        client = SoapClient(
            location=conf.hostname % fport,
            action=conf.hostname % fport,
            soap_ns="soap",
            trace=False,
            ns=False)
        query_to_lbs[query].append(client)
        time.sleep(1)

    response = query_to_lbs[query][0].poll()

    return {'response': {"data": response.response}}


class Server:
    """Main server"""

    def __init__(self):
        """Creates SOAP dispatcher"""
        self.dispatcher = SoapDispatcher(
            name="Main Server",
            location=conf.location,
            action=conf.location,
            documentation="CS3301 Pseudo-Uber service-oriented system",
            trace=True,
            ns=True)

        self.dispatcher.register_function('subscribe', subscribe,
                                          returns=conf.subscribe_return_pattern,
                                          args=conf.subscribe_arg_pattern)

        self.dispatcher.register_function('poll', poll,
                                          returns=conf.poll_return_pattern,
                                          args=conf.poll_arg_pattern)

    def run(self):
        """Runs the server"""
        httpd = HTTPServer((conf.http_hostname, conf.s_port), SOAPHandler)
        httpd.dispatcher = self.dispatcher
        httpd.serve_forever()

if __name__ == '__main__':
    server = Server()
    server.run()
