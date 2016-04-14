import sys
sys.path.append("..")
sys.path.append("../..")

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils
import time
import Queue
from random import randint

class random_cat_fact_service(service_interface):

    def __init__(self):
        service_interface.__init__(self)
        self.server_thread = None
        self.list_of_cats = None

    def get_random_number(self):
        number = randint(1, 10)
        return number


    def initiate_connection(self, location):
        self.client = utils.client(location)


    def get_connection(self):
        return self.client


    def get_data(self):
        return self.list_of_cats


    def get_demand(self):
        return {"demand": int(self.q.qsize())}


    def setup_server(self):
        dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)
        dispatcher.register_function('parse_event',
                         lambda event_id, user_token, service_token, add_info, reply_addr, client_message_id
                         : self.parse_event(event_id, user_token, service_token, add_info, reply_addr, client_message_id),
                         args={"event_id": str, "user_token": str, "service_token": str, "add_info": str, "reply_addr": str,
                               "client_message_id": str},
                         returns={"errorcode": int}
                         )
        dispatcher.register_function('get_demand',
                         lambda: self.get_demand(),
                         args={},
                         returns={"demand": int}
                         )

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)


    def register(self):
        reply = self.client.register_publisher(service_name=self.service_name, port=self.port, tags=self.tags)
        self.token = reply.token


    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        time.sleep(5)
        server_client = utils.client(globalconf.hostname % 1237)
        number = self.get_random_number()
        print "Random cat fact event ", number
        response = server_client.get_Cats(number_of_cats=int(number))
        print response.list_of_cats
        s = response.list_of_cats
        self.list_of_cats = s
        self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
        return {"errorcode": globalconf.SUCCESS_CODE}


    def publish(self):
        """The publishing of the events from the queue to the load balancer"""
        while (True):
            try:
                event = self.q.get(timeout=10)
                event_id, user_token, service_token, add_info, reply_addr, client_message_id = event
                message = "UT:%s, %s, %s" % (user_token, service_token, self.get_data())
                utils.client(reply_addr).publish(service_token=service_token, user_token=user_token, event_id=event_id,
                                                 message=message, client_message_id=client_message_id)
            except Queue.Empty:
                continue

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

random_cat = random_cat_fact_service()
random_cat.port = utils.generate_port()
random_cat.tags = "cat,dog"

random_cat.initiate_connection(linker)
random_cat.setup_server()
random_cat.register()
random_cat.publish()