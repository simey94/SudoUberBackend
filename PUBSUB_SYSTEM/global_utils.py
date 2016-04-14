"""Utilities by the server"""

from random import random, SystemRandom
import string
from BaseHTTPServer import HTTPServer
from threading import Thread

from pysimplesoap.client import SoapClient
from pysimplesoap.server import SoapDispatcher, SOAPHandler


def random_string(N):
    return ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def generate_username():
    return random_string(5)

def generate_password():
    return random_string(6)

def generate_port(token):
    return 8100 + int(500 * random())

def generate_server_token():
    return random_string(10)

def generate_token(username, password, port):
    return str(username)+str(password)

def generate_port():
    return 7000 + int(1000 * random())

def start_server(hostname, port, dispatcher):
    httpd = HTTPServer((hostname, port), SOAPHandler)
    httpd.dispatcher = dispatcher
    print "Registring at %s " % (hostname + str(port))
    httpd.serve_forever()


def open_server_thread(hostname, port, dispatcher):
    thread = Thread(target=start_server, args=((hostname, port, dispatcher)))
    thread.start()
    return thread


def client(link):
    return SoapClient(location=link, action=link, soap_ns="soap", trace=False, ns=False)


def dispatcher(name, location):
    return SoapDispatcher(
        name=name,
        location=location,
        action=location,
        documentation="doc",
        trace=False,
        ns=False)
