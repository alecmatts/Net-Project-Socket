import socket
import logging

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
        logging.error(str(msg) + "\n")
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
        logging.error(str(msg) + "\n")
        send_status = 0
    
    return send_status

def handle_server(client):
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = msg_length.strip()
        if msg_length.isdigit():
            msg_length = int(msg_length)
        else:
            logging.error("[ERROR] Something happened to the server.\n")
            return 0
        
        try:
            msg = client.recv(msg_length).decode(FORMAT)
        except socket.error as error_msg:
            logging.error(str(error_msg) + "\n")
            return 0     
        logging.info(msg)
        return 1

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    func_status, client = create_socket()
    if func_status:
        logging.info(f"[CONNECTED] Client has connected to server at port {PORT}.\n")

        while True:
            try:
                msg = input("> ")
            except KeyboardInterrupt as error_msg:
                logging.info("\n[INTERRUPTED] Detected KeyboardInterrupt. Force closing application.\n")
                msg = DISCONNECT_MSG

            if send_msg(client, msg) == 0:
                break

            if msg == DISCONNECT_MSG:
                break

            if not handle_server(client):
                break

        logging.info("[DISCONNECT] Client is disconnecting from server.")
        client.close()
    else:
        logging.info("[SHUTTING DOWN] Closing application due to create socket error...")