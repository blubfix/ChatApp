import sys
import threading
from Client_Class import Client

if __name__ == '__main__':
    client = Client()

    client_ui_thread = threading.Thread(target=client.ui)
    client_await_message_thread = threading.Thread(target=client.get_message_by_other_user_multicast)

    client_ui_thread.start()
    client_await_message_thread.start()

    client_ui_thread.join()
    client_await_message_thread.join()
