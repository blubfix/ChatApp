# Project Server implemented
# Imports needed for Server

import socket
import time


class Sever:

    # Constructor for Class Server
    def __init__(self, s_sockets, s_receive, c_addresses, s_leader):
        super(Sever, self).__init__()
        self.s_leader = s_leader
        self.c_addresses = c_addresses
        self.s_receive = s_receive
        self.s_sockets = s_sockets


def udp_sockets_server():
    # UDP-socket of server
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_socket.bind(('', 0))


def client_listener():
    # buf size oriented on whatsapp as it is as big as 1 kb
    bufferSize = 1024

    # UDP socket for listener
    client_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_listener_socket.bind(('', 0))
    print(str(client_listener_socket))

    while True:
        try:
            message = client_listener_socket.recvfrom(bufferSize)
            print(message)
            address = (message.split(','))[1]
            print(address)

        except:
            pass


def heartbeat_listener():
    # UDP socket for heartbeat listener
    heartbeat_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    heartbeat_listener_socket.bind(('', 0))


def heartbeat():
    # Heartbeat socket
    heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    heartbeat_socket.bind(('', 0))


if __name__ == '__main__':
    client_listener()
