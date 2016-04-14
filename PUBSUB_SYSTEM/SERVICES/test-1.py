import sys
sys.path.append("..")
sys.path.append("../..")
import global_utils as utils
import global_configuration as globalconf


def get_city(port_number):
    print port_number
    return {"location": "Moscow"}


port = 5000
dispatcher = utils.dispatcher("hello", globalconf.hostname % port)

dispatcher.register_function('get_city', lambda port_number: get_city(port_number),
                             returns={"location" : str},
                             args={"port_number": int})

print ("Starting server...")
thread = utils.open_server_thread(globalconf.http_hostname, port, dispatcher)

client = utils.client(globalconf.hostname % 9000)
response = client.get_calculation()
print client



