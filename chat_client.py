import socket
import threading

class ChatClient:
    def __init__(self, username, host='localhost', port=55556):
        self.username = username
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.client.send(self.username.encode('utf-8'))
        self._message_listener = None

    def set_message_listener(self, listener):
        self._message_listener = listener
        threading.Thread(target=self._listen_for_messages).start()

    def _listen_for_messages(self):
        while True:
            message = self.client.recv(1024).decode('utf-8')
            if self._message_listener:
                self._message_listener(message)

    def send_message(self, message):
        self.client.send(message.encode('utf-8'))

    def close(self):
        self.client.close()

if __name__ == "__main__":
    client = ChatClient('Test User')
    client.send_message("Hello, Server!")
    client.close()
