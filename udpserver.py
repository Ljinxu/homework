# github:  https://github.com/Ljinxu/homework

import socket
import os
from threading import Thread

# 获取本地IP地址的函数
def get_local_ip():
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))  # 连接到一个公共的IP地址和端口（Google的DNS服务器）
        local_ip = temp_socket.getsockname()[0]  # 获取本机IP地址
        temp_socket.close()
        return local_ip
    except socket.error:
        return "Unable to retrieve local IP"

# UDP接收文件的函数
def udp_receive_file(server_socket, filename, addr, port):
    with open(filename, 'wb') as file:
        print(f"Receiving {filename} from {addr}:{port}")
        while True:
            data, client_addr = server_socket.recvfrom(1024)
            print(data)
            if not data:
                break
            file.write(data)

# 模拟TCP握手过程的函数
def tcp_handshake(server_socket, client_addr, client_port):
    data, _ = server_socket.recvfrom(1024)
    server_socket.sendto(b"SYN-ACK", (client_addr, client_port))
    data, _ = server_socket.recvfrom(1024)
    if data == b"ACK":
        print(f"Simulated TCP connection established from {client_addr}:{client_port}.")

# 模拟TCP连接终止过程的函数
def tcp_terminate(server_socket, client_addr, client_port):
    data, _ = server_socket.recvfrom(1024)
    if data == b"FIN":
        server_socket.sendto(b"ACK", (client_addr, client_port))
    server_socket.sendto(b"FIN", (client_addr, client_port))
    data, _ = server_socket.recvfrom(1024)
    if data == b"ACK":
        print(f"Simulated TCP connection terminated from {client_addr}:{client_port}.")

# 文件传输的函数
def fileTransfer(server_socket, client_addr, client_port):
    while True:
        data, clientInfo = server_socket.recvfrom(1024)
        command, *params = data.decode().split()

        client_addr = clientInfo[0]
        client_port = clientInfo[1]

        if command == "s":
            filename = params[0]
            udp_receive_file(server_socket, filename, client_addr, client_port)
        elif command == "TERMINATE":
            tcp_terminate(server_socket, client_addr, client_port)
            break

    server_socket.close()

# 主函数
def main():
    server_ip = get_local_ip()  # 获取本地IP地址
    server_port = int(input("Please input server port:"))  # 输入服务器端口号

    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((server_ip, server_port))  # 绑定服务器IP和端口号

        print(f"Server listening on {server_ip}:{server_port}")
        data, clientInfo = server_socket.recvfrom(1024)  # 接收来自客户端的连接请求

        client_addr = clientInfo[0]
        client_port = clientInfo[1]

        if data == b"CONNECT":
            tcp_handshake(server_socket, client_addr, client_port)  # 进行TCP握手
            Thread(target=fileTransfer, args=(server_socket, client_addr, client_port)).start()  # 创建线程进行文件传输
            server_port += 1  # 更新服务器端口号，以便接受下一个连接

if __name__ == "__main__":
    main()  # 调用主函数执行程序逻辑
