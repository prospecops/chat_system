import os
import socket
import threading
import mysql.connector
import json
import bcrypt
import signal

def handle_alarm(signum, frame):
    print("Alarm handler invoked.")
    raise TimeoutError("Operation timed out")

class ChatServer:
    def __init__(self, host='localhost', port=55557):
        print("Initializing server...")
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.clients = {}
        self.lock = threading.Lock()

        self.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS chat_messages "
                            "(message_id INT AUTO_INCREMENT PRIMARY KEY, "
                            "username VARCHAR(255) NOT NULL, "
                            "message_text TEXT NOT NULL, "
                            "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        print("Server initialized.")

    def handle_client(self, client, username):
        print(f"Handling client {username}...")
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                print(f"Received message from {username}: {message}")
                if message == "":
                    print(f"Empty message received from {username}, breaking...")
                    break
                else:
                    self.broadcast_message(username, message)
            except Exception as e:
                print(f"Exception in handle_client for user {username}: {e}")
                break

        self.lock.acquire()
        del self.clients[username]
        self.lock.release()

        client.close()
        print(f"Closed connection with {username}.")

    def broadcast_message(self, sender, message):
        print(f"Broadcasting message from {sender}...")
        self.lock.acquire()
        # Store the message in the database
        try:
            sql = "INSERT INTO chat_messages (username, message_text) VALUES (%s, %s)"
            print(f"Executing SQL: {sql}")
            self.cursor.execute(sql, (sender, message))
            self.db.commit()
        except mysql.connector.Error as err:
            print(f"Failed to insert message into database: {err}")
        # Broadcast the message to other clients
        for username, client in self.clients.items():
            if username != sender:
                client.send(f"{sender}: {message}".encode('utf-8'))
        self.lock.release()

    def start(self):
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            client, address = self.server.accept()
            print(f"Connection accepted from {address}")

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
                print("Invalid request type received, closing connection.")
                client.close()
                continue

            username = request["username"]
            print(f"Connected with {username} at {str(address)}")

            self.lock.acquire()
            self.clients[username] = client
            self.lock.release()

            # Fetch recent messages and send them to the client
            recent_messages = self.fetch_recent_messages()
            for msg in reversed(recent_messages):  # reverse to send older messages first
                client.send(f"{msg[0]} ({msg[2]}): {msg[1]}".encode('utf-8'))  # msg[0] is username, msg[1] is message text, msg[2] is timestamp

            thread = threading.Thread(target=self.handle_client, args=(client, username))
            thread.start()

    def register(self, client, username, password):
        print(f"Registering {username}...")
        password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        try:
            signal.signal(signal.SIGALRM, handle_alarm)
            signal.alarm(5)
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                                (username, hashed.decode()))  # decode hashed to convert it to a string
            self.db.commit()
            signal.alarm(0)
            client.send("success".encode('utf-8'))
        except mysql.connector.Error as err:
            self.send_error(client, f"Failed to register: {err}")
        except TimeoutError:
            self.send_error(client, "Registration timed out")

    def login(self, client, username, password):
        password_encoded = password.encode('utf-8')
        try:
            signal.signal(signal.SIGALRM, handle_alarm)
            signal.alarm(5)
            self.cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            result = self.cursor.fetchone()
            signal.alarm(0)
            if result is None:
                self.send_error(client, "User does not exist")
                return False
            stored_password = result[1].encode('utf-8')  # this is actually the hashed password, which includes the salt
            if not bcrypt.checkpw(password_encoded, stored_password):  # use stored_password as the salt
                self.send_error(client, "Incorrect password")
                return False
        except TimeoutError:
            self.send_error(client, "Login operation timed out")
            return False
        except Exception as e:
            self.send_error(client, str(e))
            return False
        client.send("success".encode('utf-8'))  # Add this line
        return True

    def send_error(self, client, message):
        client.send(json.dumps({"type": "error", "message": message}).encode('utf-8'))

    def fetch_recent_messages(self):
        self.cursor.execute("SELECT username, message_text, timestamp FROM chat_messages "
                            "ORDER BY timestamp DESC LIMIT 100")
        return self.cursor.fetchall()


if __name__ == "__main__":
    ChatServer('172.31.25.224', 55557).start()
