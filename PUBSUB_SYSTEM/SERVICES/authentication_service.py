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

    def authentication(self,username,password,token):
        return self.get_data(self)


    def initiate_connection(self):
        self.client = utils.client(globalconf.location)

    def initalise_db(self):
        con = sqlite3.connect("users.db")
        print "Opened database successfully"
        con.isolation_level = None
        cur = con.cursor()
        cur.execute("CREATE TABLE Users(username, password, token)")
        cur.execute("INSERT  INTO  Users(username, password, token) \
                      VALUES (test, putin, 12)")
        print "current row count: " + str(cur.rowcount)
        cur.close()
        con.commit()
        con.close()

    def insert_into_db(self, username, password, token):
        con = sqlite3.connect("users.db")
        print "Opened database successfully"
        con.isolation_level = None
        cur = con.cursor()
        cur.execute("INSERT  INTO  Users(username, password, token) \
                  VALUES (username, password, token)")
        print "current row count: " + str(cur.rowcount)
        cur.close()
        con.commit()
        con.close()

    def get_db_handle(self):
        con = sqlite3.connect("users.db")
        return con;

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def get_connection(self):
        return self.client

    def get_data(self):
        command = "Select * from Users where token = 12"
        # con = self.get_db_handle()
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        query_result = cur.execute(command)
        user_data = query_result.fetchone()
        print user_data
        con.close()
        return str(user_data)

    def recover_message(self):
        pass

if len(sys.argv) > 1:
    linker = sys.argv[1]
else:
    linker = globalconf.location

au = authentication()
# au.initalise_db()
au.port = utils.generate_port()
au.tags = "cat,dog"
au.initiate_connection(linker)
au.setup_server()
au.register()
au.publish()