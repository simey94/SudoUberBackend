import sys
sys.path.append("..")

import logging

from pysimplesoap.client import SoapClient, SoapFault
import configuration as conf
import time

logging.basicConfig(level=logging.INFO)

class Client:
    """Client representation"""

    def __init__(self, username, password, client):
        """The username for the client """
        self._username = username

        """The password for the client"""
        self._password = password

        """Client handle"""
        self._client = client

        """Id of the user"""
        self._id = None

        self._log = logging.getLogger(__name__)
        self._log.setLevel(conf.log_level)

        self._log.debug("Created the a client with [%s, %s]" % (self._username,
            self._password))

    def connect(self):
        """Connect to the client"""
        if self._client is None:
            return
        response =self._client.subscribe(username=self._username,password=self._password)
        self._id = response.subscriber_id
        self._log.debug("Got the following id assigned:[%s]" % self._id)

    def poll_forever(self, interval):
        """Make the client to poll forever"""

        if self._client is None:
            return

        while(True):
            response = self._client.poll(token=self._id)
            reply = response.data

            print reply
            time.sleep(interval)

client = SoapClient(
        location="http://localhost:8008",
        action="http://localhost:8008",
        soap_ns="soap",
        trace=False,
        ns=False)

if client is not None:
    c = Client("username", "password", client)

    c.connect()
    c.poll_forever(conf.pollInterval)

