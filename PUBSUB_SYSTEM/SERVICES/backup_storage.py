import sys
sys.path.append("..")
sys.path.append("../..")
import Queue

class BackupStorage(object):
	def __init__(self):
		self.q = Queue.Queue()
		self.publish_q = Queue.Queue()
		self.last_ids = {} 
		self.received_message_ids = [] 
	def backup(self, q, publish_q, last_ids, received_message_ids):
		self.q = q
		self.publish_q = publish_q
		self.last_ids = last_ids
		self.received_message_ids = received_message_ids

	def recover(self):
		return self.q, self.publish_q, self.last_ids, self.received_message_ids