import sys
sys.path.append("../..")
sys.path.append("..")

import requests
import json
from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils
import Queue
from termcolor import colored

class cat_fact_collector_service(service_interface):
    def __init__(self):
        service_interface.__init__(self)
        self.server_thread = None
        self.list_of_cats = None

    def find_cat_facts(self, no_of_facts):
        if 1 <= no_of_facts <= 100:
            url = "http://catfacts-api.appspot.com/api/facts?number="
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                from BeautifulSoup import BeautifulSoup
            url += str(no_of_facts)
            print url
            try:
                response = requests.get(url)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                   print colored('API Error: catches the HTTP Error, something went wrong', 'red')
                   return "API Error: catches the HTTP Error, something went wrong"
            except requests.exceptions.RequestException:
                print colored('API Error: could not find the cat facts', 'red')
                return "API Error: catches the Request Exception, something went wrong"

            html = response.content
            soup = BeautifulSoup(html)
            try:
                catFacts = json.loads(str(soup))
                s = ""
                for item in catFacts["facts"]:
                    s += item.encode('ascii', 'ignore')
                    s += " "
                if not self.isBlank(s):
                    return s
                else:
                    print colored('Error: the facts were empty or could not encode into the ascii format ', 'red')
                    return "Error, the facts were empty"
            except ValueError, e:
                print colored('API Error: could not find the cat facts', 'red')
                return "API Error: could not find the cat facts"

        else:
            print colored('Error: number of cats should be in the range [1, 100]', 'red')
            return "Error, number of cats should be in the range [1, 100] "

    def isBlank(self, myString):
        if myString and myString.strip():
            return False
        return True


    def initiate_connection(self, location):
        self.client = utils.client(location)


    def get_connection(self):
        return self.client


    def get_data(self):
        return self.list_of_cats


    def get_demand(self):
        return {"demand": int(self.q.qsize())}


    def setup_server(self):
        dispatcher = utils.dispatcher("%s:%s" % (self.service_name, self.port), globalconf.hostname % self.port)
        dispatcher.register_function('parse_event',
                                     lambda event_id, user_token, service_token, add_info, reply_addr, client_message_id
                                     : self.parse_event(event_id, user_token, service_token, add_info, reply_addr,
                                                        client_message_id),
                                     args={"event_id": str, "user_token": str, "service_token": str, "add_info": str,
                                           "reply_addr": str,
                                           "client_message_id": str},
                                     returns={"errorcode": int}
                                     )
        dispatcher.register_function('get_demand',
                                     lambda: self.get_demand(),
                                     args={},
                                     returns={"demand": int}
                                     )

        dispatcher.register_function('get_Cats',
                                     lambda number_of_cats: self.find_cat_facts(number_of_cats),
                                     returns={"list_of_cats": str},
                                     args={"number_of_cats": int}
                                     )

        self.server_thread = utils.open_server_thread(globalconf.http_hostname, self.port, dispatcher)


    def register(self):
        reply = self.client.register_publisher(service_name=self.service_name, port=self.port, tags=self.tags)
        self.token = reply.token


    def parse_event(self, event_id, user_token, service_token, add_info, reply_addr, client_message_id):
        if not self.isBlank(add_info):
            print "Cat fact parser event", add_info
            try:
                a = int(add_info)
                if isinstance(int(add_info), int):
                    self.list_of_cats = self.find_cat_facts(int(add_info))
            except ValueError:
                print colored('Error: data must be a number but was', 'red'), colored(add_info, 'green')
                s = "Error: data must be a number but was " + add_info
                self.list_of_cats = s
        else:
            print colored('Error: client is not sending any', 'red'), colored('add_info', 'green')
            self.list_of_cats = "Error: client is not sending any add_info"
        self.q.put((event_id, user_token, service_token, add_info, reply_addr, client_message_id))
        return {"errorcode": globalconf.SUCCESS_CODE}


    def publish(self):
        while (True):
            try:
                event = self.q.get(timeout=10)
                event_id, user_token, service_token, add_info, reply_addr, client_message_id = event
                message = "UT:%s, %s, %s" % (user_token, service_token, self.get_data())
                utils.client(reply_addr).publish(service_token=service_token, user_token=user_token, event_id=event_id,
                                                 message=message, client_message_id=client_message_id)
            except Queue.Empty:
                continue


if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

cat_fact = cat_fact_collector_service()
cat_fact.port = globalconf.cat_port
cat_fact.tags = "cat,dog"

cat_fact.initiate_connection(linker)
cat_fact.setup_server()
cat_fact.register()
cat_fact.publish()