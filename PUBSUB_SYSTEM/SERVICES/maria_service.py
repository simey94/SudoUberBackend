import sys
sys.path.append("..")
sys.path.append("../..")
import timing_service
import holidays

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils

class price_calculator(service_interface):

    def __init__(self):
        service_interface.__init__(self)
        self.server_thread = None


    def price_calculation(self, demand, supply, location):
        journeyPrice = 1.00

        degreesC = 12
        currentDateTime = timing_service.timing_pricing()
        us_holidays = holidays.UnitedStates()

        if currentDateTime.date() in us_holidays:
            journeyPrice *= 1.2
        if demand > supply:
            journeyPrice *= 1.2
        if degreesC > 15:
            journeyPrice *= 1.2
        elif degreesC > 20:
            journeyPrice *= 1.5

        return journeyPrice

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def setup_server(self):
        dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)
        dispatcher.register_function('parse_event',
                                     lambda event_id, user_token, service_token, add_info, reply_addr,
                                            client_message_id: self.parse_event(event_id, user_token, service_token,
                                                                                add_info, reply_addr,
                                                                                client_message_id),
                                     returns={"errorcode": int},
                                     args={"event_id": str, "user_token": str, "service_token": str, "add_info": str,
                                           "reply_addr": str, "client_message_id": str})

        dispatcher.register_function('get_demand',
                                     lambda: self.get_demand(),
                                     returns={"demand": int},
                                     args={}
                                     )
        dispatcher.register_function('blabla',
                                     lambda : self.enqueue_helper(),
                                     returns={"location": str},
                                     args={}
                                     )

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)


    def enqueue(self):
        # send location to the weather
        #dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)

        print self.service_name
        print self.port
        print "ENQUEUE"


    def enqueue_helper(self):
        print "In new eqneue"
        return {"location": "Moscow"}

    def dequeue(self):
        # receive degrees back
        print "DEQUEUE"
        pass

    def get_connection(self):
        return self.client

    def get_data(self):
        return self.price_calculation(10, 12, "London")

    def recover_message(self):
        pass

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

pc = price_calculator()
pc.port = 5000
pc.tags = "cat,dog"
pc.initiate_connection(linker)
#HERE
#pc.enqueue()
pc.setup_server()
pc.register()

pc.publish()
