import os
import utils
import socket
import select
import struct
import config
from threading import Thread


def receive(tcp_sock, udp_sock, mcast_sock):
    while True:
        ready_socks, _, _ = select.select([tcp_sock, udp_sock, mcast_sock], [], [])

        if tcp_sock in ready_socks:
            try:
                data = utils.tcp_recvmsg(tcp_sock)
            except Exception as exc:
                raise SystemExit

            if data == b'':
                print('Server disconnected')
                raise SystemExit

            author, content = utils.readmsg(data)
            print('received tcp from', author, ":", content)

        if udp_sock in ready_socks:
            data, _ = udp_sock.recvfrom(1024)
            author, content = utils.readmsg(data)
            print('received udp from', author, ":", content)

        if mcast_sock in ready_socks:
            data, _ = mcast_sock.recvfrom(1024)
            author, content = utils.readmsg(data)
            print('received multicast from', author, ":", content)


if __name__ == '__main__':
    print('Python Chat Client')

    nickname = input('Choose a nickname: ')

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    try:
        tcp_sock.connect(config.server_address)
    except ConnectionRefusedError:
        print('Server unavailable')
        raise SystemExit
    _, tcp_port = tcp_sock.getsockname()

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_sock.bind(('', tcp_port))

    mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mcast_sock.bind(('', config.multicast_port))

    group = socket.inet_aton(config.multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    thread = Thread(target=receive, args=(tcp_sock, udp_sock, mcast_sock), daemon=True)
    thread.start()

    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            tcp_sock.close()
            udp_sock.close()
            mcast_sock.close()
            raise SystemExit
        if not line:
            continue

        if line.startswith('/'):
            first, *rest = line.split(' ', 1)
            command = first[1:].lower()
            message = ''.join(rest)
        else:
            command, message = None, line

        if command in ('q', 'quit', 'exit'):
            tcp_sock.close()
            udp_sock.close()
            mcast_sock.close()
            raise SystemExit

        data = utils.makemsg(nickname, message)
        if command is None or command in ('t', 'tcp'):
            tcp_sock.sendall(data)
        elif command in ('u', 'udp'):
            udp_sock.sendto(data, config.server_address)
        elif command in ('m', 'mcast', 'multicast'):
            mcast_sock.sendto(data, (config.multicast_group, config.multicast_port))
        else:
            print("invalid command")
