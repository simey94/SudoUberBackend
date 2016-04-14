"""File contains the code to run the server"""
import sys

sys.path.append("../..")
sys.path.append("..")

import global_configuration as globalconf
import global_utils as utils
from collections import defaultdict
from subprocess import Popen
from collections import defaultdict
from threading import Thread
import time

servers = {}  # lb_token -> (client, link)
publishers = {}  # service_token -> (name, client, link)

servers_allocations = defaultdict(int)  # lb_token -> number of clients allocated

def register_publisher(service_name, port, tags):
    """
    Handle the requests from publishers to the register.
    :param service_name: name of the service
    :param port: the port
    :param tags: tags of the services
    :return: ack
    """
    token = utils.generate_token(service_name, service_name, port)

    client = utils.client(globalconf.hostname % str(port))

    publishers[token] = (token, service_name, client, globalconf.hostname % str(port))

    Thread(target=sync_services).start()

    return {"token": token, "errorcode": globalconf.SUCCESS_CODE}


def spawn_lb(token):
    """Spawn a load balancer class"""
    fport = utils.generate_port()
    Popen([globalconf.runner, globalconf.file_loadbalancer, token, str(fport)])

    link = globalconf.hostname % fport
    client = utils.client(link)

    servers[token] = (client, link)
    servers_allocations[token] = 0

def alloc_server():
    """Allocates a new load balancer"""
    chosen_serv = None

    for server_token in servers:
        if servers_allocations[server_token] < globalconf.connection_threashold:
            chosen_serv = server_token
            break

    if chosen_serv is None:
        server_token = utils.generate_server_token()
        spawn_lb(server_token)
        chosen_serv = server_token
        Thread(target=sync_service, args=(server_token, )).start()

    servers_allocations[server_token]+=1

    return chosen_serv

def sync_services():
    for server in servers:
        sync_service(server)

def sync_service(server_token):
    time.sleep(1)

    sync_token = utils.generate_server_token()
    i = 0
    server_client = servers[server_token][0]

    server_client.start_service_sync(sync_token=sync_token)
    for service in publishers:
        service_token, service_name, _, service_link = publishers[service]
        server_client.sync_service(sync_token=sync_token, nonce=str(i), service_token=service_token, service_link=service_link, service_name=service_name)
        i+=1
    server_client.end_service_sync(sync_token=sync_token)

def subscribe(username, password, port):
    """
    Subscribe to the server.
    :param username: username
    :param password: password
    :param port: port
    :return: token and the server
    """
    token = utils.generate_token(username, password, port)

    server_token = alloc_server()
    #print "Allocated %s(user) to %s(server)" % (username, server_token)

    return {"token": token, "server": servers[server_token][1]}

def sync_daemon():
    while(True):
        time.sleep(10)
        sync_services()

dispatcher = utils.dispatcher("Main server", globalconf.location)
dispatcher.register_function('subscribe', subscribe,
                             returns={"token": str, "server": str},
                             args={"username": str, "password": str, "port": str})

dispatcher.register_function('register_publisher', register_publisher,
                             returns={"errorcode": int, "token": str},
                             args={"service_name": str, "port": str, "tags": str})


# print "Running the server at %s:%s" % (globalconf.http_hostname, globalconf.s_port)

Thread(target=sync_daemon).start()

thread = utils.open_server_thread(globalconf.http_hostname, globalconf.s_port, dispatcher)
thread.join()
