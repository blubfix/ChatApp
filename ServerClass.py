# This Python file contains the class Server and a few variables that are needed
# Imports needed for Server
from socket import *
import socket
import sys
from time import time, ctime, sleep

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

# Port for list update communication
list_update_broadcast_port = 52551

# The own IP address
host = socket.gethostname()
my_own_ip_address = socket.gethostbyname(host)

# multicast group ip. This port is used because it is in range of 224.0.1.0 - 238.255.255.255 and should be used for
# multicast IPs that are used over the internet
multicast_group_ip = '224.1.2.1'

# Multicast Port
multicast_port_for_messages = 52153


# The Server class contains the functionalities of the server

class Server:

    # the __init__ method for Class Server comparable to constructor
    def __init__(self):
        self.user_list = []  # List with tupel of available users including name and address
        self.server_list = []  # List with the other Servers
        self.leader = False  # Needed to enable leader methods and to make sure only the leader handles Round Robin
        self.user_address_list = []  # A list with the addresses of users that are available
        self.user_name_list = []  # A list with the user names that are available
        self.list_of_receiver_of_messages = []  # needed to see who receives a message

    # The method update_list is used to send the updated user list to all others servers in the distributed system
    def update_list(self):
        update_list_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        update_list_send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        send_string_with_user = ''

        try:
            for element in self.user_list:
                send_string_with_user = send_string_with_user + "'" + element
            user_list_in_ascii = send_string_with_user.encode('ascii')
            update_list_send_socket.sendto(user_list_in_ascii, ('255.255.255.255', list_update_broadcast_port))
            send_string_with_user = ''

        except:
            pass

    def receive_list_update(self):
        pass

    def multicast_message_for_receiver(self, message):

        # To ensure that a multicast message is not accidentally sent across the internet, a maximum number of server
        # hops is set. In this case, the maximum is 2 hops.
        ttl = 2

        multicast_socket_for_messages = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket_for_messages.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        send_message = message.encode('ascii')
        addresses_to_send_to = ''

        for element in self.list_of_receiver_of_messages:
            addresses_to_send_to = element[1]
            multicast_socket_for_messages.sendto(send_message, (addresses_to_send_to, multicast_port_for_messages))
            print(addresses_to_send_to)
            addresses_to_send_to = ''

        self.list_of_receiver_of_messages = []

    # This method is used to receive the message of a client that wants to sent a message to one or more other Clients
    def tcp_answer_client_about_receivers_are_available(self):
        # build up TCP socket
        tcp_socket_for_messages = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket_for_messages.bind((my_own_ip_address, receive_the_message_with_tcp_port))
        tcp_socket_for_messages.listen()

        # set timeout to 10
        timeout_for_client_answer = 10
        tcp_socket_for_messages.settimeout(timeout_for_client_answer)

        new_socket_for_connection, address_of_client = tcp_socket_for_messages.accept()
        while True:
            try:
                data_with_message = new_socket_for_connection.recv(buffer_size)
                str_data_with_message = str(data_with_message)
                str_data_with_message = str_data_with_message.split("'")
                prepared_message = str_data_with_message[1]
                print(prepared_message)

                # was auch immer mit der Nachricht gemacht wird, dannach muss diese entsprechende Funktion aufgerufen werden
                self.multicast_message_for_receiver(prepared_message)
                break
            except:
                print('Fehler Zeile 116')


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

        # This method is used to have a better structured code. It is used when a user is not known for the server

    def user_completely_unknown(self, identity, address, name, msg):
        self.user_address_list.append(address)
        self.user_name_list.append(name)
        self.user_list.append(identity)
        self.update_list()
        print(self.user_list)
        self.answer_client_via_tcp(address, msg)

    # achtung noch nicht fertig!
    def only_user_address_is_known(self, identity, address, name, msg):
        outside_loop_variable = ()

        for element in self.user_list:
            str_element = str(element)
            element_guts_list = str_element.split("'")
            user_list_element_name = str(element_guts_list[1])
            user_list_element_address = str(element_guts_list[3])

            if address == user_list_element_address:
                self.user_list.remove(element)
                self.user_name_list.remove(user_list_element_name)
                self.user_name_list.append(name)
                self.user_list.append(identity)
                self.update_list()
                print(self.user_list)
                self.answer_client_via_tcp(address, msg)
                break
            else:
                pass

    # The method implements a UDP socket that waits for the broadcast from clients and makes it possible to process
    # Client requests further.

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

                # Different specific error and success messages
                success_msg_for_client = 'Hello {}, your identification was successful'.format(identity_name)
                success_msg_changed_name = 'Hello {}, your name was updated'.format(identity_name)
                error_msg_for_client = 'Excuse me, your name is already used, please tryout another name'
                error_msg_already_logged_in = 'Excuse me, your already logged in'
                general_error = 'Excuse me, an Error occurred'

                # load the data into a list containing all data of currently possible users and amke sure this list is
                # reliable, make sure it's not possible to have wrong data in this List

                # Fehler hier, es ist möglich das ein Name zwei mal vorkommt
                # If the user address list is empty or just has 1 tupel inside, its not needed to iterate through
                if len(self.user_list) < 1:

                    # If the incoming address and name arent in any list do following
                    if identity_address not in self.user_address_list and identity_name not in self.user_name_list:
                        self.user_completely_unknown(user_identity, identity_address,
                                                     identity_name, success_msg_for_client)

                    # If the identity name is in no list but the address occurs in list do following
                    elif identity_name not in self.user_name_list and identity_address in self.user_address_list:
                        self.only_user_address_is_known(user_identity, identity_address,
                                                        identity_name, success_msg_changed_name)

                    # If the identity is the same, the user is already logged in do following
                    elif identity_name in self.user_name_list and identity_address in self.user_address_list:
                        print(self.user_list)
                        self.answer_client_via_tcp(identity_address, error_msg_already_logged_in)

                    # If any other failure occurs just send a general error message
                    else:
                        print(self.user_list)
                        self.answer_client_via_tcp(identity_address, general_error)

                # if there is more than one tupel inside user_list, it has to be iterated through, so the code has to be
                # different, because the in statement just works out for the first tupel and not for a whole list
                elif len(self.user_list) >= 1:
                    # The decide string is extended by the user_list with each iteration.
                    # This creates a string that can be examined for a substring and a message is sent according to
                    # the substring that appears. This makes it possible to iterate through the entire user_list and
                    # make sure that no name or address can get into the list more than once.
                    # Thus the list remains reliable and can be used as an address book for the second client
                    # functionality.
                    decide_string = ''
                    just_append = '1'
                    remove_and_append = '2'
                    name_already_used = '3'
                    dont_append = '4'

                    for user_list_element in self.user_list:
                        str_user_list_element = str(user_list_element)
                        splitted_user_list_element = str_user_list_element.split("'")
                        user_list_element_name = str(splitted_user_list_element[1])
                        user_list_element_address = str(splitted_user_list_element[3])

                        # If the incoming address and name arent in any list do following
                        if identity_name != user_list_element_name and identity_address != user_list_element_address:
                            decide_string = decide_string + just_append

                        # If the identity name is in no list but the address occurs in list do following
                        elif identity_name != user_list_element_name and identity_address == user_list_element_address:
                            decide_string = decide_string + remove_and_append
                            break

                        # If a name is already used but the address is not known do following
                        elif identity_name == user_list_element_name and identity_address != user_list_element_address:
                            decide_string = decide_string + name_already_used
                            break

                        # If the identity is the same, the user is already logged in do following
                        elif identity_name == user_list_element_name and identity_address == user_list_element_address:
                            decide_string = decide_string + dont_append
                            break

                    # self.answer_client_via_tcp(identity_address, success_msg_for_client)
                    if dont_append in decide_string:
                        print(decide_string)
                        print(self.user_list)
                        decide_string = ''
                        self.answer_client_via_tcp(identity_address, error_msg_already_logged_in)

                    elif remove_and_append in decide_string:
                        print(decide_string)
                        decide_string = ''
                        self.only_user_address_is_known(user_identity, identity_address, identity_name,
                                                        success_msg_changed_name)

                    elif name_already_used in decide_string:
                        print(decide_string)
                        decide_string = ''
                        print(self.user_list)
                        self.answer_client_via_tcp(identity_address, error_msg_for_client)

                    else:
                        print(decide_string)
                        decide_string = ''
                        self.user_completely_unknown(user_identity, identity_address, identity_name,
                                                     success_msg_for_client)

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
                print(sender_ip_of_message)

                # split the list of receiver to make the single names comparable with the list of users
                splitted_list_of_receiver = list_of_receiver.split(',')
                filtered_list_of_receiver = [x for x in splitted_list_of_receiver if x]
                print(filtered_list_of_receiver)
                test_list_for_comparison = []

                # declare the both messages that are needed for response to the client
                success_message_for_receiver = 'The users exist' + ',' + str(my_own_ip_address)
                error_message_for_receiver = 'The users doesnt exist'

                for element in self.user_list:
                    for name in splitted_list_of_receiver:
                        if name in element:
                            test_list_for_comparison.append(name)
                            self.list_of_receiver_of_messages.append(element)
                        else:
                            print('Fehler in Zeile 352')

                if test_list_for_comparison == filtered_list_of_receiver:
                    self.answer_client_via_tcp(sender_ip_of_message, success_message_for_receiver)
                    self.tcp_answer_client_about_receivers_are_available()
                else:
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
        debug = True
        server_ip = '127.0.0.1'  # local host, just for testing
        heartbeat_port = 49154
        heartbeat_timer = 10  # number of seconds between heartbeats

        if len(sys.argv) > 1:
            server_ip = sys.argv[1]
        if len(sys.argv) > 2:
            heartbeat_port = sys.argv[2]

        heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("PyHeartBeat client sending to IP %s , port %d" % (server_ip, heartbeat_port))

        while 1:
            heartbeat_socket.sendto(str.encode("Thump!"), (server_ip, heartbeat_port))
            if debug:
                print("Time: %s" % ctime(time()))
            sleep(heartbeat_timer)
