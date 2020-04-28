import socket

PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!"

def create_socket():
    func_status = 1
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
    except socket.error as msg:
        print(str(msg) + "\n")
        func_status = 0

    return func_status, client

def send_msg(client, msg):
    message = msg.encode(FORMAT)

    msg_length = len(message)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))

    send_status = 1
    try:
        client.sendall(msg_length)
        client.sendall(message)
    except socket.error as msg:
        print(str(msg) + "\n")
        send_status = 0
    
    return send_status

def handle_server(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        try:
            msg = client.recv(msg_length).decode(FORMAT)
        except socket.error as error_msg:
            print(str(error_msg) + "\n")
            return 0     
        print(msg)
        return 1


def main():
    func_status, client = create_socket()
    if func_status:
        print(f"[CONNECTED] Client has connected to server at port {PORT}\n")

        while True:
            msg = input("> ")
            if send_msg(client, msg) == 0:
                break

            if msg == DISCONNECT_MSG:
                break

            if not handle_server(client):
                break

        print("[DISCONNECT] Client is disconnecting from server.")
        client.close()
    else:
        print("[SHUTTING DOWN] Closing application due to create socket error...")