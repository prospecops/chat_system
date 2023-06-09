import socket
import json
import threading


class ChatClient:
    def __init__(self, username, password, host='localhost', port=55557, register=False):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        if register:
            request = {"type": "register", "username": username, "password": password}
        else:
            request = {"type": "login", "username": username, "password": password}
        self.client.send(json.dumps(request).encode('utf-8'))

        self._message_listener = None
        self.login_successful = None  # Flag to track login status

        self.thread = threading.Thread(target=self._listen_for_messages)
        self.thread.start()

    def _listen_for_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                print(f"Received message: {message}")
                if message == "success":
                    print("Login was successful.")
                    self.login_successful = True
                elif message == "fail":
                    print("Login failed.")
                    self.login_successful = False
                else:
                    if self._message_listener:
                        self._message_listener(message)
            except Exception as e:
                print(f"Exception in listen_for_messages: {e}")
                break

    def set_message_listener(self, listener):
        self._message_listener = listener

    def send_message(self, message):
        print(f"Sending message: {message}")
        try:
            self.client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Exception in send_message: {e}")

    def close(self):
        print("Closing connection...")
        try:
            self.client.close()
        except Exception as e:
            print(f"Exception in close: {e}")


if __name__ == "__main__":
    import time

    def print_message(message):
        print("Received:", message)

    client1 = ChatClient("alice", "password", register=True)
    client1.set_message_listener(print_message)
    client2 = ChatClient("bob", "password", register=True)
    client2.set_message_listener(print_message)

    time.sleep(1)  # give server a bit of time to process registrations

    client1.send_message("Hello, Bob!")
    client2.send_message("Hello, Alice!")
