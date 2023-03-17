import socket
import config
from threading import Thread
import utils


clients: dict[(int, int), socket.socket] = {}


def accept_tcp_clients(server_socket: socket.socket):
    while True:
        tcp_client_socket, client_address = server_socket.accept()
        clientthread = Thread(target=handle_tcp_client, args=(tcp_client_socket, client_address))
        clientthread.start()


def handle_tcp_client(tcp_client_socket: socket.socket, client_address: (int, int)):
    ip, port = client_address
    print("Starting new connection IP:", ip, "port:", port)
    clients[client_address] = tcp_client_socket

    while True:
        data = utils.tcp_recvmsg(tcp_client_socket)
        if data == b'':
            clients.pop(client_address)
            tcp_client_socket.close()
            print("Disconnecting client:", client_address)
            return

        print("Received data from TCP:", data)

        for client in clients.values():
            if client != tcp_client_socket:
                client.sendall(data)


def handle_udp(udp_socket: socket.socket):
    while True:
        try:
            data, udp_client_socket = udp_socket.recvfrom(1024)
        except OSError:
            return

        for client in clients.keys()\
                :
            if client != udp_client_socket:
                udp_server_socket.sendto(data, client)


if __name__ == '__main__':
    tcp_server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    try:
        tcp_server_socket.bind(config.server_address)
    except OSError:
        tcp_server_socket.close()
        print("Socket binding went wrong!")
        raise SystemExit
    tcp_server_socket.listen(5)

    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        udp_server_socket.bind(config.server_address)
    except OSError:
        udp_server_socket.close()
        tcp_server_socket.close()
        print("Socket binding went wrong!")
        raise SystemExit

    Thread(target=accept_tcp_clients, args=(tcp_server_socket,), daemon=True).start()
    Thread(target=handle_udp, args=(udp_server_socket,), daemon=True).start()

    utils.pause()

    for client_address, tcp_client_socket in clients.items():
        tcp_client_socket.shutdown(socket.SHUT_WR)
    tcp_server_socket.close()
