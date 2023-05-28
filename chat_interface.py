import tkinter as tk
from tkinter import Scrollbar, Text
from tkinter import simpledialog
from chat_client import ChatClient

class ChatWindow:
    def __init__(self, window_title):
        self.window = tk.Tk()
        self.window.title(window_title)

        self.username = None

        self.chat_log = Text(self.window, bd=0, bg="white", height="8", width="50")
        self.scrollbar = Scrollbar(self.window, command=self.chat_log.yview, cursor="heart")
        self.chat_log['yscrollcommand'] = self.scrollbar.set

        self.entry_box = tk.Entry(self.window, bd=0, bg="beige")
        self.entry_box.bind("<Return>", self.send_message)
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message)

        self.quit_button = tk.Button(self.window, text="Quit", command=self.quit)

    def get_username(self):
        self.username = simpledialog.askstring("Username", "Enter your username")
        if not self.username:
            self.quit()

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

    def run(self):
        self.get_username()

        self.client = ChatClient(self.username)
        self.client.set_message_listener(self.handle_message)

        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entry_box.pack(side=tk.BOTTOM, fill=tk.X)
        self.send_button.pack(side=tk.BOTTOM)
        self.quit_button.pack(side=tk.TOP)
        self.window.mainloop()

if __name__ == "__main__":
    chat_window = ChatWindow("Chat Window")
    chat_window.run()
