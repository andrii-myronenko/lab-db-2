import time
import random
from threading import Thread
from messagelistener import EventListener

import redis

class QueueMessageWorker(Thread):

    def __init__(self, conn, delay):
        Thread.__init__(self)
        self.conn = conn
        self.delay = delay

    def run(self):
        while True:
            message = self.conn.brpop("queue:")
            if message:
                message_id = int(message[1])

                self.conn.hmset('message:%s' % message_id, {
                    'status': 'checking'
                })
                message = self.conn.hmget("message:%s" % message_id, ["sender_id", "consumer_id"])
                sender_id = int(message[0])
                consumer_id = int(message[1])
                self.conn.hincrby("user:%s" % sender_id, "queue", -1)
                self.conn.hincrby("user:%s" % sender_id, "checking", 1)
                time.sleep(self.delay)

                message_text = self.conn.hmget("message:%s" % message_id, ["text"])[0];
                is_spam = "spam" in message_text
                pipeline = self.conn.pipeline(True)
                pipeline.hincrby("user:%s" % sender_id, "checking", -1)
                if is_spam:
                    print("The message with id %d was blocked. It is spam" % message_id)
                    sender_username = self.conn.hmget("user:%s" % sender_id, ["login"])[0]
                    pipeline.zincrby("spam:", 1, "user:%s" % sender_username)
                    pipeline.hmset('message:%s' % message_id, {
                        'status': 'blocked'
                    })
                    pipeline.hincrby("user:%s" % sender_id, "blocked", 1)
                    pipeline.publish('spam', "User %s sent spam message: \"%s\"" % (sender_username, message_text))
                else:
                    print("The message with id %d was checked and sent." % message_id)
                    pipeline.hmset('message:%s' % message_id, {
                        'status': 'sent'
                    })
                    pipeline.hincrby("user:%s" % sender_id, "sent", 1)
                    pipeline.sadd("sentto:%s" % consumer_id, message_id)
                pipeline.execute()


def main():
    handlers_count = 5
    handlers_delay = 3

    connection = redis.Redis(charset="utf-8", decode_responses=True)
    listener = EventListener(connection)
    listener.setDaemon(True)
    listener.start()

    for x in range(handlers_count):
        connection = redis.Redis(charset="utf-8", decode_responses=True)
        worker = QueueMessageWorker(connection, random.randint(0, 3))
        worker.daemon = True
        worker.start()
    while True:
        pass


if __name__ == '__main__':
    main()