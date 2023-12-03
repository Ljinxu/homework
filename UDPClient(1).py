# github:  https://github.com/Isaaaaaaaaaaaaaa/Computer-Network

import os
import select
from socket import *

TIMEOUT = 5  # 超时时间设置为 5 秒

# 判断IP地址是否合法的函数
def is_valid_ip(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        i = int(part)
        if i < 0 or i > 255:
            return False
    return True

while True:
    flag = input("是否继续传输文件？(Y/n)：")
    if flag.lower() == "n":
        break
    
    # 获取目标端口号
    while True:
        server_port = input("请输入目标端口号：")
        if server_port.isdigit() and 0 <= int(server_port) <= 65535:
            server_port = int(server_port)
            break
        else:
            print("请输入有效的端口号！")
            
    # 获取服务器IP地址
    while True:
        server_name = input("请输入服务器 IP 地址：")
        if is_valid_ip(server_name):
            break
        else:
            print("请输入有效的 IP 地址！")

    # 创建 UDP 套接字
    client_socket = socket(AF_INET, SOCK_DGRAM)
    print("尝试建立连接...")

    connection_established = False
    retry_count = 0
    
    # 建立连接的过程
    while True:
        client_socket.sendto("SYN".encode(), (server_name, server_port))
        ready = select.select([client_socket], [], [], TIMEOUT)
        
        if ready[0]:
            ack = client_socket.recv(1024)
            if ack == b"ACK":
                client_socket.sendto("ACK".encode(), (server_name, server_port))
                print(f"已连接到服务器，IP：{server_name}，端口号：{server_port}")
                connection_established = True
                break
        elif retry_count > 2:
            break
        else:
            retry_count += 1
            print(f"超时，重试中...次数 = {retry_count}")
    
    if not connection_established:
        print("连接失败，请重试！")
        continue
    
    while True:
        transfer_type = input("请选择传输类型：发送(s)/接收(r)，输入 q 退出：")
        
        if transfer_type.lower() not in ["s", "r", "q"]:
            print("请输入有效的传输类型！")
            continue
        
        client_socket.sendto(transfer_type.encode(), (server_name, server_port))
        
        while True:
            ack = client_socket.recv(1024)
            if ack == b"ACK":
                break
        
        if transfer_type.lower() == "q":
            while True:
                print("尝试释放连接...")
                client_socket.sendto("FIN".encode(), (server_name, server_port))
                ack = client_socket.recv(1024)
                if ack == b"ACK":
                    break
            
            while True:
                fin = client_socket.recv(1024)
                if fin == b"FIN":
                    break
                
            client_socket.sendto("ACK".encode(), (server_name, server_port))
            client_socket.close()
            print("连接已释放")
            break
        
        elif transfer_type.lower() == "s":
            while True:
                file_name = input("请输入文件名：")
                if os.path.exists(file_name):
                    #处理文件名
                    filePath = file_name.split('/')
                    #发送文件名
                    client_socket.sendto(filePath[len(filePath)-1].encode(),(server_name,server_port))
                    #接收ACK
                    
                    while True:
                        ack = client_socket.recv(1024)
                        if ack == b"ACK":
                            break
                    
                    file_to_send = open(file_name, "rb")
                    while True:
                        data = file_to_send.read(1024)
                        if not data:
                            client_socket.sendto("ACK".encode(), (server_name, server_port))
                            print("文件已发送！")
                            break
                        client_socket.sendto(data, (server_name, server_port))
                    file_to_send.close()
                    break
                else:
                    print("文件不存在！")
        
        elif transfer_type.lower() == "r":
            while True:
                file_name = input("请输入文件名：")
                client_socket.sendto(file_name.encode(), (server_name, server_port))
                ack = client_socket.recv(1024)
                if ack == b"ACK":
                    break
                else:
                    print("文件不存在！")
                    
            received_file = open(file_name, "wb")
            while True:
                data, addr = client_socket.recvfrom(1024)
                if data == b"ACK":
                    print("文件已接收！")
                    break
                received_file.write(data)
            received_file.close()
