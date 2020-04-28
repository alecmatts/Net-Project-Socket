import socket
import threading
import sys

# constant values
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!"

def create_socket():
    func_status = 1
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(ADDR)
    except socket.error as msg:
        print(str(msg) + "\n")
        func_status = 0
    finally:
        return func_status, server

def start(server):
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}\n")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}\n")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")

    while True:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MSG:
                print(f"[DISCONNECTED] Client {addr} has gone offline.\n")
                break

            print(f"[RECEIVED DATA] {addr} : {msg}\n")

            if send_msg(conn, "Ok. I have received your request.") == 0:
                print("Can not send ACK to client.\n")

    conn.close()

def send_msg(conn, msg):
    message = msg.encode(FORMAT)

    msg_length = len(message)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))

    send_status = 1
    try:
        conn.sendall(msg_length)
        conn.sendall(message)
    except socket.error as msg:
        print(str(msg) + "\n")
        send_status = 0
    
    return send_status


def main():
    func_status, server = create_socket()
    if func_status:
        print("[STARTING] Server is starting...\n")
        start(server)
    else:
        print("[SHUTTING DOWN] Closing application due to create socket error...")