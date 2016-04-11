import os
import time


class service_interface:

    def ping_service(hostname):
        response = os.system("ping -c 1 " + hostname)

        if response == 0:
            print hostname, 'is up!'
            return True
        else:
            print hostname, 'is down!'
            return False

    def initiate_connection(server_hostname):
        """returns a client conenction to the server   """
        pass

    def get_connection(object):
        pass

    def get_data(object):
        pass

    def recover_message(object):
        pass

    # Publish info
    def publish(object):
       while(True):
            # wait 10 seconds before publishing
            time.sleep(10)
            # publish to server
            connection = object.get_connection()
            connection.publish(object.getData())