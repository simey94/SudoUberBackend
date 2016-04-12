import sys
sys.path.append("../..")
sys.path.append("..")

import global_configuration as globalconf
import os
import time

class service_interface:

    def __init__(self):
        self.client = None
        self.token  = None
        self.last_ids = None
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
       # if message is not None:
       #     # Presuming messages are in format id:msg
       #     split_msg = message.split(':')
       #     msg_id = int(split_msg[0])
       #     contnet = str(split_msg[1])
       # else:
       #     return ""
       #
       #  print "\n Recieved From Publisher: " , str(publisher_id), "Message: ", message
       #
       #  # check we got messages in order
       # if self.last_ids[publisher_id] + 1 == int(msg_id):
       #     pub_queue = publishers_queues[publisher_id]
       #     pub_queue.put_message(message)
       #     self.last_ids[publisher_id] = int(msg_id)
       #     return "OK"
       #
       # # check for repetition of messages
       # elif self.last_ids[publisher_id] == int(msg_id):
       #     return "DUPLICATE"
       #
       # # Notify if messages are not in order, reject message
       # else:
       #     return str(self.last_ids[publisher_id])

       while(True):
            # wait 10 seconds before publishing
            time.sleep(globalconf.publish_interval)
            # publish to server
            connection = self.get_connection()
            reply = connection.publish(service_token=self.token, message=self.get_data())