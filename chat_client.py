# chat_client.py

import os
import socket
import threading
import json
import logging  # NEW

# Configure logging
logging.basicConfig(filename='chat_client.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class ChatClient:
    def __init__(self, username, password, host=os.getenv('SERVER_HOST'), port=55557, register=False):
        self.username = username
        self.password = password
        self.host = host
        self.port = port

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
        except Exception as e:  # catch any exceptions and log them
            logging.error(f"Error in connecting to server: {e}")
            raise

        request = {
            "type": "register" if register else "login",
            "username": self.username,
            "password": self.password
        }
        try:
            self.client.send(json.dumps(request).encode('utf-8'))
        except Exception as e:  # catch any exceptions and log them
            logging.error(f"Error in sending request: {e}")
            raise

        if register:  # if this was a registration request
            try:
                server_response = self.client.recv(1024).decode('utf-8')
                if server_response == "fail":
                    raise Exception("Registration failed.")
                else:
                    print("Registration successful. Please login again.")
                    self.close()  # Close the connection
                    return  # End the __init__ method early
            except Exception as e:  # catch any exceptions and log them
                logging.error(f"Error in receiving response or registration failure: {e}")
                raise

        self._message_listener = None

    def set_message_listener(self, listener):
        self._message_listener = listener
        try:
            threading.Thread(target=self._listen_for_messages).start()
        except Exception as e:  # catch any exceptions and log them
            logging.error(f"Error in starting message listener: {e}")
            raise

    def _listen_for_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if self._message_listener:
                    self._message_listener(message)
            except Exception as e:  # catch any exceptions and log them
                logging.error(f"Error in listening for messages: {e}")
                break

    def send_message(self, message):
        try:
            self.client.send(message.encode('utf-8'))
        except Exception as e:  # catch any exceptions and log them
            logging.error(f"Error in sending message: {e}")

    def close(self):
        try:
            self.client.close()
        except Exception as e:  # catch any exceptions and log them
            logging.error(f"Error in closing connection: {e}")
