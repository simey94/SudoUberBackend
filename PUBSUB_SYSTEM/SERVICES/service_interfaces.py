import os
import time


class service_interface:

    def __init__(self):
        self.client = None
        self.token  = None
        self.service_name = "CAT"
        self.port = None
        self.tags = ""

    # Ping the service to find if it is still alive
    def ping_service(hostname):
        response = os.system("ping -c 1 " + hostname)

        if response == 0:
            print hostname, 'is up!'
            return True
        else:
            print hostname, 'is down!'
            return False

    def initiate_connection(self):
        """returns a client conenction to the server   """
        pass

    def get_connection(self):
        """returns a connection to the server  for the client passed int  """
        pass

    def get_data(self):
        """returns data that is to be published """
        pass

    def recover_message(self):
        """ recovers messages that may be lost from queue """
        pass

    def register(self):
        reply = self.client.register_publisher(service_name = self.service_name, port = self.port, tags = self.tags)
        self.token = reply.token

    # Publish info
    def publish(self):
       while(True):
            # wait 10 seconds before publishing
            time.sleep(10)
            # publish to server
            connection = object.get_connection()
            reply = connection.publish(service_token=self.token, message=object.getData())