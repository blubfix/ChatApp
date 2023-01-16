# This Python file contains the class Server and a few variables that are needed
# Imports needed for Server
import json
from socket import *
import socket
import sys
from time import time, ctime, sleep
import struct

# Ports and other needed variables
# buf size oriented on whatsapp as it is as big as 1 kb
buffer_size = 1024

# Port for broadcast listener, waiting for a clients message
client_listener_port = 49153

# Port where to send success and error messages with tcp
tcp_answer_port = 50101

# Port for sending messages
send_message_to_port = 50154
receive_message_request_port = 50155
receive_the_message_with_tcp_port = 50156

# Port for system exist communication
system_exit_port_tcp = 51153
system_exit_port_udp = 51154

# Port for lcr
lcr_port = 56150

# Port for list update communication
list_update_broadcast_port = 52551
server_list_update_broadcast_port = 52552

# The own IP address
host = socket.gethostname()
my_own_ip_address = socket.gethostbyname(host)

# multicast group ip. This port is used because it is in range of 224.0.1.0 - 238.255.255.255 and should be used for
# multicast IPs that are used over the internet
multicast_group_ip = '224.1.2.1'
multicast_neighbour_group_ip = '224.1.3.1'

# Multicast Port
multicast_port_for_messages = 52153
multicast_port_for_neighbours = 52154
multicast_message_buffer = 10240


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
        self.lastMessageTime = time()
        self.actualTime = 0
        self.my_neighbour = ''
        self.election_message = {"mid": my_own_ip_address, "isLeader": False}
        self.lcrActiveFlag=False

    def detection_of_dead_leader(self):
        while True:
            #print("leader" + str(self.leader) +" LCR ACTIVE: " + str(self.lcrActiveFlag))
            
            if self.leader != True:
                if self.lcrActiveFlag != True:
                    self.actualTime = time()
                    
                    leader_death_time = 15

                    if ((self.actualTime - self.lastMessageTime) >= leader_death_time):
                        print("WASTED")
                        self.server_list=[]
                        self.server_list.append(my_own_ip_address)
                        self.my_neighbour=[]
                        sleep(3)
                        ring = self.form_a_ring_with_server_addresses()
                        my_ip = my_own_ip_address
                        self.my_neighbour = self.get_the_left_neighbour(ring, my_ip)

                        self.send_message_to_neighbour(self.my_neighbour, ring)

                        self.start_lcr()

    def neighbour_message_listener(self):
        multicast_neighbour_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_neighbour_listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        multicast_neighbour_listener_socket.bind(('', multicast_port_for_neighbours))
        mreq = struct.pack('4sl', socket.inet_aton(multicast_neighbour_group_ip), socket.INADDR_ANY)

        multicast_neighbour_listener_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            try:
                message = multicast_neighbour_listener_socket.recv(multicast_message_buffer)
                str_message = str(message)
                #print("Listener ____")
                #print(message)
                neighbour_list = str_message.replace('b', "")
                # print(neighbour_list)
                neighbour_list = neighbour_list.replace('"', "")
                neighbour_list = neighbour_list.replace("'", "")

                neighbour_list = neighbour_list.replace(']', "")
                # print(temp2_user_list)
                neighbour_list = neighbour_list.replace("[", "")

                #print(neighbour_list)

            except:
                pass

    def send_message_to_neighbour(self, ip, message):
        ttl = 2

        multicast_socket_for_neighbours = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket_for_neighbours.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        stringMessage = str(message)
        send_message = stringMessage.encode('ascii')

        multicast_socket_for_neighbours.sendto(send_message, (ip, multicast_port_for_neighbours))
        addresses_to_send_to = ''

    def form_a_ring_with_server_addresses(self):
        binary_ring_from_server_list = sorted([socket.inet_aton(element) for element in self.server_list])
        # print(binary_ring_from_server_list)

        ip_ring = [socket.inet_ntoa(ip) for ip in binary_ring_from_server_list]
        # print(ip_ring)
        return ip_ring

    def get_the_left_neighbour(self, ring, own_ip, direction='left'):
        # print(ring[0])
        own_index = ring.index(own_ip) if own_ip in ring else -1
        if own_index != -1:
            if direction == 'left':
                if own_index + 1 == len(ring):

                    return ring[0]
                else:
                    return ring[own_index + 1]
            else:
                if own_index == 0:
                    return ring[len(ring) - 1]
                else:
                    return ring[own_index - 1]
        else:
            return None

    def start_lcr(self):
        self.server_list=[]
        
        sleep(3)
        lcr_begin_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        x = self.election_message
        #print(json.dumps(x))
        lcr_begin_socket.sendto((json.dumps(self.election_message).encode()), (self.my_neighbour,lcr_port))
        print('lcr was started')
        self.lcrActiveFlag=True
        print(self.lcrActiveFlag)
        pass

    def lcr_listener_and_execution(self):
        lcr_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        lcr_listener_socket.bind((my_own_ip_address, lcr_port))
        participant = False
        leader_uid = ''
        while self.leader != True: 

           
            if(self.lcrActiveFlag == True):
                print("lcr active")
                if self.my_neighbour =='':
                    self.leader=True
                else:
                    data, address = lcr_listener_socket.recvfrom(buffer_size)
                    message_with_election = json.loads(data.decode())
                    #print(message_with_election)
                    if message_with_election['isLeader']:
                        print("isLeader^1")
                        #print(self.my_neighbour)
                        leader_ip = message_with_election['mid']
                        participant = False
                        lcr_listener_socket.sendto((json.dumps(message_with_election).encode()), (self.my_neighbour,lcr_port))
                        self.lcrActiveFlag = False

                    

                    if message_with_election['mid']<my_own_ip_address and not participant:
                        print("mid^1")
                        #print(self.my_neighbour)
                        new_election_message = self.election_message
                        participant = True
                        lcr_listener_socket.sendto((json.dumps(new_election_message).encode()), (self.my_neighbour,lcr_port))

                    elif message_with_election['mid']>my_own_ip_address:
                        print("mid^2")
                        print(message_with_election['mid'])
                        #print(self.my_neighbour)
                        participant = True
                        lcr_listener_socket.sendto((json.dumps(message_with_election).encode()), (self.my_neighbour,lcr_port))
                        self.lcrActiveFlag=False
                    elif message_with_election['mid']==my_own_ip_address:
                        print("mid^3")
                        #print(self.my_neighbour)
                        leader_uid = my_own_ip_address
                        new_election_message = {"mid": my_own_ip_address, "isLeader": True}
                        participant = False
                        lcr_listener_socket.sendto((json.dumps(new_election_message).encode()), (self.my_neighbour,lcr_port))
                        print("leader")
                        print(self.leader)
                        self.leader=True
                        print("leader")
                        print(self.leader)
                        self.lcrActiveFlag = False
                        print("leader true")
                        
                    else:
                        print("its smth else")


    # The method update_list is used to send the updated user list to all others servers in the distributed system
    def update_user_list(self):
        starttime = time()
        while True:
            if self.leader:

                if len(self.user_list) != 0:
                    update_list_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    update_list_send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

                    try:
                        send_string_with_user = ''.join(str(element) for element in self.user_list)
                        user_list_in_ascii = send_string_with_user.encode('ascii')
                        update_list_send_socket.sendto(user_list_in_ascii, ('255.255.255.255', list_update_broadcast_port))
                        send_string_with_user = ''
                        print('Liste mit Inhalt versendet')

                    except:
                        print('update List Error')

                else:
                    update_list_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    update_list_send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                    try:
                        send_string_with_user = '1'
                        user_list_in_ascii = send_string_with_user.encode('ascii')
                        update_list_send_socket.sendto(user_list_in_ascii, ('255.255.255.255', list_update_broadcast_port))
                        send_string_with_user = ''
                        print('Leere Liste versendet')
                    except:
                        pass
                sleep(5.0 - ((time() - starttime) % 5.0))

    # This method is used to listen to the user list that is sent by the leader every 10 second
    def receive_list_update(self):
        print('die socket hört jetzt auf den Broadcast')
        while True:
            if self.leader != True:

                list_update_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                list_update_listener_socket.bind(('', list_update_broadcast_port))

                while True:

                    # Receives identification messages from clients
                    user_list_update_ascii = list_update_listener_socket.recvfrom(buffer_size)

                    user_list_update_string = str(user_list_update_ascii[0])
                    meaningless_message = user_list_update_string.replace('b', '')
                    meaningless_message = meaningless_message.replace("'", "")
                    print(meaningless_message)
                    if meaningless_message == "1":
                        self.lastMessageTime = time()
                        print(1)
                    elif len(user_list_update_ascii) != 0 and user_list_update_string != '1':

                        self.lastMessageTime = time()

                        # print(user_list_update_string)
                        temp_user_list = user_list_update_string.replace('b"', "")
                        # print(temp_user_list)
                        temp_user_list = temp_user_list.replace(')"', ")")
                        # print(temp2_user_list)
                        temp_user_list = temp_user_list.replace(")(", "!")
                        temp_user_list = temp_user_list.replace("(", "")
                        temp_user_list = temp_user_list.replace(")", "")

                        # print(temp_user_list)
                        if "!" in temp_user_list:
                            temp4_user_list = temp_user_list.split("!")
                            for element in temp4_user_list:
                                user = element.split(", ")[0].replace("'", "")
                                ip = element.split(", ")[1].replace("'", "")
                                # print(user)
                                # print(ip)
                                if ip not in self.user_address_list and user not in self.user_name_list:
                                    user_list_tuple = (user, ip)
                                    print("thisthat")
                                    flag = False
                                    self.user_address_list.append(ip)
                                    self.user_name_list.append(user)
                                    self.user_list.append(user_list_tuple)

                                    # self.update_list()
                                    for element in self.user_list:
                                        print(element)

                        else:
                            user = temp_user_list.split(", ")[0].replace("'", "")
                            ip = temp_user_list.split(", ")[1].replace("'", "")
                            if ip not in self.user_address_list and user not in self.user_name_list:
                                user_list_tuple = (user, ip)
                                flag = False
                                self.user_address_list.append(ip)
                                self.user_name_list.append(user)
                                self.user_list.append(user_list_tuple)

                                # self.update_list()
                                for element in self.user_list:
                                    print(element)

    def update_server_list(self):
        starttime = time()

        while True:
            update_server_list_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            update_server_list_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            send_own_ip_string = str(my_own_ip_address)
            send_own_ip_ascii = send_own_ip_string.encode('ascii')
            update_server_list_socket.sendto(send_own_ip_ascii, ('255.255.255.255', server_list_update_broadcast_port))

            send_own_ip_string = ''

            sleep(2.0 - ((time() - starttime) % 2.0))

    def listen_to_server_list_update(self):
        startTime = time()
        while True:
            if((time()-startTime)>=10):
                startTime=time()
                self.server_list=[]
                self.server_list.append(my_own_ip_address)
            if self.leader != True:

                
                server_list_update_listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                server_list_update_listener_socket.bind(('', server_list_update_broadcast_port))

                while self.leader != True:
                    
                    try:
                        server_ip_ascii = server_list_update_listener_socket.recvfrom(buffer_size)
                        server_ip_string = str(server_ip_ascii)
                        # print(server_ip_string)
                        server_ip_split = server_ip_string.split("'")
                        # print(server_ip_split)
                        server_ip = server_ip_split[1]
                        # print(server_ip)

                        if (self.server_list == []):
                            self.server_list.append(server_ip)
                            print(self.server_list)

                        else:
                            decide_string = ''
                            just_append = '1'
                            dont_append = '2'

                            for server_list_element in self.server_list:
                                str_server_list_element = str(server_list_element)
                                if server_ip != str_server_list_element:
                                    decide_string = decide_string + just_append
                                else:
                                    decide_string = decide_string + dont_append
                                    break

                            if dont_append in decide_string:
                                print('list is up to date')
                                print(self.server_list)

                                pass

                            else:
                                self.server_list.append(server_ip)
                                print(self.server_list)

                    except:
                        pass

    def multicast_message_for_receiver(self, message):

        # To ensure that a multicast message is not accidentally sent across the internet, a maximum number of server
        # hops is set. In this case, the maximum is 2 hops.
        print("multicast_message_for_receiver")
        ttl = 2

        multicast_socket_for_messages = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multicast_socket_for_messages.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        send_message = message.encode('ascii')
        addresses_to_send_to = ''
        print("multicast socket")
        for element in self.list_of_receiver_of_messages:
            addresses_to_send_to = element[1]
            print(addresses_to_send_to)
            multicast_socket_for_messages.sendto(send_message, (addresses_to_send_to, multicast_port_for_messages))
            addresses_to_send_to = ''

        self.list_of_receiver_of_messages = []

    # This method is used to receive the message of a client that wants to sent a message to one or more other Clients
    def tcp_answer_client_about_receivers_are_available(self):
        # build up TCP socket
        print("tcp_answer_client_about_receivers_are_available")
        tcp_socket_for_messages = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket_for_messages.bind((my_own_ip_address, receive_the_message_with_tcp_port))
        tcp_socket_for_messages.listen()
        print("socket binded")
        # set timeout to 10
        timeout_for_client_answer = 10
        tcp_socket_for_messages.settimeout(timeout_for_client_answer)

        new_socket_for_connection, address_of_client = tcp_socket_for_messages.accept()
        print("New socket")
        while True:
            try:
                data_with_message = new_socket_for_connection.recv(buffer_size)
                print("data_with_message")
                print(data_with_message)
                str_data_with_message = str(data_with_message)
                str_data_with_message = str_data_with_message.split("'")
                prepared_message = str_data_with_message[1]
                print(prepared_message)

                # was auch immer mit der Nachricht gemacht wird, dannach muss diese entsprechende Funktion aufgerufen werden
                
                self.multicast_message_for_receiver(prepared_message)
                break
            except Exception as e:
                print('Error Line 116')
                print(e)

    # Method is used for message response via tcp to a client action
    def answer_client_via_tcp(self, address, message):
        print("answer_client_via_tcp")
        print(address)
        # build up the TCP socket
        answer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        answer_socket.connect((address, tcp_answer_port))
        answer_socket.setblocking(False)
        print("connection established")
        # the given answer for client is sent
        send_answer = message.encode('ascii')
        answer_socket.sendall(send_answer)
        answer_socket.close()
        print("answer socket closed")

        # This method is used to have a better structured code. It is used when a user is not known for the server

    def user_completely_unknown(self, identity, address, name, msg, flag):
        print("unknown user")
        self.user_address_list.append(address)
        self.user_name_list.append(name)
        self.user_list.append(identity)
        # self.update_list()
        print(self.user_list)
        if flag == True:
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
                print(self.user_list)
                self.answer_client_via_tcp(address, msg)
                break
            else:
                pass

    # The method implements a UDP socket that waits for the broadcast from clients and makes it possible to process
    # Client requests further.

    def client_listener(self):
        while True:
            #print("Self.leader client listner" + str(self.leader))
            if self.leader == True:
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
                                flag = True
                                self.user_completely_unknown(user_identity, identity_address,
                                                            identity_name, success_msg_for_client, flag)

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
                                flag = True
                                self.user_completely_unknown(user_identity, identity_address, identity_name,
                                                            success_msg_for_client, flag)

                    except Exception as e :
                        print("Exception in: discover_listener")
                        print(self.leader)
                        print(e)

                        

    # This method is used to receive a initial message by Clients, if they want to chat with other users
    def message_receiver_handler(self):
        while True:
            if self.leader == True:
                print("Message receiver handler")
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
                        for name in splitted_list_of_receiver:
                            if name == '':
                                splitted_list_of_receiver.remove(name)

                        filtered_list_of_receiver = [x for x in splitted_list_of_receiver if x]
                        test_list_for_comparison = []

                        # declare the both messages that are needed for response to the client
                        success_message_for_receiver = 'The users exist' + ',' + str(my_own_ip_address)
                        error_message_for_receiver = 'The users doesnt exist'
                        test_list_for_comparison = []
                        self.list_of_receiver_of_messages = []
                        for element in self.user_list:
                            for name in splitted_list_of_receiver:
                                if name == element[0]:
                                    test_list_for_comparison.append(name)
                                    self.list_of_receiver_of_messages.append(element)
                                    break

                        if test_list_for_comparison == filtered_list_of_receiver:
                            print("test_list_for_comparison == filtered_list_of_receiver")
                            print(sender_ip_of_message)
                            print(success_message_for_receiver)
                            self.answer_client_via_tcp(sender_ip_of_message, success_message_for_receiver)

                            self.tcp_answer_client_about_receivers_are_available()



                        else:
                            
                            self.answer_client_via_tcp(sender_ip_of_message, error_message_for_receiver)

                    except Exception as e:
                        print("Exception in: message_receiver_handler")
                        print(e)

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
