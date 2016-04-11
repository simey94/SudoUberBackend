"""File contains the code to run the server"""
import sys

sys.path.append("../..")
sys.path.append("..")

import configuration as localconf
import global_configuration as globalconf
import global_utils as utils
from collections import defaultdict
from subprocess import Popen
from collections import defaultdict

servers = {}  # lb_token -> (client, link)
servers_allocations = defaultdict(int)  # lb_token -> number of clients allocated


def spawn_lb(token):
    """Spawn a load balancer class"""
    fport = utils.generate_port()
    Popen([globalconf.runner, globalconf.file_loadbalancer, token, str(fport)])

    link = globalconf.hostname % fport
    client = utils.client(link)

    servers[token] = (client, link)
    servers_allocations[token] = 0


def alloc_server():
    chosen_serv = None

    for server_token in servers:
        if servers_allocations[server_token] < globalconf.connection_threashold:
            chosen_serv = server_token
            break

    if chosen_serv is None:
        server_token = utils.generate_server_token()
        spawn_lb(server_token)
        chosen_serv = server_token

    servers_allocations[server_token]+=1

    return chosen_serv


def subscribe(username, password, port):
    token = utils.generate_token(username, password, port)

    # client = utils.client(globalconf.hostname % str(port))
    # subscribers[token] = client

    server_token = alloc_server()

    return {"token": token, "server": servers[server_token][1]}


dispatcher = utils.dispatcher("Main server", globalconf.location)
dispatcher.register_function('subscribe', subscribe,
                             returns={"token": str, "server": str},
                             args={"username": str, "password": str, "port": str})


print "Running the server at %s:%s" % (globalconf.http_hostname, globalconf.s_port)

thread = utils.open_server_thread(globalconf.http_hostname, globalconf.s_port, dispatcher)

thread.join()
