"""Utilities by the server"""

import random
import string
from pysimplesoap.client import SoapClient


def random_string(N):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def generate_username():
    return random_string(5)

def generate_password():
    return random_string(6)

def generate_port(token):
    return 8000 + int(50 * random.random())

def generate_token():
    return random.random()

def generate_token(username, password, port):
    return str(username)+str(password)+str(port)

def generate_port():
    return 7000 + int(1000 * random.random())

def client(link):
    return SoapClient(location=link, action=link, soap_ns="soap", trace=True, ns=False)

