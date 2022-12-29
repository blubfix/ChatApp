# This Python file contains the class Server and a few variables that are needed
# Imports needed for Server
import socket

# Ports and other needed variables
# buf size oriented on whatsapp as it is as big as 1 kb
buffer_size = 1024

# Port for broadcast listener, waiting for a clients message
client_listener_port = 49153

# Port where to send success and error messages with tcp
tcp_answer_port = 50153

# Port for sending messages
send_message_to_port = 50154
receive_message_request_port = 50155
receive_the_message_with_tcp_port = 50156

# Port for system exist communication
system_exit_port_tcp = 51153
system_exit_port_udp = 51154

# The own IP address
host = socket.gethostname()
my_own_ip_address = socket.gethostbyname(host)

# multicast group ip. This port is used because it is in range of 224.0.1.0 - 238.255.255.255 and should be used for
# multicast IPs that are used over the internet
multicast_group_ip = '224.0.2.0'


# The Server class contains the functionalities of the server

class Server:

    # the __init__ method for Class Server comparable to constructor
    def __init__(self):
        self.user_list = []  # List of available Chat Partners
        self.server_list = []  # List with the other Servers
        self.leader = False  # Needed to enable leader methods and to make sure only the leader handles Round Robin
        self.user_address_list = []
        self.user_name_list = []

    # The method update_list is used to send the updated user list to all others servers in the distributed system
    def update_list(self):
        pass

    def receive_list_update(self):
        pass

    # This method is used to receive the message of a client that wants to sent a message to one or more other Clients
    def tcp_answer_and_receive_messages_for_other_clients(self):
        # build up TCP socket
        tcp_socket_for_messages = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket_for_messages.bind((my_own_ip_address, receive_the_message_with_tcp_port))
        tcp_socket_for_messages.listen()

        # set timeout to 5
        timeout_for_client_answer = 5
        tcp_socket_for_messages.settimeout(timeout_for_client_answer)

        new_socket_for_connection, address_of_client = tcp_socket_for_messages.accept()
        while True:
            try:
                data_with_message = new_socket_for_connection.recv(buffer_size)
                str_data_with_message = str(data_with_message)





            finally:
                pass

    """server_answer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_answer_socket.bind((my_own_ip_address, server_answer_port_tcp))
    server_answer_socket.listen()
    timeout_for_serverconnection = 5
    server_answer_socket.settimeout(timeout_for_serverconnection)

    connection, address = server_answer_socket.accept()
    while True:
        try:
            # get data from Server
            data = connection.recv(buffer_size)
            str_server_answer_for_request = str(data)

            # split message for output on consol
            split_server_answer_for_request = str_server_answer_for_request.split("'")
            server_message = split_server_answer_for_request[1]

            # split message for identity
            bye = 'Bye'
            if bye not in server_message:
                split_server_answer_for_identity = server_message.split(" ")
                self.own_identity = split_server_answer_for_identity[1]

            output = str(server_message)
            server_answer_socket.close()
            return output
        finally:
            # Close connection to server
            server_answer_socket.close()

except socket.timeout:

return server_timeout_message"""

    # Method is used for message response via tcp to a client action
    def answer_client_via_tcp(self, address, message):
        # build up the TCP socket
        answer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        answer_socket.connect((address, tcp_answer_port))
        answer_socket.setblocking(False)

        # the given answer for client is sent
        send_answer = message.encode('ascii')
        answer_socket.sendall(send_answer)
        answer_socket.close()

    # The method implements a UDP socket that waits for the broadcast from clients and makes it possible to process
    # client requests further.

    def client_listener(self):
        # UDP socket for listener
        client_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_listener_socket.bind(('', client_listener_port))
        print(str(client_listener_socket))

        while True:
            try:
                # Receives identification messages from clients
                client_identification_message = client_listener_socket.recvfrom(buffer_size)

                # Process Data from Clients that only the name and the IP-Address is left
                str_client_identification_message = str(client_identification_message)
                split_identification_message = str_client_identification_message.split("'")
                identity_name = split_identification_message[1]
                identity_address = split_identification_message[3]
                user_identity = (identity_name, identity_address)
                success_msg_for_client = 'Hello {}, your identification was successful'.format(identity_name)
                error_msg_for_client = 'Excuse me, your name is already used, please tryout another name'

                # load the data into a list containing all data of currently possible users and amke sure this list is
                # reliable, make sure it's not possible to have wrong data in this List
                if identity_address not in self.user_address_list and identity_name not in self.user_name_list:
                    self.user_address_list.append(identity_address)
                    self.user_name_list.append(identity_name)
                    self.user_list.append(user_identity)
                    self.update_list()
                    print(self.user_list)
                    self.answer_client_via_tcp(identity_address, success_msg_for_client)
                elif identity_name not in self.user_list and identity_address in self.user_address_list:
                    for element in self.user_list:
                        if element in self.user_list:
                            self.user_list.remove(element)
                            self.user_list.append(user_identity)
                            self.update_list()
                            print(self.user_list)
                            self.answer_client_via_tcp(identity_address, success_msg_for_client)
                            break
                        else:
                            pass
                else:
                    print(user_identity)
                    print(self.user_list)
                    self.answer_client_via_tcp(identity_address, error_msg_for_client)
            finally:
                pass

    # This method is used to receive a initial message by Clients, if they want to chat with other users
    def message_receiver_handler(self):
        message_receiver_handler_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message_receiver_handler_socket.bind(('', receive_message_request_port))
        print(str(message_receiver_handler_socket))

        while True:
            try:
                message_receiver_message = message_receiver_handler_socket.recvfrom(buffer_size)

                # prepare the message to get the user that should receive a message and the address of the origin
                str_message_receiver_message = str(message_receiver_message)
                str_message_receiver_message = str_message_receiver_message.split("'")
                list_of_receiver = str_message_receiver_message[1]
                sender_ip_of_message = str_message_receiver_message[3]

                # split the list of receiver to make the single names comparable with the list of users
                splitted_list_of_receiver = list_of_receiver.split(',')
                filtered_list_of_receiver = [x for x in splitted_list_of_receiver if x]
                test_list_for_comparison = []

                # declare the both messages that are needed for response to the client
                success_message_for_receiver = 'The users exist' + ',' + str(my_own_ip_address)
                error_message_for_receiver = 'The users doesnt exist'

                for name in self.user_name_list:
                    if name in filtered_list_of_receiver:
                        test_list_for_comparison.append(name)
                    else:
                        pass

                if test_list_for_comparison == filtered_list_of_receiver:
                    self.answer_client_via_tcp(sender_ip_of_message, success_message_for_receiver)
                    print('its in here')
                    self.tcp_answer_and_receive_messages_for_other_clients()
                else:
                    print('test2')
                    self.answer_client_via_tcp(sender_ip_of_message, error_message_for_receiver)

            finally:
                pass

    # When the Client stops running it has to be removed from the user list
    def client_listener_for_system_exit(self):
        # build up the socket that awaits a message from client
        client_exit_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_exit_socket.bind(('', system_exit_port_udp))
        print(str(client_exit_socket))

        while True:
            try:
                # Receives exit messages from clients
                client_exit_message = client_exit_socket.recvfrom(buffer_size)
                str_client_exit_message = str(client_exit_message)
                split_exit_message = str_client_exit_message.split("'")
                exit_message_text = split_exit_message[1]
                identity_name_split = exit_message_text.split(',')
                identity_name = identity_name_split[0]
                identity_address = split_exit_message[3]
                user_identity = (identity_name, identity_address)
                bye_message = 'Bye'

                if user_identity in self.user_list and self.user_list:
                    self.user_list.remove(user_identity)
                    self.user_name_list.remove(identity_name)
                    self.user_address_list.remove(identity_address)
                    self.update_list()
                    test_message = 'The user {} is deleted'.format(identity_name)
                    print(test_message)
                    self.answer_client_via_tcp(identity_address, bye_message)
                else:
                    error_message_for_exit = 'Couldnt find the user {}'.format(identity_name)
                    self.answer_client_via_tcp(identity_address, error_message_for_exit)

            finally:
                pass

    def udp_sockets_server(self):
        # UDP-socket of server
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server_socket.bind(('', 0))

    def heartbeat_listener(self):
        # UDP socket for heartbeat listener
        heartbeat_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        heartbeat_listener_socket.bind(('', 0))

    def heartbeat(self):
        # Heartbeat socket
        heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        heartbeat_socket.bind(('', 0))
