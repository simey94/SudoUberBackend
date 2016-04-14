import subprocess
import sys
sys.path.append("..")
sys.path.append("../..")
import timing_service
import holidays

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils
import time

class price_calculator(service_interface):

    def __init__(self):
        service_interface.__init__(self)
        self.server_thread = None
        self.current_temperature = None
        self.recieved_msg_ids = []


    def price_calculation(self, demand, supply):
        journeyPrice = 1.00

        degreesC = self.current_temperature
        currentDateTime = timing_service.timing_pricing()
        us_holidays = holidays.UnitedStates()

        if currentDateTime.date() in us_holidays:
            journeyPrice *= 1.5
        if demand > supply:
            journeyPrice *= 1.6
        if degreesC > 15:
            journeyPrice *= 1.7
        elif degreesC > 20:
            journeyPrice *= 1.8

        return journeyPrice

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def register(self):
        reply = self.client.register_publisher(service_name=self.service_name, port=self.port, tags=self.tags)
        self.token = reply.token

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

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)

    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        if(self.recieved_msg_ids).__contains__(client_message_id):
            print "DUPLICATE MSG Recieved"
            return {"errorcode": globalconf.SUCCESS_CODE}
        else:
            time.sleep(5)
            print "Price parser event", add_info
            client1 = utils.client(globalconf.hostname % 5000)
            # If weather is up
            weather_host = globalconf.hostname % 5000
            print "====== weather host: " + weather_host
            if self.ping_service(weather_host):
                response = client1.get_T(location=str(add_info))
                print "Temperature in %s : %s" % (add_info, response.temperature)
                self.current_temperature = int(response.temperature)
                self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
                return {"errorcode": globalconf.SUCCESS_CODE}

            # Else open a sub process and create weather instance
            else:
                print "Weather is down: Calling sub process"
                subprocess.call(['python', 'weather_forecaster.py'])
                print "Sub process called"
                response = client1.get_T(location=str(add_info))
                print "Temperature in %s : %s" % (add_info, response.temperature)
                self.current_temperature = int(response.temperature)
                self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
                return {"errorcode": globalconf.SUCCESS_CODE}

    def get_connection(self):
        return self.client

    def get_data(self):
        return self.price_calculation(10, 12)

    def recover_message(self):
        pass

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

pc = price_calculator()
pc.port = utils.generate_port()
pc.tags = "cat,dog"
pc.initiate_connection(linker)

pc.setup_server()
pc.register()
pc.publish()

