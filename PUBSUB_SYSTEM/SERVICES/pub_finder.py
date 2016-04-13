"""
WARNING: 
This component uses Google Map library. To install it, type in the command line:
pip install geolocation-python
"""
import sys

sys.path.append("..")
sys.path.append("../..")
from geolocation.main import GoogleMaps
from service_interfaces import service_interface
import global_configuration as globalconf
import global_utils as utils
import Queue
from backup_storage import BackupStorage


class PubFinder(service_interface):
    def __init__(self):
        self.bs = BackupStorage()
        service_interface.__init__(self)

    """
    This function estimates the closest pub based on the driver geolocation.
    @param driver_location current location of the driver
    @return zip code of the closest pub
    """

    def find_closest_pub(self, driver_location):
        google_maps = GoogleMaps(api_key='AIzaSyBdo6RCkcJ692cefoRn3IfTdn3DsjDXRoE')
        driver_location = google_maps.search(location=driver_location)
        pub_locations = google_maps.search(location="pub")
        pub_locations = pub_locations.all()  # Find all british pubs
        duration = []  # Duration of the travel by car between a driver and the pub
        for pub_location in pub_locations:
            item = google_maps.distance(driver_location, pub_location).first()
            duration.append([pub_location, item.distance.kilometers])
        closest_pub = min(duration)
        import time
        print "START DELAY"
        # To initiate a very long delay of 20s
        time.sleep(20)
        print "END DELAY"
        return closest_pub[0].postal_code  # Find closest pub to driver

    def initiate_connection(self, location):
        self.client = utils.client(location)

    def get_connection(self):
        return self.client

    def get_data(self):
        # Coordinates of the driver are 48.234123, 76.1234532 for the testing purposes
        return self.find_closest_pub("48.234123, 76.1234532")

    def backup(self):
        self.bs.backup(self.q, self.publish_q, self.last_ids, self.received_message_ids)

    def publish(self):
        while True:
            try:
                event = self.q.get(timeout=5)
                event_id, user_token, service_token, add_info, reply_addr, client_message_id = event

                # check for repetition of messages
                if self.last_ids.__contains__(str(client_message_id)):
                    print "DUPLICATE"
                    return {"errorcode": globalconf.REPETITION_CODE}
                else:
                    # Add received msg ID to list of received messages
                    self.last_ids[user_token] = client_message_id
                self.backup()
                
                print "CRUSH QUEUE"

                self.q = Queue.Queue()
                self.publish_q = Queue.Queue()
                self.last_ids = {}  # Dictionary of user_id -> last message id from a client
                self.received_message_ids = []  # List of all recieved client ID messages

                print "QUEUE CRUSHED"

                if add_info is not None:
                    message = "UT:%s, %s, %s" % (user_token, service_token, self.get_data())
                    # Return fulfilled request to client
                    utils.client(reply_addr).publish(service_token=service_token, user_token=user_token,
                                                     event_id=event_id, message=message,
                                                     client_message_id=client_message_id)
                print "START RECOVER PROCEDURE"

                recover = self.bs.recover()
                self.q = recover[0]
                self.publish_q = recover[1]
                self.last_ids = recover[2]
                self.received_message_ids = recover[3]

                if self.q is not None and self.publish_q is not None and self.last_ids is not None and self.received_message_ids is not None:
                	print "RECOVER WAS SUCCESSFUL"


            except Queue.Empty:
                continue

if __name__ == "__main__":
	if len(sys.argv) > 1:
		linker = sys.argv[1]
	else:
		linker = globalconf.location

	pc = PubFinder()
	pc.port = utils.generate_port()
	pc.tags = "pub"
	pc.initiate_connection(linker)
	pc.setup_server()
	pc.register()
	pc.publish()
