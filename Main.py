# This is the main method to start a server
import threading

from ServerClass import Server

if __name__ == '__main__':
    server = Server()

    # Start a thread that is used for the method client listener
    client_listener_thread = threading.Thread(target=server.client_listener)
    client_listener_thread.start()

    message_receiver_thread = threading.Thread(target=server.message_receiver_handler)
    message_receiver_thread.start()

    # Heartbeat Thread
    """heartbeat_sender_thread = threading.Thread(target=server.heartbeat)
    heartbeat_sender_thread.start()"""

    # Update List Threads
    update_list_listener_thread = threading.Thread(target=server.receive_list_update)
    update_list_listener_thread.start()

    send_user_list_thread = threading.Thread(target=server.update_user_list)
    send_user_list_thread.start()

    detect_dead_leader_thread = threading.Thread(target = server.detection_of_dead_leader)
    detect_dead_leader_thread.start()

    # Thread for server List update
    server_list_update_thread = threading.Thread(target=server.update_server_list)
    server_list_update_thread.start()

    server_list_update_listener_thread = threading.Thread(target=server.listen_to_server_list_update)
    server_list_update_listener_thread.start()

    # Neighbour threads
    neighbour_listener_thread = threading.Thread(target=server.neighbour_message_listener)
    neighbour_listener_thread.start()

    # lcr threads
    lcr_listener_and_execution_thread = threading.Thread(target=server.lcr_listener_and_execution)
    lcr_listener_and_execution_thread.start()


    # Starts a thread that is used for the method client listener for system exit
    client_exit_thread = threading.Thread(target=server.client_listener_for_system_exit)
    client_exit_thread.start()

 