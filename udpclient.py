# github:  https://github.com/Ljinxu/homework

import socket

def udp_send_file(client_socket, filename, server_ip, server_port):
    print(f"Sending {filename} to {server_ip}:{server_port}")
    # 打开文件
    file = open(filename, "rb")
    # 分块读取和发送整个文件
    while True:
        data = file.read(1024)
        if not data:
            print(f"File {filename} sent!")
            break
        client_socket.sendto(data, (server_ip, server_port))
    # 关闭文件
    file.close()
    client_socket.sendto(b'', (server_ip, server_port))  # 发送空字节通知文件传输结束

def tcp_handshake(client_socket, server_ip, server_port):
    client_socket.sendto(b"SYN", (server_ip, server_port))  # 发送 SYN 数据包
    data, _ = client_socket.recvfrom(1024)  # 接收 SYN-ACK 数据包
    if data == b"SYN-ACK":
        client_socket.sendto(b"ACK", (server_ip, server_port))  # 发送 ACK 数据包确认连接建立
        print(f"Simulated TCP connection established to {server_ip}:{server_port}.")

def tcp_terminate(client_socket, server_ip, server_port):
    client_socket.sendto(b"FIN", (server_ip, server_port))  # 发送 FIN 数据包开始关闭连接
    data, _ = client_socket.recvfrom(1024)  # 接收对方的 ACK 确认
    client_socket.sendto(b"ACK", (server_ip, server_port))  # 发送 ACK 数据包确认收到对方的 FIN
    data, _ = client_socket.recvfrom(1024)  # 接收对方的 FIN 确认
    if data == b"FIN":
        print(f"Simulated TCP connection terminated from {server_ip}:{server_port}.")

def main():
    server_ip = input("Enter server IP: ")  # 输入服务器 IP 地址
    server_port = int(input("Enter server port: "))  # 输入服务器端口号

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建 UDP 套接字

    client_socket.sendto(b"CONNECT", (server_ip, server_port))  # 发送连接请求信息
    tcp_handshake(client_socket, server_ip, server_port)  # 进行 TCP 握手

    while True:
        command = input("Enter command (Send (s FileName) / TERMINATE (t)): ")  # 输入命令
        if command.startswith("s"):  # 如果命令以 "s" 开头
            _, filename = command.split()  # 分割命令，获取文件名
            client_socket.sendto(command.encode(), (server_ip, server_port))  # 发送命令信息
            udp_send_file(client_socket, filename, server_ip, server_port)  # 发送文件
        elif command == "t":  # 如果命令是 "t"
            client_socket.sendto(b"TERMINATE", (server_ip, server_port))  # 发送终止连接请求
            tcp_terminate(client_socket, server_ip, server_port)  # 进行 TCP 连接关闭
            break  # 跳出循环，结束程序
        else:
            print("Invalid command.")  # 打印无效命令提示信息

    client_socket.close()  # 关闭客户端套接字

if __name__ == "__main__":
    main()  # 调用主函数执行程序逻辑
