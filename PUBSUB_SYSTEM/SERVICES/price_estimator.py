import holidays
import weather_forecaster
import timing_service
from PUBSUB_SYSTEM.SERVICES.service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils


class price_calculator(service_interface):

    def __init__(self):
        service_interface.__init__()

    def price_calculation(demand, supply, location):
        journeyPrice = 1.00  # £1 per mile

        # Get pricing formulae components from other services
        degreesC = weather_forecaster.get_degrees_c(location)
        currentDateTime = timing_service.timing_pricing()
        us_holidays = holidays.UnitedStates()  # package is lame and doesn't do UK

        if currentDateTime.date() in us_holidays:
            journeyPrice *= 1.2
        if demand > supply:
            journeyPrice *= 1.2
        if degreesC > 15:
            journeyPrice *= 1.2
        elif degreesC > 20:
            journeyPrice *= 1.5

        return journeyPrice

    def initiate_connection(self):
        """returns a client conenction to the server   """
        self.client = utils.client(globalconf.location)

    def get_connection(self):
        """returns a connection to the server  for the client passed int  """
        return self.client

    def get_data(self):
        """returns data that is to be published """
        return price_calculator(10, 12, "London")

    def recover_message(self):
        """ recovers messages that may be lost from queue """
        pass


pc = price_calculator()
pc.register()

pc.publish()