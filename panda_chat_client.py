import tkinter as tk
import socket
import threading

# Client Configuration
HOST = '127.0.0.1'
PORT = 5555
BUFFER_SIZE = 1024
FORMAT = 'utf-8'

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, radius, text, command,
                 bg="#3e3e3e", fg="#90EE90", font=("Helvetica", 12, "bold")):
        tk.Canvas.__init__(self, parent, width=width, height=height,
                           bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.width = width
        self.height = height
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.font = font
        self.draw_button(text)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def draw_button(self, text):
        self.button_id = self.create_round_rect(0, 0, self.width, self.height, r=self.radius,
                                                fill=self.bg, outline=self.bg)
        self.text_id = self.create_text(self.width/2, self.height/2,
                                        text=text, fill=self.fg, font=self.font)

    def create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_press(self, event):
        self.itemconfig(self.button_id, fill="#4e4e4e", outline="#4e4e4e")

    def on_release(self, event):
        self.itemconfig(self.button_id, fill=self.bg, outline=self.bg)
        if self.command:
            self.command()

    def on_enter(self, event):
        self.itemconfig(self.button_id, fill="#4e4e4e", outline="#4e4e4e")

    def on_leave(self, event):
        self.itemconfig(self.button_id, fill=self.bg, outline=self.bg)

class PandaChatGUIClient:
    def __init__(self, master):
        self.master = master
        # Use custom title bar by removing OS decorations
        self.master.overrideredirect(True)
        self.master.geometry("700x600")
        self.master.configure(bg="#1e1e1e")
        self.offset_x = 0
        self.offset_y = 0

        # Bind map event to reapply custom decorations when restored
        self.master.bind("<Map>", self.on_map)

        # ---------------------------
        # Custom Title Bar
        # ---------------------------
        self.title_bar = tk.Frame(master, bg="#2e2e2e", relief="flat", bd=0)
        self.title_bar.pack(side="top", fill="x")
        self.title_label = tk.Label(self.title_bar, text="Panda Chat", bg="#2e2e2e",
                                     fg="#90EE90", font=("Helvetica", 14, "bold"))
        self.title_label.pack(side="left", padx=10, pady=4)

        # Custom minimize and close buttons using RoundedButton
        self.minimize_button = RoundedButton(self.title_bar, width=30, height=30, radius=15, text="_",
                                             command=self.minimize_window, bg="#2e2e2e", fg="#90EE90",
                                             font=("Helvetica", 12))
        self.minimize_button.pack(side="right", padx=5, pady=2)
        self.close_button = RoundedButton(self.title_bar, width=30, height=30, radius=15, text="X",
                                          command=self.on_closing, bg="#2e2e2e", fg="#90EE90",
                                          font=("Helvetica", 12))
        self.close_button.pack(side="right", padx=5, pady=2)

        # Enable window dragging via the title bar
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        # ---------------------------
        # Main Chat UI
        # ---------------------------
        self.main_frame = tk.Frame(master, bg="#1e1e1e")
        self.main_frame.pack(side="top", fill="both", expand=True)

        # Chat display area
        self.chat_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.chat_frame.pack(padx=10, pady=(10,5), fill="both", expand=True)
        self.chat_area = tk.Text(self.chat_frame, bg="#1e1e1e", fg="#90EE90",
                                  state="disabled", wrap="word", font=("Helvetica", 12),
                                  bd=0, highlightthickness=0)
        self.chat_area.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_area.yview,
                                      bg="#1e1e1e", activebackground="#1e1e1e",
                                      bd=0, relief="flat")
        self.scrollbar.pack(side="right", fill="y")
        self.chat_area.config(yscrollcommand=self.scrollbar.set)

        # Message entry and send button frame
        self.entry_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.entry_frame.pack(fill="x", padx=10, pady=(5,10))
        self.message_entry = tk.Entry(self.entry_frame, bg="#2e2e2e", fg="#90EE90",
                                      font=("Helvetica", 12), bd=0, highlightthickness=0)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0,10), ipady=8)
        self.message_entry.bind("<Return>", self.send_message)
        self.send_button = RoundedButton(self.entry_frame, width=100, height=40, radius=20, text="Send",
                                         command=self.send_message, bg="#3e3e3e", fg="#90EE90",
                                         font=("Helvetica", 12, "bold"))
        self.send_button.pack(side="right")

        # ---------------------------
        # Integrated Name Overlay
        # ---------------------------
        self.name_overlay = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.name_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.name_label = tk.Label(self.name_overlay, text="Enter your panda name:",
                                   bg="#1e1e1e", fg="#90EE90", font=("Helvetica", 16))
        self.name_label.pack(pady=(150,10))
        self.name_entry = tk.Entry(self.name_overlay, bg="#2e2e2e", fg="#90EE90",
                                   font=("Helvetica", 16), bd=0, highlightthickness=0)
        self.name_entry.pack(ipadx=10, ipady=8)
        self.name_entry.focus_set()
        self.name_entry.bind("<Return>", self.submit_name)
        self.join_button = RoundedButton(self.name_overlay, width=120, height=40, radius=20, text="Join Chat",
                                         command=self.submit_name, bg="#3e3e3e", fg="#90EE90",
                                         font=("Helvetica", 12, "bold"))
        self.join_button.pack(pady=20)

        # ---------------------------
        # Networking Setup
        # ---------------------------
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.username = None

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ----- Window Dragging Methods -----
    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def stop_move(self, event):
        self.offset_x = 0
        self.offset_y = 0

    def do_move(self, event):
        x = self.master.winfo_pointerx() - self.offset_x
        y = self.master.winfo_pointery() - self.offset_y
        self.master.geometry(f"+{x}+{y}")

    # ----- Minimize/Restore Handling -----
    def minimize_window(self):
        self.master.overrideredirect(False)
        self.master.iconify()

    def on_map(self, event):
        # When restored from minimized state, reapply custom decorations
        self.master.overrideredirect(True)

    # ----- Name Overlay Handling -----
    def submit_name(self, event=None):
        name = self.name_entry.get().strip()
        if name:
            self.username = name
            self.name_overlay.destroy()
            self.connect_to_server()
        else:
            self.name_entry.focus_set()

    # ----- Networking Methods -----
    def connect_to_server(self):
        try:
            self.client_socket.connect((HOST, PORT))
            self.running = True
            self.client_socket.send(self.username.encode(FORMAT))
            self.insert_message(f"Connected to the server as {self.username}.")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.insert_message(f"Connection Error: {e}")

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                if message:
                    self.insert_message(message)
                else:
                    self.insert_message("Disconnected from server.")
                    self.running = False
                    break
            except Exception:
                self.insert_message("Error receiving message.")
                self.running = False
                break

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
                if message != "@leaves":
                    self.insert_message(f"You: {message}")
                else:
                    self.insert_message("You have left the chat.")
                    self.running = False
                self.message_entry.delete(0, tk.END)
            except Exception:
                self.insert_message("Error sending message.")

    def on_closing(self):
        if self.running:
            try:
                self.client_socket.send("@leaves".encode(FORMAT))
            except Exception:
                pass
            self.running = False
            self.client_socket.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PandaChatGUIClient(root)
    root.mainloop()
