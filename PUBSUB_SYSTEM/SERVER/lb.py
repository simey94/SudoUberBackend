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
from collections import defaultdict
from random import randint

subscribers = {}  # user_token -> (user_token, utils.client(hostname), hostname)
publishers = {} # service_token -> (service_token, service_name, client, service_link)
subscribers_last_message_id = defaultdict(int) # user_token -> last id
subscribers_last_event_id = defaultdict(int) # user_token -> last generated event id

processing_messages = defaultdict(dict) # user_token -> event_id -> tuple
name_publisher = defaultdict(list)

current_recovery = defaultdict(Lock) # user_token -> Lock

events = Queue.Queue() # (user_token, service_token, add_info)
reply_events = Queue.Queue() # (user_token, service_token, event_id, message)

publish_lock = 0

def start_service_sync(sync_token):
    global publish_lock
    if publish_lock != 0:
        return {"errorcode": globalconf.ERROR_CODE}
    publish_lock = sync_token

    name_publisher.clear()

    return {"errorcode": globalconf.SUCCESS_CODE}

def sync_service(sync_token, nonce, service_token, service_link, service_name):
    global publish_lock, publishers

    if publish_lock != sync_token:
        return {"errorcode": globalconf.ERROR_CODE}

    publishers[service_token] = (service_name, service_token, utils.client(service_link), service_link)

    name_publisher[service_name].append(service_token)

    return {"errorcode": globalconf.SUCCESS_CODE}

def end_service_sync(sync_token):
    global publish_lock

    if publish_lock != sync_token:
        return {"errorcode": globalconf.ERROR_CODE}

    publish_lock = 0
    return {"errorcode": globalconf.SUCCESS_CODE}

def request_services(user_token):
    global publishers

    msg = ",".join([ str(publishers[x][0]) for x in publishers])
    return {"services": msg}

def service(client_message_id, user_token, service_token, additional_info):

    if (subscribers_last_message_id[user_token] + 1) != client_message_id:
        print "Wrong client_id"
        return {"errorcode": globalconf.REPETITION_CODE, "message_id": subscribers_last_message_id[user_token] + 1}

    events.put(
        (
            user_token,
            service_token,
            additional_info,
            client_message_id
        )
    )

    subscribers_last_message_id[user_token] += 1
    return {"errorcode": globalconf.SUCCESS_CODE, "message_id": subscribers_last_message_id[user_token]}

def notify(user_token, hostname):
    subscribers[user_token] = (
        user_token,
        utils.client(hostname),
        hostname
    )
    return {"errorcode":globalconf.SUCCESS_CODE}


def publish(service_token, user_token, event_id, message):
    reply_events.put(
        (
            user_token,
            service_token,
            event_id,
            message
        )
    )
    return {"errorcode": globalconf.SUCCESS_CODE}


def pick_service(service_name):
    if service_name not in name_publisher:
        return None
    else:
        services = name_publisher[service_name][:]
        if len(services) == 0:
            return None
        elif len(services) == 1:
            return services[0]
        else:
            services.sort(key=lambda service_token: int(publishers[service_token][2].get_demand().demand))
            return services[0]

def recover(user_token, service_name, add_info, client_message_id):
    global events

    events.put((user_token, service_name, add_info, client_message_id))

def event_recovery():
    global processing_messages, current_recovery

    while(True):
        time.sleep(globalconf.event_recovery_sleep_time)
        now = time.time()
        for user_token in processing_messages:
            current_recovery[user_token].acquire()
            for event_id in processing_messages[user_token]:
                message = processing_messages[user_token][event_id]
                if (now-message[4]) > globalconf.event_recovery_threashold:
                    user_token, service_name, add_info, client_message_id, _ = message
                    del processing_messages[user_token][event_id]
                    recover(user_token, service_name, add_info, client_message_id)
                    break
            current_recovery[user_token].release()

def process_events():
    global processing_messages, subscribers_last_event_id, events

    while True:
        if publish_lock != 0:
            continue
        try:
            user_token, service_name, add_info, client_message_id = events.get(timeout=5)
            service_token = pick_service(service_name)
            if service_token is None:
                print "NOT FOUND SERVICE"
                continue

            event_id = subscribers_last_event_id[user_token]
            subscribers_last_event_id[user_token] += 1

            processing_messages[str(user_token)][str(event_id)] = (
                user_token,
                service_name,
                add_info,
                client_message_id,
                time.time()
            )

            print "Enqueueing %s(event) to %s->%s(Service Name)" % (event_id, service_token, service_name)
            publishers[service_token][2].parse_event(
                event_id=event_id,
                user_token=user_token,
                service_token=service_token,
                add_info=add_info,
                reply_addr=(globalconf.hostname % port)
            )
        except Queue.Empty:
            continue

def reply_to_events():
    global processing_messages, reply_events, subscribers, current_recovery

    while True:
        try:
            user_token, service_token, event_id, message = reply_events.get(timeout=5)

            user_token = str(user_token)
            service_token = str(service_token)
            event_id = str(event_id)
            message = str(message)

            if event_id not in processing_messages[user_token]:
                print "Message replay"
                continue

            current_recovery[user_token].acquire()
            del processing_messages[user_token][event_id]
            print "Replying[%s] to %s(user) with %s(msg) from %s(service)" % (event_id, user_token, message, service_token)
            current_recovery[user_token].release()
            subscribers[user_token][1].receive(message=message)
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
                             args={"service_token": str, "user_token": str, "event_id": str, "message": str})

dispatcher.register_function('service', service,
                             returns={"errorcode": int, "message_id":int},
                             args={"client_message_id": int, "service_token": str, "user_token": str, "additional_info": str})

dispatcher.register_function('notify', notify,
                             returns={"errorcode": int},
                             args={"user_token": str, "hostname": str})

dispatcher.register_function('start_service_sync', start_service_sync,
                             returns={"errorcode": int},
                             args={"sync_token": str})

dispatcher.register_function('sync_service', sync_service,
                             returns={"errorcode": int},
                             args={"sync_token":str, "nonce": str, "service_token": str, "service_link": str, "service_name": str})

dispatcher.register_function('end_service_sync', end_service_sync,
                             returns={"errorcode": int},
                             args={"sync_token": str})

server_thread = utils.open_server_thread(globalconf.http_hostname, port, dispatcher)

Thread(target=process_events).start()
Thread(target=reply_to_events).start()
Thread(target=event_recovery).start()
