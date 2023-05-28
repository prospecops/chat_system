import socket
import threading

class ChatServer:
    def __init__(self, host='localhost', port=55556):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.clients = {}
        self.lock = threading.Lock()

    def handle_client(self, client, username):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break
                self.broadcast_message(username, message)
            except:
                break

        self.lock.acquire()
        del self.clients[username]
        self.lock.release()

        client.close()

    def broadcast_message(self, sender, message):
        self.lock.acquire()
        for username, client in self.clients.items():
            if username != sender:
                client.send(f"{sender}: {message}".encode('utf-8'))
        self.lock.release()

    def start(self):
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            client, address = self.server.accept()

            username = client.recv(1024).decode('utf-8')
            print(f"Connected with {username} at {str(address)}")

            self.lock.acquire()
            self.clients[username] = client
            self.lock.release()

            thread = threading.Thread(target=self.handle_client, args=(client, username))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.start()
