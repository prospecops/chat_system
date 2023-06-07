import os
import socket
import threading
import mysql.connector  # To connect and interact with MySQL database
import json  # To send and receive JSON formatted messages
import bcrypt  # To encrypt passwords

class ChatServer:
    def __init__(self, host='localhost', port=55557):
        # Setup server
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        # Initialize clients dictionary and threading lock
        self.clients = {}
        self.lock = threading.Lock()

        # Setup MySQL connection
        self.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        # Cursor to execute MySQL commands
        self.cursor = self.db.cursor()
        # Create users table if not exists
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255))")

    def handle_client(self, client, username):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == "":  # client disconnected
                    break
                else:  # it's a chat message
                    self.broadcast_message(username, message)
            except:
                break

        # Remove disconnected client from the clients dictionary
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

            # Receive and process login or registration request
            request = client.recv(1024).decode('utf-8')
            request = json.loads(request)
            if request["type"] == "register":
                self.register(client, request["username"], request["password"])
            elif request["type"] == "login":
                if not self.login(client, request["username"], request["password"]):
                    client.send("fail".encode('utf-8'))
                    client.close()
                    continue
            else:
                client.close()
                continue

            username = request["username"]
            print(f"Connected with {username} at {str(address)}")

            # Add connected client to the clients dictionary
            self.lock.acquire()
            self.clients[username] = client
            self.lock.release()

            # Start a new thread to handle the client
            thread = threading.Thread(target=self.handle_client, args=(client, username))
            thread.start()

    def register(self, client, username, password):
        # Hash the password
        password = password.encode('utf-8')  # convert to bytes
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            # Try to insert new user into users table
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
            self.db.commit()
        except mysql.connector.Error as err:
            self.send_error(client, f"Failed to register: {err}")  # Send error to client

    def login(self, client, username, password):
        # Check if the user exists and the password is correct
        self.cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        result = self.cursor.fetchone()
        if result is None:
            self.send_error(client, "User does not exist")  # Send error to client
            return False
        hashed = result[1]
        if not bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
            self.send_error(client, "Incorrect password")  # Send error to client
            return False
        return True

    def send_error(self, client, error_message):
        # Send an error message to the client
        error_msg = {
            "type": "error",
            "message": error_message
        }
        client.send(json.dumps(error_msg).encode('utf-8'))

if __name__ == "__main__":
    server = ChatServer('172.31.25.224')
    server.start()
