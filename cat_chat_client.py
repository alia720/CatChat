import tkinter as tk
import socket
import threading

# Client Configuration
HOST = '127.0.0.1'
PORT = 5555
BUFFER_SIZE = 4096  # Increased buffer size
FORMAT = 'utf-8'

# Subdued Cat-themed Colors
BG_COLOR = "#f2f2f2"       # Light gray background
TEXT_COLOR = "#333333"     # Dark gray text
ACCENT_COLOR = "#ffc0cb"   # Soft pink accent
ENTRY_BG = "#e6e6e6"       # Light gray for entry

class CatChatGUIClient:
    def __init__(self, master):
        self.master = master
        self.master.title("😻 Cat Chat")
        self.master.geometry("700x600")
        self.master.configure(bg=BG_COLOR)
        self.master.minsize(400, 400)

        # Main Container
        self.main_container = tk.Frame(master, bg=BG_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Chat Display Area
        self.chat_frame = tk.Frame(self.main_container, bg=BG_COLOR)
        self.chat_frame.pack(fill="both", expand=True)
        
        self.chat_area = tk.Text(self.chat_frame, bg=BG_COLOR, fg=TEXT_COLOR,
                                 state="disabled", wrap="word", font=("Helvetica", 12),
                                 bd=0, highlightthickness=0)
        self.chat_area.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_area.yview,
                                      bg=BG_COLOR, troughcolor=ENTRY_BG)
        self.scrollbar.pack(side="right", fill="y")
        self.chat_area.config(yscrollcommand=self.scrollbar.set)

        # Message Entry Bar
        self.entry_frame = tk.Frame(self.main_container, bg=BG_COLOR)
        self.entry_frame.pack(fill="x", padx=10, pady=(5,10))
        
        self.message_entry = tk.Entry(self.entry_frame, bg=ENTRY_BG, fg=TEXT_COLOR,
                                      font=("Helvetica", 12), bd=0, highlightthickness=1,
                                      highlightbackground=ACCENT_COLOR, insertbackground=TEXT_COLOR)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0,10), ipady=8)
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.entry_frame, text="Send 🐾", command=self.send_message,
                                     bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"),
                                     relief="flat", padx=10, pady=5)
        self.send_button.pack(side="right")

        # Name Overlay (covers the chat UI initially)
        self.name_overlay = tk.Frame(self.main_container, bg=BG_COLOR)
        self.name_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.name_label = tk.Label(self.name_overlay, text="Enter your cat name:",
                                   bg=BG_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 16))
        self.name_label.pack(pady=(150,10))
        
        self.name_entry = tk.Entry(self.name_overlay, bg=ENTRY_BG, fg=TEXT_COLOR,
                                   font=("Helvetica", 16), bd=0, highlightthickness=1,
                                   highlightbackground=ACCENT_COLOR, insertbackground=TEXT_COLOR)
        self.name_entry.pack(ipadx=10, ipady=8)
        self.name_entry.focus_set()
        self.name_entry.bind("<Return>", self.submit_name)
        
        self.join_button = tk.Button(self.name_overlay, text="Join Chat 😸",
                                     command=self.submit_name, bg=ACCENT_COLOR, fg=TEXT_COLOR,
                                     font=("Helvetica", 14, "bold"), relief="flat", padx=10, pady=5)
        self.join_button.pack(pady=20)

        # Networking Setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.username = None
        # Buffer for incomplete messages
        self.message_buffer = b''
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def submit_name(self, event=None):
        name = self.name_entry.get().strip()
        if name:
            self.username = name
            self.name_overlay.destroy()  # Reveal chat UI
            self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket.connect((HOST, PORT))
            self.running = True
            self.client_socket.send(self.username.encode(FORMAT))
            self.insert_message(f"🐾 Connected as {self.username}! Start chatting!")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.insert_message(f"😿 Connection Error: {e}")

    def insert_message(self, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state="disabled")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            try:
                self.client_socket.send(message.encode(FORMAT))
                if message != "@nap":
                    self.insert_message(f"😺 You: {message}")
                else:
                    self.insert_message("💤 You curled up for a nap!")
                    self.running = False
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.insert_message(f"😾 Error sending message: {e}")

    def receive_messages(self):
        while self.running:
            try:
                # Receive data and add to buffer
                chunk = self.client_socket.recv(BUFFER_SIZE)
                if not chunk:
                    # Connection closed by server
                    self.insert_message("😿 Server closed the connection")
                    break
                
                # Add the new chunk to our buffer
                self.message_buffer += chunk
                
                # Process as many complete messages as possible
                while True:
                    try:
                        # Try to decode the current buffer
                        message = self.message_buffer.decode(FORMAT)
                        # If successful, clear buffer and process message
                        self.message_buffer = b''
                        if message:
                            self.insert_message(message)
                        break
                    except UnicodeDecodeError as e:
                        # If we get a specific error about unexpected end of data
                        if "unexpected end of data" in str(e):
                            # We need more data, break this inner loop and wait for next chunk
                            break
                        else:
                            # For other decode errors, discard a byte and try again
                            self.message_buffer = self.message_buffer[1:]
                            if not self.message_buffer:
                                break
            except Exception as e:
                if self.running:  # Only show error if we're still supposed to be running
                    self.insert_message(f"😿 Error receiving message: {e}")
                break
        self.running = False

    def on_closing(self):
        # Gracefully close connection and exit
        if self.running:
            try:
                self.client_socket.send("@nap".encode(FORMAT))
            except:
                pass
            self.running = False
            self.client_socket.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CatChatGUIClient(root)
    root.mainloop()