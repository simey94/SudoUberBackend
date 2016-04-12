"""Class that is used as a Load Balancer"""
import sys
sys.path.append("../..")
sys.path.append("..")
import Queue

import global_utils as utils
from pysimplesoap.server import SoapDispatcher, SOAPHandler
import global_configuration as globalconf
from threading import Thread, Lock
import time

subscribers = {}  # user_token -> client
publishers = {} # service_token -> (service_token, client, service_link)

events = Queue.Queue()
publish_lock = 0

def start_service_sync(sync_token):
    global publish_lock
    if publish_lock != 0:
        return {"errorcode": globalconf.ERROR_CODE}
    publish_lock = sync_token
    print "START SERVICE SYNC"
    return {"errorcode": globalconf.SUCCESS_CODE}

def sync_service(sync_token, nonce, service_token, service_link):
    global publish_lock, publishers

    if publish_lock != sync_token:
        return {"errorcode": globalconf.ERROR_CODE}

    publishers[service_token] = (service_token, utils.client(service_link), service_link)

    return {"errorcode": globalconf.SUCCESS_CODE}

def end_service_sync(sync_token):
    global publish_lock

    if publish_lock != 0:
        return {"errorcode": globalconf.ERROR_CODE}
    publish_lock = 0
    print "END SERVICE SYNC"
    return {"errorcode": globalconf.SUCCESS_CODE}

def request_services(user_token):
    global publishers

    # msg = ",".join(["(" + str(publishers[x][0]) + "|" + str(publishers[x][2]) + ")" for x in publishers])
    msg = str(publishers)
    return {"services": msg}

def service(user_token, service_token, additional_info):
    events.put((user_token, service_token, additional_info))

def notify(user_token, hostname):
    subscribers[user_token] = (user_token, utils.client(hostname), hostname)
    return {"errorcode":globalconf.SUCCESS_CODE}

def publish(service_token, message):
    print "[", service_token, "]", message

    for user in subscribers:
        subscribers[user].receive(message=message)

    return {"errorcode": globalconf.SUCCESS_CODE}

def process_events():

    while True:
        if publish_lock != 0:
            continue
        try:
            user_token, service_token, add_info = events.get(timeout=5)
            publishers[service_token][1].parse_event(user_token=user_token, service_token=service_token, add_info=add_info)
        except Queue.Empty:
            continue


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
                             args={"service_token": str, "event_id": str, "message": str})


dispatcher.register_function('notify', notify,
                             returns={"errorcode": int},
                             args={"user_token": str, "hostname": str})

dispatcher.register_function('start_service_sync', start_service_sync,
                             returns={"errorcode": int},
                             args={"sync_token": str})

dispatcher.register_function('sync_service', sync_service,
                             returns={"errorcode": int},
                             args={"sync_token":str, "nonce": str, "service_token": str, "service_link": str})

dispatcher.register_function('end_service_sync', end_service_sync,
                             returns={"errorcode": int},
                             args={"sync_token": str})

server_thread = utils.open_server_thread(globalconf.http_hostname, port, dispatcher)

Thread(target=process_events).start()