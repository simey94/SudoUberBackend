import sys
sys.path.append("..")
sys.path.append("../..")
import weather_forecaster
import timing_service
import holidays

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils

class price_calculator(service_interface):

    def __init__(self):
        service_interface.__init__(self)

    def price_calculation(self, demand, supply, location):
        journeyPrice = 1.00

        degreesC = weather_forecaster.get_degrees_c(location)
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

    def parse_event(self, event_id, user_token, service_token, add_info):
        # save request to queue
        self.q.queue.append(event_id)
        # perform price_calculation() on the event values
        demand = add_info[0]
        supply = add_info[1]
        location = add_info[2]
        self.price_calculation(self, demand, supply, location)
        # return fulfilled request back through server
        pc.register()
        pc.publish()

    # def publish(self, message, publisher_id):
    #     if message is not None:
    #         # Presuming messages are in format id:msg
    #         split_msg = message.split(':')
    #         msg_id = int(split_msg[0])
    #         contnet = str(split_msg[1])
    #     else:
    #         return ""
    #
    #     print "\n Recieved From Publisher: " , str(publisher_id), "Message: ", message
    #
    #      # check we got messages in order
    #     if self.last_ids[publisher_id] + 1 == int(msg_id):
    #         self.publish_q.put(publisher_id)
    #         self.publish_q.put_message(message)
    #         self.last_ids[publisher_id] = int(msg_id)
    #         return "OK"
    #
    #     # check for repetition of messages
    #     elif self.last_ids[publisher_id] == int(msg_id):
    #         return "DUPLICATE"
    #
    #     # Notify if messages are not in order, reject message
    #     else:
    #         return str(self.last_ids[publisher_id])

    def initiate_connection(self, location):
        self.client = utils.client(location)

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
pc.port = utils.generate_port()
pc.tags = "cat,dog"
pc.initiate_connection(linker)
pc.setup_server()
# pc.parse_event()
pc.register()
pc.publish()