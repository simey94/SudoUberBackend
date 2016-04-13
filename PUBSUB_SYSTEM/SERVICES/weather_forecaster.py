import sys
sys.path.append("../..")

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils


from pywwo import *


class weather_forecaster(service_interface):

    def __init__(self):
        service_interface.__init__(self)
        self.server_thread = None

    def get_degrees_c(self, location):
        setKey('<45a7v53q9qaveabsekth9ucc>', 'free')
        w = LocalWeather(location)
        # print w.data.current_condition.temp_C
        return w.data.current_condition.temp_C


    def initiate_connection(self, location):
        self.client = utils.client(location)

    def get_connection(self):
        return self.client

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


        client1 = utils.client(globalconf.hostname % 5000)
        response = client1.blabla()
        print response.location
        yo = self.get_degrees_c(response.location)
        print yo

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)

    def enqueue(self):
        # use a global variable to go to getDegress and return int
        print "ENQUEUE"
        pass

    def dequeue(self):
        # extract the city location to a global variable


        #dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)
        #dispatcher.register_function('dequeue', self.enqueue_helper(), returns={"location": str})
        print "DEQUEUE"
        pass

    def get_data(self):
        return self.get_degrees_c("Moscow")

    def recover_message(self):
        pass

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

pc = weather_forecaster()
pc.port = utils.generate_port()
pc.tags = "cat,dog"
pc.initiate_connection(linker)
pc.setup_server()
pc.register()
pc.publish()