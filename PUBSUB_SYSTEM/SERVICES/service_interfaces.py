import sys
sys.path.append("../..")
sys.path.append("..")

import global_configuration as globalconf
import global_utils as utils
import os
import time
import Queue

class service_interface:

    def __init__(self):
        self.client = None
        self.token  = None
        self.service_name = "haha"#utils.generate_server_token()
        self.port = None
        self.tags = ""
        self.q = Queue.Queue()
        self.publish_q = Queue.Queue()
        self.last_ids = {}     # Dictionary of user_id -> last message id from a client
        self.received_message_ids = [] # List of all recieved client ID messages
        self.server_thread = None

    # Ping the service to find if it is still alive
    def ping_service(hostname):
        response = os.system("ping -c 1 " + hostname)

        if response == 0:
            print hostname, 'is up!'
            return True
        else:
            print hostname, 'is down!'
            return False

    def initiate_connection(self, location):
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

    def setup_server(self):
        dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)
        dispatcher.register_function('parse_event',
                                     lambda event_id, user_token, service_token, add_info, reply_addr, client_message_id: self.parse_event(event_id, user_token, service_token, add_info, reply_addr, client_message_id),
                                     returns={"errorcode": int},
                                     args={"event_id": str, "user_token": str, "service_token": str, "add_info": str, "reply_addr": str, "client_message_id": str})

        dispatcher.register_function('get_demand',
                                     lambda : self.get_demand(),
                                     returns={"demand": int},
                                     args={}
                                     )

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)

    def get_demand(self):
        return {"demand": int(self.q.qsize())}

    def register(self):
        reply = self.client.register_publisher(service_name = self.service_name, port = self.port, tags = self.tags)
        self.token = reply.token

    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
        return {"errorcode":globalconf.SUCCESS_CODE}

    # Publish info
    def publish(self):
       while(True):
            try:
                event = self.q.get(timeout=5)
                event_id, user_token, service_token, add_info, reply_addr, client_message_id = event
                message = "UT:%s, %s, %s" % (user_token, service_token, self.get_data())
                utils.client(reply_addr).publish(service_token=service_token, user_token=user_token, event_id=event_id, message=message, client_message_id=client_message_id)
            except Queue.Empty:
                continue