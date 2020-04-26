import socket

PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"[CONNECTING] Client has connected to server with port {PORT}")

def send_msg(msg):
    message = msg.encode(FORMAT)
    
    msg_length = len(message)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    
    client.send(msg_length)
    client.send(message)

while True:
    msg = input("> ")
    send_msg(msg)

    if msg == DISCONNECT_MSG:
        break;

print("[DISCONNECT] Client is disconnecting from server.")
client.close()
