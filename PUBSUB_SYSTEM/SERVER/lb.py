"""Class that is used as a Load Balancer"""
import sys
sys.path.append("..")
sys.path.append("../..")

import global_utils as utils
from pysimplesoap.server import SoapDispatcher, SOAPHandler
import global_configuration as globalconf

subscribers = {}  # user_token -> client
publishers = {}  # service_token -> client

def request_services(user_token):
    return {"services": "NON"}

def register_publisher(service_name, port, tags):
    token = utils.generate_token(service_name, service_name, port)

    client = utils.client(globalconf.hostname % str(port))

    publishers[token] = client
    return {"token": token, "errorcode": globalconf.SUCCESS_CODE}

def notify(user_token, hostname):
    subscribers[user_token] = utils.client(hostname)
    return {"errorcode":globalconf.SUCCESS_CODE}

def publish(service_token, message):
    print "[", service_token, "]", message

    for user in subscribers:
        subscribers[user].receive(message=message)

    return {"errorcode": globalconf.SUCCESS_CODE}

if len(sys.argv) < 2:
    port = utils.generate_port()
    query = utils.generate_server_token()
else:
    query = sys.argv[1]
    port = int(sys.argv[2])

dispatcher = utils.dispatcher("Lb:%s,%s" % (port, query), globalconf.hostname % port)
dispatcher.register_function('request_services', request_services, returns={"services":str}, args={"user_token": str})

dispatcher.register_function('publish', publish,
                             returns={"errorcode": int},
                             args={"service_token": str, "message": str})

dispatcher.register_function('register_publisher', register_publisher,
                             returns={"errorcode": int, "token": str},
                             args={"service_name": str, "port": str, "tags": str})

dispatcher.register_function('notify', notify,
                             returns={"errorcode": int},
                             args={"user_token": str, "hostname": str})

server_thread = utils.open_server_thread(globalconf.http_hostname, port, dispatcher)