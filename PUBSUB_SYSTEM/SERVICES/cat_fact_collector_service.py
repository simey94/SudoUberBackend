import sys
sys.path.append("../..")
sys.path.append("..")

import requests
import json
from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils


class cat_fact_collector_service(service_interface):
    def __init__(self):
        service_interface.__init__(self)
        self.server_thread = None
        self.list_of_cats = None

    def find_cat_facts(self, no_of_facts):
        url = "http://catfacts-api.appspot.com/api/facts?number="
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            from BeautifulSoup import BeautifulSoup
        url += str(no_of_facts)
        print url
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html)
        catFacts = json.loads(str(soup))
        s = ""
        for item in catFacts["facts"]:
            s += str(item)
            s += " "
        return s

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def get_connection(self):
        return self.client

    def setup_server(self):
        dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)
        dispatcher.register_function('parse_event',
                                     lambda event_id, user_token, service_token, add_info, reply_addr,
                                            client_message_id: self.parse_event(event_id, user_token, service_token,
                                                                                add_info, reply_addr,
                                                                                client_message_id),
                                     returns={"errorcode": int},
                                     args={"event_id": str, "user_token": str, "service_token": str, "add_info": str,
                                           "reply_addr": str, "client_message_id": str})

        dispatcher.register_function('get_demand',
                                     lambda: self.get_demand(),
                                     returns={"demand": int},
                                     args={}
                                     )

        dispatcher.register_function('get_Cats',
                                     lambda number_of_cats: self.find_cat_facts(number_of_cats),
                                     returns={"list_of_cats": str},
                                     args={"number_of_cats": int}
                                     )

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)

    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        if not self.isBlank(add_info) :
            print "Cat fact parser event", add_info
            try:
                random = int(add_info) + 1
                self.list_of_cats = self.find_cat_facts(int(add_info))
            except TypeError:
                s = "ERROR, data must be a number but was " + add_info
                self.list_of_cats = s
        self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
        return {"errorcode": globalconf.SUCCESS_CODE}

    def get_data(self):
        return self.list_of_cats

    def recover_message(self):
        pass

    def isBlank(self, myString):
        if myString and myString.strip():
            return False
        return True

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

cat_fact = cat_fact_collector_service()
cat_fact.port = 1237
cat_fact.tags = "cat,dog"
cat_fact.initiate_connection(linker)
cat_fact.setup_server()
cat_fact.register()
cat_fact.publish()