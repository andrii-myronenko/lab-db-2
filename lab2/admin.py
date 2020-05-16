import redis

def admin_menu():
    print(10 * "*", "Admin menu", 10 * "*")
    print("1. Users online")
    print("2. Top senders")
    print("3. Top spamers")
    print("4. Exit")
    return int(input("What do you want to do? "))

def main():
    loop = True
    connection = redis.Redis(charset="utf-8", decode_responses=True)

    while loop:
        choice = admin_menu();

        if choice == 1:
            online_users = connection.smembers("online:")
            print("Users online:")
            for user in online_users:
                print(user)

        elif choice == 2:
            top_senders_count = 10
            senders = connection.zrange("sent:", 0, top_senders_count, desc=True, withscores=True)
            print("Top %s senders" % top_senders_count)
            for index, sender in enumerate(senders):
                print(index + 1, ". ", sender[0], " - ", int(sender[1]), "message(s)")

        elif choice == 3:
            top_spamers_count = 10
            spamers = connection.zrange("spam:", 0, top_spamers_count, desc=True, withscores=True)
            print("Top %s spamers" % top_spamers_count)
            for index, spamer in enumerate(spamers):
                print(index + 1, ". ", spamer[0], " - ", int(spamer[1]), " spammed message(s)")

        elif choice == 4:
            print("Exiting...")
            loop = False
        else:
            print("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()
