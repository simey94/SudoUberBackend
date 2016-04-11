import sys
sys.path.append("..")
sys.path.append("../..")

from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils
import sqlite3

class authentication(service_interface):
    def __init__(self):
        service_interface.__init__(self)

    def initiate_connection(self):
        self.client = utils.client(globalconf.location)

    def initalise_db(self):
        con = sqlite3.connect("users.db")
        print "Opened database successfully"
        con.isolation_level = None
        con.text_factory = str
        cur = con.cursor()
        # cur.execute("CREATE TABLE Users(username, password, token)")
        cur.execute("INSERT  INTO  Users (username, password, token) \
                    VALUES ('masha', 'PUTINROCKS2', 19)")
        print "current row count: " + str(cur.rowcount)
        cur.close()
        con.commit()
        con.close()

    def insert_into_db(self, username, password, token):
        con = sqlite3.connect("users.db")
        print "Opened database successfully"
        con.isolation_level = None
        con.text_factory = str
        cur = con.cursor()
        cur.execute("INSERT  INTO  Users(username, password, token) VALUES (username, password, token)")
        print "current row count: " + str(cur.rowcount)
        cur.close()
        con.commit()
        con.close()

    def get_db_handle(self):
        con = sqlite3.connect("users.db")
        return con;

    def get_connection(self):
        return self.client

    def get_data(self):
        command = "Select * from Users where token = 19"
        # con = self.get_db_handle()
        con = sqlite3.connect("users.db")
        con.text_factory = str
        cur = con.cursor()
        query_result = cur.execute(command)
        user_data = query_result.fetchone()
        print user_data
        con.close()
        return str(user_data)

    def recover_message(self):
        pass

au = authentication()
au.initalise_db()
au.port = utils.generate_port()
au.tags = "cat,dog"
au.initiate_connection()
au.register()
au.publish()

# TODO: All this stuff
# Dropped messages;
#   No ack re-send
# Temporary interruptions of connections;
# Crashing queues;
# Crashing customers;
# Increasing number of queries;
# Mobility of users;
# Long delays in network traffic;
# Out of order messages;
# If(msg_id != expected):
#     wait to recieve next msg
# Duplicated messages
#     Ignore duplicated msg