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
        self.current_temperature = None
        self.recieved_msg_ids = []

    def get_T(self, location):
        print "Getting...", location
        setKey('<45a7v53q9qaveabsekth9ucc>', 'free')
        w = LocalWeather(location)
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

        dispatcher.register_function('get_T',
                                     lambda location: self.get_T(location),
                                     returns={"temperature": int},
                                     args={"location": str}
                                     )

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)

    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        if (self.recieved_msg_ids).__contains__(client_message_id):
            print "DUPLICATE MSG Recieved"
            return {"errorcode": globalconf.SUCCESS_CODE}
        else:
            print "Weather parser event", add_info
            t = self.get_T(str(add_info))
            print "Temperature in %s : %s" % (add_info, t)
            self.current_temperature = int(t)
            self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
            return {"errorcode": globalconf.SUCCESS_CODE}

    def get_data(self):
        return self.current_temperature

    def recover_message(self):
        pass

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

pc = weather_forecaster()
pc.port = 5000
pc.tags = "cat,dog"
pc.initiate_connection(linker)
pc.setup_server()
pc.register()
pc.publish()