import threading
import tkinter as tk
import json
from tkinter import simpledialog, messagebox
from chat_client import ChatClient


class ChatWindow:
    def __init__(self, master, username, client):
        self.window = tk.Toplevel(master)
        self.window.title("Chat")
        self.username = username
        self.client = client
        self.client.set_message_listener(self.handle_message)

        self.chat_log = tk.Text(self.window, bd=0, bg="white", height="8", width="50")
        self.chat_log.pack()

        self.entry_box = tk.Entry(self.window, bd=0, bg="beige")
        self.entry_box.bind("<Return>", self.send_message)
        self.entry_box.pack()

        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack()

        self.quit_button = tk.Button(self.window, text="Quit", command=self.quit)
        self.quit_button.pack()

    def handle_message(self, incoming_message):
        print(f"Handling message in thread: {threading.current_thread().name}")
        print(f"Raw message: {incoming_message}")  # Debugging line

        def _insert_message():
            # Process the message string to exclude the timestamp
            message = incoming_message.strip()  # Remove leading and trailing whitespaces

            # Check if the message is from the sender
            if "(Just now)" in message:
                username, _, message_text = message.partition(": ")  # Assume the part after ": " is the message
                formatted_message = f"{username}: {message_text}\n"  # username: message
                formatted_message = formatted_message.replace(" (Just now)", "")  # Remove "(Just now)"
            else:
                # Assume it's from the receiver
                username, _, message_text = message.partition(": ")
                formatted_message = f"{username}: {message_text}\n"  # username: message

            self.chat_log.insert(tk.END, formatted_message)

        self.window.after(0, _insert_message)

    def send_message(self, event=None):
        message = self.entry_box.get()
        self.chat_log.insert(tk.END, f"{self.username}: {message}\n")  # Remove " (Just now)" from this line
        self.entry_box.delete(0, tk.END)
        print(f"Sending message: {message}")
        try:
            self.client.send_message(message)
        except Exception as e:
            print(f"Exception in send_message: {e}")

    def quit(self):
        self.window.destroy()
        self.client.close()


class AuthWindow:
    def __init__(self, master):
        self.window = master
        self.window.title("Auth")

        self.register_button = tk.Button(self.window, text="Register", command=self.register)
        self.register_button.pack()

        self.login_button = tk.Button(self.window, text="Login", command=self.login)
        self.login_button.pack()

    def register(self):
        username = simpledialog.askstring("Register", "Enter your desired username")
        password = simpledialog.askstring("Register", "Enter your desired password", show="*")
        if not username or not password:
            messagebox.showerror("Error", "Both username and password are required.")
            return

        try:
            print(f"Registering user: {username}")
            client = ChatClient(username, password, '3.141.17.252', register=True)
            print("Registration successful")
            messagebox.showinfo("Success", "Registration successful!")
        except Exception as e:
            print(f"Exception in register: {e}")
            messagebox.showerror("Error", str(e))
            return

    def login(self):
        username = simpledialog.askstring("Login", "Enter your username")
        password = simpledialog.askstring("Login", "Enter your password", show="*")
        if not username or not password:
            messagebox.showerror("Error", "Both username and password are required.")
            return
        try:
            print(f"Logging in user: {username}")
            client = ChatClient(username, password, '3.141.17.252')
            print("Login successful")
            ChatWindow(self.window, username, client)
        except Exception as e:
            print(f"Exception in login: {e}")
            messagebox.showerror("Error", str(e))
            return


def main():
    root = tk.Tk()
    AuthWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
