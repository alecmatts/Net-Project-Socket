import socket
import threading
import json
import unidecode
import subprocess
import logging

# constant values
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!"

NON_SERVICE = "[ERROR] Please connect as a client for service.\n"

INSTRUCTION = "[INSTRUCTION]\n1. Xem kết quả xổ số của tỉnh X, gửi truy vấn:\n                <X>           với X là tên tỉnh thành không có dấu, không có khoảng trắng.\n2. Tra sổ số theo số vé Y và tỉnh thành X, gửi truy vấn:\n      <X> <khoảng trắng> <Y>  với X là tên tỉnh thành không có dấu, không có khoảng trắng, Y là số vé của quý khách.\n"
NOT_SUPPORT = "[NOT SUPPORT] Request is not supported. Please try again.\n"
NO_PROVINCE = "[NOT FOUND] The province you looking up is not available. Please try again.\n"
NOT_VALID = "[NOT VALID] Your ticket number is not in the right format. Please try again.\n"

def create_socket():
    func_status = 1
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(ADDR)
    except socket.error as msg:
        logging.error(str(msg) + "\n")
        func_status = 0
    finally:
        return func_status, server

def start(server, province_list, data_list, reward_value):
    server.listen()
    logging.info(f"[LISTENING] Server is listening on {HOST}.\n")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, province_list, data_list, reward_value))
        thread.start()
        logging.info(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}.\n")

def handle_client(conn, addr, province_list, data_list, reward_value):
    logging.info(f"[NEW CONNECTION] {addr} connected.")

    while True:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except socket.error as error_msg:
            logging.info(f"Client {addr} has disconnected.")
            logging.error("[ERROR]" + str(error_msg) + "\n")
            break

        if msg_length:
            msg_length = msg_length.strip()
            if msg_length.isdigit():
                msg_length = int(msg_length)
            else:
                if send_msg(conn, NON_SERVICE) == 0:
                    logging.error("[ERROR] Can not send message to client.\n")
                break

            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MSG:
                logging.info(f"[DISCONNECTED] Client {addr} has gone offline.\n")
                break

            logging.info(f"[RECEIVED DATA] {addr} : {msg}. \n[PROCESSING] Server is handling request from client {addr}.\n")

            result = handle_request(msg, province_list, data_list, reward_value)
            
            logging.info(f"[DONE] Sending result to client {addr}.\n")
            if send_msg(conn, result) == 0:
                logging.error("[ERROR] Can not send message to client.\n")

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
        logging.error(str(msg) + "\n")
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
    
    with open('crawl_data/db/value.json') as json_file:
        json_data = json_file.read()

    reward_value = json.loads(json_data)

    return province_list, data_list, reward_value

def handle_VNese(string):
    new_string = unidecode.unidecode(string)
    new_string = new_string.replace(" ", "")
    return new_string.lower()

def get_province(input, province_list):
    region_mode = 0

    for region in province_list:
        for province in region:
            if input == handle_VNese(province):
                return province, region_mode
        region_mode += 1
    
    return "", -1

def get_reward(province, data):
    reward_list = []
    for block in data:
        if block['location'] == province:
            for reward in block['data']:
                reward_number = []
                reward_number.append(reward)
                number = (block['data'][reward]).split(', ')
                reward_number.extend(number)
                reward_list.append(reward_number)
            return reward_list

def handle_request(msg, province_list, data_list, reward_value):
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
                    output_string += ("    " + province + " (" + handle_VNese(province) + ")\n")
                count += 1
            return INSTRUCTION + "\n" + output_string
        else:
            output_string = "[RESPONSE] Kết quả xổ số của tỉnh/thành phố "
            province, mode = get_province(msg, province_list)
            output_string += (province + ":\n")

            if mode == -1:
                return NO_PROVINCE
            else:
                reward_list = get_reward(province, data_list[mode])
                for reward in reward_list:
                    output_string += ("      " + reward[0] + ": ")
                    for i in range (1, len(reward) - 2):
                        output_string += (reward[i] + ", ")
                    output_string += (reward[len(reward) - 1] + "\n")
                return output_string
                 
    elif args_count == 2:
        output_string = "[RESPONSE] Kết quả dò xổ số: \n"
        province_request = msg.split()[0]
        number_request = msg.split()[1]
        if province_request.isdigit() == False and number_request.isdigit() == True:
            province, mode = get_province(province_request, province_list)
            if mode == -1:
                return NO_PROVINCE
            elif (mode == 0 and len(number_request) != 5) or (mode != 0 and len(number_request) != 6):
                return NOT_VALID
            else:
                reward_list = get_reward(province, data_list[mode])
                for reward in reward_list:
                    reward_name = reward[0]
                    reward.pop(0)
                    for number in reward:
                        if number_request.rfind(number) == len(number_request) - len(number):
                            output_string += "Chúc mừng bạn đã trúng " + reward_name + " trị giá " + reward_value[str(mode)][reward_name] + ".\n"
                            return output_string
                    
                output_string += "Chúc bạn may mắn lần sau.\n"
                return output_string

    else:
        return NOT_SUPPORT
    
    return NOT_SUPPORT

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    func_status, server = create_socket()

    if func_status:
        logging.info("[UPDATING] Database is being updated...\n")
        with open("temp_log.txt", "a") as f:
            crawl = subprocess.run("del crawl_data\\db\\xsmb.json crawl_data\\db\\xsmt.json crawl_data\\db\\xsmn.json && cd crawl_data && scrapy crawl", stdout=f, stderr=f, text=True, shell=True)

        logging.info("[LOADING] Loading database to serve...\n")
        province_list, data_list, reward_value = launch_db()

        logging.info("[DONE] Data is loaded. Ready to serve.\n")

        logging.info("[STARTING] Server is starting...\n")
        start(server, province_list, data_list, reward_value)
    else:
        logging.info("[SHUTTING DOWN] Closing application due to create socket error...")

    server.close()