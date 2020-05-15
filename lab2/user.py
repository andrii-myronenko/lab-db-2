import redis
import atexit
import datetime
import logging

logging.basicConfig(filename="messanger.log", level=logging.INFO)


def sign_in(conn, username) -> int:
    user_id = conn.hget("users:", username)

    if not user_id:
        print("No user with such username exists. Please, register first")
        return -1

    conn.sadd("online:", username)
    logging.info(f"{datetime.datetime.now()} Actor: {username} Action: log in \n")

    return int(user_id)


def sign_out(conn, user_id) -> int:
    username = conn.hmget("user:%s" % user_id, ["login"])[0];
    logging.info(f"{datetime.datetime.now()} Actor: {username} Action: sign out \n")
    return conn.srem("online:", conn.hmget("user:%s" % user_id, ["login"])[0])


def create_message(conn, message_text, sender_id, consumer) -> int:
    try:
        message_id = int(conn.incr('message:id:'))
        consumer_id = int(conn.hget("users:", consumer))
    except TypeError:
        print("No user with %s username exists, can't send a message" % consumer)
        return

    pipeline = conn.pipeline(True)

    pipeline.hmset('message:%s' % message_id, {
        'text': message_text,
        'id': message_id,
        'sender_id': sender_id,
        'consumer_id': consumer_id,
        'status': "created"
    })

    pipeline.lpush("queue:", message_id)
    pipeline.hmset('message:%s' % message_id, {
        'status': 'queue'
    })

    pipeline.zincrby("sent:", 1, "user:%s" % conn.hmget("user:%s" % sender_id, ["login"])[0])
    pipeline.hincrby("user:%s" % sender_id, "queue", 1)
    pipeline.execute()

    return message_id

def register(conn, username):
    if conn.hget('users:', username):
        print(f"User {username} exists");
        return None

    user_id = conn.incr('user:id:')

    pipeline = conn.pipeline(True)

    pipeline.hset('users:', username, user_id)

    pipeline.hmset('user:%s' % user_id, {
        'login': username,
        'id': user_id,
        'queue': 0,
        'checking': 0,
        'blocked': 0,
        'sent': 0,
        'delivered': 0
    })
    pipeline.execute()
    logging.info(f"{datetime.datetime.now()} Actor: {username} Action: register \n")
    return user_id

def print_messages(connection, user_id):
    messages = connection.smembers("sentto:%s" % user_id)
    for message_id in messages:
        message = connection.hmget("message:%s" % message_id, ["sender_id", "text", "status"])
        sender_id = message[0]
        print("From: %s - %s" % (connection.hmget("user:%s" % sender_id, ["login"])[0], message[1]))
        if message[2] != "delivered":
            pipeline = connection.pipeline(True)
            pipeline.hset("message:%s" % message_id, "status", "delivered")
            pipeline.hincrby("user:%s" % sender_id, "sent", -1)
            pipeline.hincrby("user:%s" % sender_id, "delivered", 1)
            pipeline.execute()


def main_menu() -> int:
    print(10 * "*", "Main menu", 10 * "*")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return int(input("What do you want to do?: "))


def user_menu() -> int:
    print(10 * "*", "User menu", 10 * "*")
    print("1. Log out")
    print("2. Inbox")
    print("3. Create message")
    print("4. Statistics")
    return int(input("What do you want to do?: "))

def is_user_signed_in(current_user_id):
    return current_user_id != -1

def user_menu_flow(connection, current_user_id):
    while True:
        choice = user_menu()

        if choice == 1:
            sign_out(connection, current_user_id)
            connection.publish('users', "User %s signed out" % connection.hmget("user:%s" % current_user_id, ["login"])[0])
            break;

        elif choice == 2:
            print_messages(connection, current_user_id)

        elif choice == 3:
            try:
                message = input("Type your message:")
                recipient = input("Type the username of the reciever:")
                if create_message(connection, message, current_user_id, recipient):
                    print("Sending message...")
            except ValueError:
                print("User with such login wasn`t found!")

        elif choice == 4:
            current_user = connection.hmget("user:%s" % current_user_id,['queue', 'checking', 'blocked', 'sent', 'delivered'])
            print("In queue: %s\nChecking: %s\nBlocked: %s\nSent: %s\nDelivered: %s" %tuple(current_user))
        else:
            print("Please select correct option [1-4]")

def main():
    def exit_handler():
        sign_out(connection, current_user_id)

    atexit.register(exit_handler)
    connection = redis.Redis(charset="utf-8", decode_responses=True)

    while True:
        choice = main_menu()

        if choice == 1:
            login = input("Enter your username:")
            register(connection, login)

        elif choice == 2:
            login = input("Enter your login:")
            current_user_id = sign_in(connection, login)
            if is_user_signed_in(current_user_id):
                username = connection.hmget("user:%s" % current_user_id, ["login"])[0];
                connection.publish('users', "User %s signed in" % username)
                user_menu_flow(connection, current_user_id)

        elif choice == 3:
            print("Exiting...")
            break;

        else:
            print("Please select correct option [1-3]")


if __name__ == '__main__':
    main()