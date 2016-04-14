import sys
sys.path.append("..")
sys.path.append("../..")

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils

class price_calculator(service_interface):

    def __init__(self):
        service_interface.__init__(self)

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def get_connection(self):
        return self.client

    def get_data(self):
        return "I AM A CAT"

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
