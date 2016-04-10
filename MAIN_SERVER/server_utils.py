"""Utilities by the server"""

import random


def generate_port(token):
    return 8000 + int(50 * random.random())


def generate_token():
    return random.random()
