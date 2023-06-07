import tkinter as tk
from tkinter import simpledialog, messagebox
from chat_client import ChatClient

# A window for user authentication (registration and login).
class AuthWindow:
    def __init__(self):
        # Create a new window.
        self.window = tk.Tk()
        self.window.title("Auth")

        # Create buttons for registration and login.
        self.register_button = tk.Button(self.window, text="Register", command=self.register)
        self.login_button = tk.Button(self.window, text="Login", command=self.login)

    def register(self):
        # Show a dialog asking for the username and password.
        username = simpledialog.askstring("Register", "Enter your desired username")
        password = simpledialog.askstring("Register", "Enter your desired password", show="*")
        if not username or not password:
            messagebox.showerror("Error", "Both username and password are required.")
            return

        # Try to create a chat client with register=True. If it fails, show an error message.
        try:
            client = ChatClient(username, password, '3.141.17.252', register=True)
        except:
            messagebox.showerror("Error", "Registration failed. Try again with a different username.")
            return

        # Hide the auth window and show the chat window.
        self.hide()
        ChatWindow(username, client).show()

    def login(self):
        # Similar to register, but with register=False.
        username = simpledialog.askstring("Login", "Enter your username")
        password = simpledialog.askstring("Login", "Enter your password", show="*")
        if not username or not password:
            messagebox.showerror("Error", "Both username and password are required.")
            return

        try:
            client = ChatClient(username, password, '3.141.17.252')
        except:
            messagebox.showerror("Error", "Login failed. Check your username and password.")
            return

        self.hide()
        ChatWindow(username, client).show()

    def show(self):
        # Show the window and all its widgets.
        self.window.deiconify()
        self.register_button.pack()
        self.login_button.pack()

    def hide(self):
        # Hide the window and all its widgets.
        self.window.withdraw()
        self.register_button.pack_forget()
        self.login_button.pack_forget()

# A window for chatting.
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
        self.chat_log.insert(tk.END, f"{message}\n")

    def send_message(self, event=None):
        message = self.entry_box.get()
        self.chat_log.insert(tk.END, f"{self.username}: {message}\n")
        self.entry_box.delete(0, tk.END)
        self.client.send_message(message)

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

# The main function that runs when the script is run.
def main():
    auth_window = AuthWindow()
    auth_window.show()
    tk.mainloop()

if __name__ == "__main__":
    main()
