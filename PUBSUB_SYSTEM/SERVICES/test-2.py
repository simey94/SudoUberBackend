import sys
sys.path.append("..")
sys.path.append("../..")
import global_utils as utils
import global_configuration as globalconf
from pywwo import *
import time

def get_degrees_c(location):
    setKey('<45a7v53q9qaveabsekth9ucc>', 'free')
    w = LocalWeather(location)
    return w.data.current_condition.temp_C

def yo():
    return {"temperature" : int(1)}


dispatcher = utils.dispatcher("bye", globalconf.hostname % 6000)

dispatcher.register_function('get_calculation', lambda : yo(),
                               returns={"temperature" : int},
                               args={})

print ("Starting server...")
utils.open_server_thread(globalconf.http_hostname, 6000, dispatcher)

client = utils.client(globalconf.hostname % 5000)
response = client.get_city(port_number=int(6000))
print response.location
calculation = get_degrees_c(response.location)
print calculation



