import sys
import Queue

sys.path.append("..")
sys.path.append("../..")
import weather_forecaster
import timing_service
import holidays
import demand_service

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils

class price_calculator(service_interface):

    def __init__(self):
        service_interface.__init__(self)

    def price_calculation(self, supply, demand, location):
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

    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
        return {"errorcode": globalconf.SUCCESS_CODE}

    # Publish info
    def publish(self):
       while(True):
            try:
                event = self.q.get(timeout=5)
                event_id, user_token, service_token, add_info, reply_addr, client_message_id = event

                # check for repetition of messages
                if self.last_ids.__contains__(str(client_message_id)):
                    print "DUPLICATE"
                    return {"errorcode": globalconf.REPETITION_CODE}
                else:
                    # Add received msg ID to list of received messages
                    self.last_ids[user_token] = client_message_id

                # Check we got messages in order
                tempMsgId = self.last_ids[user_token]
                print "YOLO: " + tempMsgId
                if int(tempMsgId) + 1 == int(client_message_id):
                    self.last_ids[str(user_token)] = int(client_message_id)
                    print "OK - Messages received in order"
                # Out of order
                else:
                    print "ERROR - Messages received out of order"
                    return {"errorcode": globalconf.OUT_OF_ORDER_CODE}

                if add_info is not None:
                    message = "UT:%s, %s, %s" % (user_token, service_token, self.get_data(add_info))
                    # Return fulfilled request to client
                    utils.client(reply_addr).publish(service_token=service_token, user_token=user_token,
                                                     event_id=event_id, message=message,
                                                     client_message_id=client_message_id)
            except Queue.Empty:
                continue

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def get_connection(self):
        return self.client

    def get_demand(self):
        return self.q.queue.__sizeof__()

    def get_data(self, location):
        # Get supply and Demand from other component
        supply = demand_service.get_supply()
        demand = self.get_demand()
        return self.price_calculation(supply, demand, str(location))
        # return self.price_calculation(10, 12, "London")

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