import sys
from socket import *
import socket

try:

    # will scan ports between 49152 to 65535 because thats the range of dynamic ports
    for port in range(49152, 65535):
        s = udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sender = 'XYZ Hallo Welt'
        sender_bytes = sender.encode('ascii')
        s.sendto(sender_bytes, ('255.255.255.255', port))
        s.close()

except KeyboardInterrupt:
    print('\n Exiting Program !')
    sys.exit()
except socket.gaierror:
    print('\n Hostname Could Not Be Resolved !')
    sys.exit()
except socket.error:
    print('\ Server not responding !')
    sys.exit()