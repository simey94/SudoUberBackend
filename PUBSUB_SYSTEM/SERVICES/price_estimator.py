# import holidays

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
pc.register()
pc.publish()
