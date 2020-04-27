import client
import server

while True:
    user_type = input("Are you a client or a server? (server/client/!)    ")

    if user_type == "server":
        print("     Starting as the SERVER.\n")
        server.main()
        break;
    elif user_type == "client":
        print("     Starting as a CLIENT.\n")
        client.main()
        break
    elif user_type == "!":
        print("     Exiting the program.")
        break
    else:
        print("[UNKNOWN USER TYPE] Try again. You are a ___")
        print("     SERVER: type \"server\"")
        print("     CLIENT: type \"client\"")
        print("     If you want to exit the program, type \"!\"")
        continue