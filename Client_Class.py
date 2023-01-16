# This Python file contains the class Client and a few variables that are needed
# Imports needed for Client
import asyncio
import struct
import sys
import threading
from socket import *
import socket
import time

# Ports that are needed and other global variables needed
# buffer size oriented on whatsapp as it is as big as 1 kb
buffer_size = 1024

# Port for Server answer
server_answer_port_tcp = 50199

# Port for system Exit Message
system_exit_port_tcp = 51153

# Port for UDP Broadcast to let the system know that the client wants to exit and to open a connection between the
# Client and the Server that is responsible to manage the exit
system_exit_port_udp = 51154

# Port for dynamic discovery Broadcast
dynamic_discovery_portNr = 49153

# Port for get and send multicast messages
get_multicast_messages_port = 50154
send_multicast_request_port = 50155
send_the_message_to_tcp_port = 50156

# the own Host and IP address
host = socket.gethostname()
my_own_ip_address = socket.gethostbyname(host)

# multicast group ip. This port is used because it is in range of 224.0.1.0 - 238.255.255.255 and should be used for
# multicast IPs that are used over the internet
multicast_group_ip = '224.1.2.1'

# Multicast Port
multicast_port_for_messages = 52153
multicast_message_buffer = 10240

# general server timeout is 5 seconds
general_timeout = 5

# general server timeout message
server_timeout_message = 'Couldnt build up a connection to server.'
error_message_for_receiver = 'The users doesnt exist'

# success messages
success_message_for_receiver = 'The users exist'
system_exit_success_message = 'Your user was deleted on server'
no_identity_message = 'You dont own an identity'


class Client:
    stop_event = threading.Event()

    def __init__(self):
        self.connection_with_server = False
        self.own_identity = None
        self.name_of_receiver = ''

    def delay_time_function(self):
        time.sleep(1)

    def add_receiver(self):
        self.name_of_receiver = self.name_of_receiver + ',' + input('What is the name of the receiving person: ')
        response = input('Do you want to sent the message to another person? (y/n) ')

        # if y was typed in, the method calls itself again to add another name
        if response.lower() == 'y':
            self.add_receiver()

        # if n was typed in the method returns the name string
        elif response.lower() == 'n':
            return self.name_of_receiver
        else:
            # Code, der ausgeführt wird, wenn die Antwort weder "ja" noch "nein" ist
            print('invalid character, please enter y for yes or n for no')

    # This method is used to timeout after x seconds of no response of the server
    async def timeout(self, response_timout):
        # wait for response timeout
        await asyncio.sleep(response_timout)

        # if timeout is happening, print the timeout message
        print(server_timeout_message)

    def method_to_write_message(self):
        message_for_other_users = input('Please enter the message you would like to send to one or more other users ')
        return message_for_other_users

    # This method is used to send the message that should be sent to other users to the server.
    # The server is responsible to send this message to the other users
    def method_to_send_messages(self, address, message):
        send_the_message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_the_message_socket.connect((address, send_the_message_to_tcp_port))
        send_the_message_socket.setblocking(False)

        send_message = message.encode('ascii')
        send_the_message_socket.sendall(send_message)
        send_the_message_socket.close()

    # Method that is needed for responding to tcp message sent by server to a Client
    def handle_server_answers(self):
        try:
            print("handle_server_answers")
            server_answer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_answer_socket.bind(('', server_answer_port_tcp))
            server_answer_socket.listen()
            print("server_answer_socket binded")
            timeout_for_serverconnection = 5
            server_answer_socket.settimeout(timeout_for_serverconnection)

            connection, address = server_answer_socket.accept()
            while True:
                try:
                    # get data from Server
                    print("handle_server_answers while true")
                    data = connection.recv(buffer_size)
                    str_server_answer_for_request = str(data)
                    print("data")
                    # split message for output on consol
                    split_server_answer_for_request = str_server_answer_for_request.split("'")
                    server_message = split_server_answer_for_request[1]
                    print(server_message)
                    # messages to be checked
                    bye = 'Bye'
                    exist_message = 'The user exist'

                    if bye not in server_message:
                        if exist_message in server_message:
                            print(exist_message)
                        else:
                            print("bye not in server and exist message not in server_message")
                            split_server_answer_for_identity = server_message.split(" ")
                            self.own_identity = split_server_answer_for_identity[1]
                    elif success_message_for_receiver in server_message:
                        print('yes it does work')


                    output = str(server_message)
                    server_answer_socket.close()
                    return output
                except Exception as e:
                    print("Exception in: handle_server_answer")
                    print(e)

        except Exception as e:
            print("Exception in: handle_server_answer outer try/except")
            print(e)

    # As long as the identity isn't changed it is your identity for the Servers
    # if the identity get changed the servers change it as well after receiving the message with the new name
    def get_acquainted_with_server(self):
        # makes it possible for the User to give his own identity to the Servers and enables a communication
        # with himself, because other users can find that name and send a message to this name
        identity = input('What is your identity name: ')
        broadcast_discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_discovery_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        try:
            sender_bytes = identity.encode('ascii')
            broadcast_discovery_socket.sendto(sender_bytes, ('255.255.255.255', dynamic_discovery_portNr))
            broadcast_discovery_socket.close()
            server_message = self.handle_server_answers()
            print('\n')
            print(server_message)
            print('\n')
        finally:
            pass

    # This method enables to chat with other users, if you know their name.
    # It is possible to send a message to one other user, if you know his identity name, this is what you ask for in
    # udp request and you get an answer by server via tcp. After that you can send the message and it will be sent to
    # the other user
    def send_a_message_to_other_clients(self):
        # The user should type in the message he want to send to the other users
        message_to_be_sent = self.method_to_write_message()

        # The user should type in the name of the users he wants the message to be sent to
        self.add_receiver()
        receiver_name_string = self.name_of_receiver

        # Build up the socket for the
        send_message_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_message_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        try:
            # Send the request with the list of possible receiver to the server for check the receivers
            print("start communication")
            sender_bytes = receiver_name_string.encode('ascii')
            send_message_socket.sendto(sender_bytes, ('255.255.255.255', send_multicast_request_port))
            print("send_message_socket.sendto")
            send_message_socket.close()
            print("socket close")
            self.name_of_receiver = ''
            server_message = self.handle_server_answers()
            print("handle server answers done")

            # Check the message of the server
            if success_message_for_receiver in server_message:
                print("success_message_for_receiver in server_message")
                # Get the address of the server out of the server message
                splitted_server_message = server_message.split(',')
                address_of_server_to_communicate = splitted_server_message[1]

                # Send the message that should be sent to the other users to the server, that performs the multicast
                self.method_to_send_messages(address_of_server_to_communicate, message_to_be_sent)
            elif server_message == error_message_for_receiver:
                print("server_message == error_message_for_receiver")
                print(server_message)
            else:
                print("timeout")
                print(server_timeout_message)
                
        except Exception as e:
            print("Exception in: send_a_message_to_other_clients")
            print(e)


    # This method is used to get multicast messages by other users
    def get_message_by_other_user_multicast(self):
        print('Listener for message is active')
        multicast_get_message_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_get_message_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        multicast_get_message_socket.bind(('', multicast_port_for_messages))
        mreq = struct.pack('4sl', socket.inet_aton(multicast_group_ip), socket.INADDR_ANY)

        multicast_get_message_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            try:
                message = multicast_get_message_socket.recv(multicast_message_buffer)
                if message !=b'':
                    str_message = str(message)
                    str_message_splitted = str_message.split("'")
                    print_message = str_message_splitted[1]
                    print('')
                    print("You received a new message:\n")
                    print(print_message)

            except:
                print("Error while receiving message")
        

    # This method is used to end the program and ensure that the identity is removed from user List on server
    def end_the_program(self):
        if self.own_identity is None:
            print('\n')
            print(no_identity_message)
            print('\n')
        else:
            # Ask for server ip address with udp Broadcast
            system_exit_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            system_exit_socket_udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            system_exit_request = '{} want to exit!'.format(self.own_identity)
            system_exit_test_string = 'Bye'

            while True:
                try:
                    sender_bytes = system_exit_request.encode('ascii')
                    system_exit_socket_udp.sendto(sender_bytes, ('255.255.255.255', system_exit_port_udp))
                    system_exit_socket_udp.close()

                    for_exit_message = self.handle_server_answers()
                    if system_exit_test_string in for_exit_message:
                        print('\n')
                        print('End program was successful')
                        print('\n')
                        break
                    else:
                        print('\n')
                        print('End program wasnt successful, please try again!')
                        print('\n')
                        break
                finally:
                    break

    def ui(self):
        while True:

            print('please select an option:')
            print('')
            print('1. Create an identity for the Server and other users ')
            print('2. Chat with an other user')
            print('3. Disconnect from server')
            print('')

            choice = input('Your choice: ')
            print('')
            if choice == '1':
                self.get_acquainted_with_server()
            elif choice == '2':
                self.send_a_message_to_other_clients()
            elif choice == '3':
                self.stop_event.set()
                #print("Stop val")
                #print(self.stop_event.is_set())
                self.end_the_program()
                break
