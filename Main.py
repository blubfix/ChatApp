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

    # Starts a thread that is used for the method client listener for system exit
    client_exit_thread = threading.Thread(target=server.client_listener_for_system_exit)
    client_exit_thread.start()

