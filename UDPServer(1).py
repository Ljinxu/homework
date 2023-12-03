# github:  https://github.com/Isaaaaaaaaaaaaaa/Computer-Network

import os
from socket import *
from threading import Thread

# 传输文件
def transfer(server_socket, client_name, client_port):   
    while True:
        # 接收传输类型
        transfer_type = server_socket.recv(1024)
        # 发送 ACK
        server_socket.sendto("ACK".encode(), (client_name, client_port))    
        
        if transfer_type == b"q":
            # 接收 FIN
            while True:
                fin = server_socket.recv(1024)
                if fin == b"FIN":
                    server_socket.sendto("ACK".encode(), (client_name, client_port))
                    break
            # 发送 ACK
            server_socket.sendto("ACK".encode(), (client_name, client_port))
            # 发送 FIN
            server_socket.sendto("FIN".encode(), (client_name, client_port))
            # 接收 ACK
            while True:
                ack = server_socket.recv(1024)
                if ack == b"ACK":
                    print(f"Connection released from client IP: {client_name}, Port Number: {client_port}!")
                    break
            break
        elif transfer_type == b"r":   
            while True:
                # 接收客户端发送的文件名
                file_name = server_socket.recv(1024).decode()
                if os.path.exists(file_name):
                    server_socket.sendto("ACK".encode(), (client_name, client_port))
                    file_to_send = open(file_name, "rb")
                    while True:
                        data = file_to_send.read(1024)
                        if not data:
                            print(f"The file {file_name} has been sent to client (IP: {client_name}, Port Number: {client_port})!")
                            server_socket.sendto("ACK".encode(), (client_name, client_port))
                            break
                        server_socket.sendto(data, (client_name, client_port))
                    file_to_send.close()
                    break
                else:
                    server_socket.sendto("Error".encode(), (client_name, client_port))
                    print(f"The File {file_name} which client (IP: {client_name}, Port Number: {client_port}) asked does not exist!")
        elif transfer_type == b"s":
            # 接收文件名
            file_name = server_socket.recv(1024).decode()
            # 返回 ACK
            server_socket.sendto("ACK".encode(), (client_name, client_port))
            file = open(file_name, "wb")
            # 接收文件
            while True:
                data, addr = server_socket.recvfrom(1024)
                client_name, client_port = addr
                if data == b"ACK":
                    print(f"The file {file_name} received from client (IP: {client_name}, Port Number: {client_port})!")
                    break
                file.write(data)
            # 关闭文件
            file.close()

while True:
    # 设定服务器端端口号
    while True:
        server_port = input("Please input server Port number: ")
        if server_port.isdigit() and 0 <= int(server_port) <= 65535:
            server_port = int(server_port)
            break
        else:
            print("Please input a valid Port number!")

    while True:
        # 创建 UDP socket
        server_socket = socket(AF_INET, SOCK_DGRAM)
        server_socket.bind(('', server_port))
        server_port += 1
        
        # 模拟建立 TCP 连接
        while True:
            syn = server_socket.recvfrom(1024)
            client_name, client_port = syn[1]
            if syn[0] == b"SYN":
                server_socket.sendto("ACK".encode(), (client_name, client_port))
                while True:
                    ack = server_socket.recv(1024)
                    if ack == b"ACK":
                        print(f"Connection established from IP: {client_name}, Port Number: {client_port}")
                        break
                break

        Thread(target=transfer, args=(server_socket, client_name, client_port)).start()
 