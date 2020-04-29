import socket
import threading
import sys
import json
import unidecode

# constant values
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!"

INSTRUCTION = "[INSTRUCTION]\n1. Xem kết quả xổ số của tỉnh X, gửi truy vấn:\n                <X>           với X là tên tỉnh thành không có dấu, không có khoảng trắng.\n2. Tra sổ số theo số vé Y và tỉnh thành X, gửi truy vấn:\n      <X> <khoảng trắng> <Y>  với X là tên tỉnh thành không có dấu, không có khoảng trắng, Y là số vé của quý khách.\n"

NOT_SUPPORT = "[NOT SUPPORT] Request is not supported. Please try again.\n"

NO_PROVINCE = "[NOT FOUND] The province you looking up is not available. Please try again.\n"


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

def start(server, province_list, data_list):
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}\n")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, province_list, data_list))
        thread.start()
        print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}\n")

def handle_client(conn, addr, province_list, data_list):
    print(f"[NEW CONNECTION] {addr} connected")

    while True:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except socket.error as error_msg:
            print(f"Client {addr} has disconnected.")
            print("[ERROR]" + str(error_msg) + "\n")
            break

        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MSG:
                print(f"[DISCONNECTED] Client {addr} has gone offline.\n")
                break

            print(f"[RECEIVED DATA] {addr} : {msg}\n")

            print(f"[PROCESSING] Server is handling request from client {addr}.")
            result = handle_request(msg, province_list, data_list)
            print(f"[DONE] Sending result to client {addr}\n")
            if send_msg(conn, result) == 0:
                print("Can not send message to client.\n")

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

def launch_db():
    # Data from mien Nam
    with open('crawl_data/db/xsmn.json') as json_file:
        json_data = json_file.read()

    data_mn = json.loads(json_data)

    province_mn = []
    for i in data_mn:
        location = i['location']
        if location not in province_mn:
            province_mn.append(location)
        else:
            data_mn.remove(i)


    # Data from mien Trung
    with open('crawl_data/db/xsmt.json') as json_file:
        json_data = json_file.read()

    data_mt = json.loads(json_data)

    province_mt = []
    for i in data_mt:
        location = i['location']
        if location not in province_mt:
            province_mt.append(location)
        else:
            data_mt.remove(i)


    # Data from mien Bac
    with open('crawl_data/db/xsmb.json') as json_file:
        json_data = json_file.read()

    data_mb = json.loads(json_data)

    province_mb = []
    for i in data_mb:
        location = i['location']
        if location not in province_mb:
            province_mb.append(location)
        else:
            data_mb.remove(i)

    province_list = [province_mb, province_mt, province_mn]
    data_list = [data_mb, data_mt, data_mn]
    
    return province_list, data_list

def handle_VNese(string):
    new_string = unidecode.unidecode(string)
    new_string = new_string.replace(" ", "")
    return new_string.lower()

def handle_request(msg, province_list, data_list):
    msg = msg.lower()
    msg = msg.strip(" ")
    args_count = len(msg.split())

    if msg.isdigit():
        return NOT_SUPPORT

    if args_count == 1:
        if msg == 'h':
            output_string = "[RESPONSE] Danh sách các tỉnh có mở thưởng:\n"
            count = 0
            for region in province_list:
                if count == 0:
                    output_string += "+ Miền Bắc:\n"
                elif count == 1:
                    output_string += "+ Miền Trung:\n"
                elif count == 2:
                    output_string += "+ Miền Nam:\n"
                else:
                    break

                for province in region:
                    output_string += ("    " + province + "\n")
                count += 1
            return INSTRUCTION + "\n" + output_string
        else:
            output_string = "[RESPONSE] Kết quả xổ số của tỉnh "
            flag = 0
            found = 0
            province_to_search = ""

            for region in province_list:
                for province in region:
                    if msg == handle_VNese(province):
                        province_to_search = province
                        found = 1
                        break
                if found == 1:
                    break
                flag += 1

            if flag < 3:
                output_string += (province_to_search + ":\n")
                data_to_search = data_list[flag]
                for block in data_to_search:
                    if block['location'] == province_to_search:
                        for reward in block['data']:
                            output_string += ("     " + reward + ": " + block['data'][reward] + "\n")
                        return output_string            
            return NO_PROVINCE
                 
    elif args_count == 2:
        #Request 2
        province_request = msg.split()[0]
        return ""
    
    else:
        return NOT_SUPPORT

def main():
    province_list, data_list = launch_db()

    func_status, server = create_socket()
    if func_status:
        print("[STARTING] Server is starting...\n")
        start(server, province_list, data_list)
    else:
        print("[SHUTTING DOWN] Closing application due to create socket error...")