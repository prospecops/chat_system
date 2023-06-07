import threading
import tkinter as tk
import json
from tkinter import simpledialog, messagebox
from chat_client import ChatClient

class AuthWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Auth")

        self.register_button = tk.Button(self.window, text="Register", command=self.register)
        self.login_button = tk.Button(self.window, text="Login", command=self.login)

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
            self.hide()
            ChatWindow(username, client).show()
        except Exception as e:
            print(f"Exception in login: {e}")
            messagebox.showerror("Error", str(e))
            return

    def show(self):
        self.window.deiconify()
        self.register_button.pack()
        self.login_button.pack()

    def hide(self):
        self.window.withdraw()
        self.register_button.pack_forget()
        self.login_button.pack_forget()



class ChatWindow:
    def __init__(self, username, client):
        self.window = tk.Tk()
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

    def handle_message(self, message):
        print(f"Handling message in thread: {threading.current_thread().name}")

        def _insert_message():
            self.chat_window.insert(tk.END, message + "\n")

        self.after(0, _insert_message)

    def insert_message(self, message):
        self.chat_log.insert(tk.END, f"{message}\n")

    def send_message(self, event=None):
        message = self.entry_box.get()
        self.chat_log.insert(tk.END, f"{self.username}: {message}\n")
        self.entry_box.delete(0, tk.END)
        print(f"Sending message: {message}")
        try:
            self.client.send_message(message)
        except Exception as e:
            print(f"Exception in send_message: {e}")

    def quit(self):
        self.window.quit()
        self.client.close()

    def show(self):
        self.window.deiconify()
        self.chat_log.pack()
        self.entry_box.pack()
        self.send_button.pack()
        self.quit_button.pack()

    def hide(self):
        self.window.withdraw()
        self.chat_log.pack_forget()
        self.entry_box.pack_forget()
        self.send_button.pack_forget()
        self.quit_button.pack_forget()

def main():
    auth_window = AuthWindow()
    auth_window.show()
    tk.mainloop()

if __name__ == "__main__":
    main()