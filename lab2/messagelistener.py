import datetime
import logging
from threading import Thread

logging.basicConfig(filename="messanger.log", level=logging.INFO)

class EventListener(Thread):
    def __init__(self, connection):
        Thread.__init__(self)
        self.connection = connection

    def run(self):
        pubsub = self.connection.pubsub()
        pubsub.subscribe(["users", "spam"])
        for item in pubsub.listen():
            if item['type'] == 'message':
                message = "\n%s Event: %s" % (datetime.datetime.now(), item['data'])
                logging.info(message)
