import sys
sys.path.append("../..")
sys.path.append("..")

import Queue
from threading import Thread
import time


# FIFO multi-producer, multi-consumer queue class to hold the publisher messages before they are sent.
# Using Queue library so information can be exchanged safely between multiple threads.

class publishers_queue():
    def __init__(self):
        self.queue = None

    def put_message(self, msg):
        self.queue.put(msg)

    def remove_message(self):
        if not self.queue.empty():
            print self.queue.get()
            return self.queue.get()

