import socket
import threading
import random
import time
import signal
import sys
import select
from datetime import datetime

# Server Configuration
HOST = '127.0.0.1'
PORT = 5555
BUFFER_SIZE = 1024
FORMAT = 'utf-8'

# Cat elements
CAT_EMOJIS = ["🐱", "🐾", "🥛", "🎣", "🧶"]
CAT_FACTS = [
    "Cats sleep 12-16 hours a day on average!",
    "A cat's nose has a unique pattern, like a human fingerprint!",
    "Cats have 32 muscles in each ear!",
    "The oldest known pet cat existed 9,500 years ago!",
    "Cats can jump up to 6 times their body length!",
    "Cats have a special reflective layer in their eyes called the tapetum lucidum!",
    "A group of cats is called a clowder!",
    "Cats walk like camels and giraffes: both right feet then both left feet!",
    "Cats have 230 bones - humans have 206!",
    "A cat's purr vibrates at 25-150Hz, which can promote healing!"
]

CAT_ASCII = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠶⢤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⡴⠞⠳⠶⠦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠾⠋⠀⠀⠀⠀⠹⣧⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣰⠏⠀⠀⠀⠀⠀⠀⠉⠳⣦⡀⠀⠀⠀⠀⠀⠀⣤⡾⠿⣷⠀⠀⠀⢠⡞⠁⠀⠀⠀⠀⠀⠀⠀⢹⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠀⣤⠤⠼⢤⡿⠃⠀⠼⠟⠻⠿⡤⠛⠀⠀⠀⠀⣠⣼⣤⣀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡇⠀⠀⣴⠖⠒⢶⡦⠀⠀⠀⠁⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠁⠀⠠⠀⠀⠻⣦⣄⣹⡄⠀⢹⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡄⠀⠀⡏⣠⡾⢻⠇⠠⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠙⢿⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡄⠀⠘⢷⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣾⠄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠠⠜⢧⡀⠀⠀⠀⠀⠀
⠀⠀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⣄⠀⠀⠀
⢀⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⡆⠀⠀⠀⢀⣀⠀⠀⠀⠀⣿⣿⣿⡆⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⢀⠙⣧⠀⠀
⣼⡍⠀⣀⡀⠀⠀⠀⠀⠀⠐⠀⠀⠀⠐⠄⠛⠿⠛⠁⠀⠀⠰⠏⠙⠷⠀⠀⠀⠈⠉⠉⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⠶⣼⡇⠀
⣿⣷⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠁⠀⠀⠀⢰⣀⠘⣇⠀
⣿⠀⢀⡴⠲⠀⠀⠀⠀⠀⠒⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡟⠀
⠹⣞⠋⢀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠇⣰⠇⠀⠀
⠀⠻⣄⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⠋⠀⠀⠀
⠀⠀⠙⠷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠙⣷⠶⡤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠋⢹⡆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣤⡴⠖⠶⣄⠀
⠀⠀⠀⠀⠀⣿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⢸⡆
⠀⠀⠀⣴⠞⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠇⠀⠀⣠⡿⠀
⠀⠀⠀⢿⡀⠀⢿⡀⠀⠀⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⣠⡟⣀⣴⡾⠛⢈⠀
⠀⠀⠀⠐⠛⠶⣤⣽⣶⣄⠀⠀⠀⠸⣇⡀⠀⠀⠤⠴⣿⠀⠀⠀⠀⠀⢸⡶⠶⠀⠀⢀⣿⠐⠀⣀⣀⣠⣤⠾⠛⠛⠋⡁⠀⠀⠀⠀
⠀⠀⠀⠐⠀⠀⠤⠄⠈⠉⠛⠛⠶⠶⢿⣄⠀⠄⠀⣠⣧⣤⣤⣤⡤⠶⠾⣇⠀⠀⢐⣽⠟⠛⢛⠉⠍⠁⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠙⡷⠖⣟⣋⣀⣀⣀⣀⠀⠀⠀⠈⠛⠛⠋⠥⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

def get_cat_decoration():
    emoji = random.choice(CAT_EMOJIS)
    decorations = [
        f"{emoji} ",
        f" {emoji} ",
        f"{emoji}{emoji} ",
        f" {emoji} PURR CHAT {emoji} ",
        f"{emoji} Catnip Zone {emoji} "
    ]
    return random.choice(decorations)

class CatChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.client_threads = []
        self.running = True
        self.lock = threading.RLock()
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        print("\n🐾 Shutdown signal received. Closing cat chat...")
        self.shutdown()
        sys.exit(0)
        
    def start(self):
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.setblocking(0)
            print(f"🐱 Cat Chat Server started on {self.host}:{PORT} 🧶")
            print("Press Ctrl+C to shut down")
            
            inputs = [self.server_socket]
            
            while self.running:
                try:
                    readable, _, exceptional = select.select(inputs, [], inputs, 1.0)
                    
                    if not self.running:
                        break
                    
                    for sock in readable:
                        if sock is self.server_socket:
                            client_socket, client_address = self.server_socket.accept()
                            print(f"New connection from {client_address}")
                            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                            client_thread.daemon = True
                            client_thread.start()
                            with self.lock:
                                self.client_threads.append(client_thread)
                    
                    for sock in exceptional:
                        print(f"Exception on socket {sock}")
                        if sock in inputs:
                            inputs.remove(sock)
                        if sock in self.clients:
                            self.remove_client(sock)
                            
                    self.clean_finished_threads()
                    
                except Exception as e:
                    if self.running:
                        print(f"Server error: {e}")
                    time.sleep(0.1)
                
        except Exception as e:
            if self.running:
                print(f"Startup error: {e}")
        finally:
            self.cleanup()
    
    def clean_finished_threads(self):
        with self.lock:
            self.client_threads = [t for t in self.client_threads if t.is_alive()]
            
    def broadcast(self, message, sender_socket=None):
        timestamp = datetime.now().strftime("%H:%M")
        decorated_message = f"[{timestamp}] {get_cat_decoration()}{message}"
        
        with self.lock:
            clients_to_remove = []
            for client_socket in list(self.clients.keys()):
                if client_socket != sender_socket:
                    try:
                        client_socket.send(decorated_message.encode(FORMAT))
                    except:
                        clients_to_remove.append(client_socket)
            
            for client_socket in clients_to_remove:
                self.remove_client(client_socket)
    
    def send_to_client(self, client_socket, message):
        if not self.running:
            return
            
        timestamp = datetime.now().strftime("%H:%M")
        decorated_message = f"[{timestamp}] {get_cat_decoration()}{message}"
        try:
            client_socket.send(decorated_message.encode(FORMAT))
        except:
            self.remove_client(client_socket)
    
    def remove_client(self, client_socket):
        with self.lock:
            if client_socket in self.clients:
                cat_name = self.clients[client_socket]
                del self.clients[client_socket]
                try:
                    client_socket.close()
                except:
                    pass
                
                if self.running:
                    self.broadcast(f"🐾 {cat_name} has left the chat!")
                print(f"Connection closed: {cat_name}")
    
    def handle_catnip_command(self, client_socket):
        fact = random.choice(CAT_FACTS)
        self.send_to_client(client_socket, f"🧶 Cat Fact: {fact}")
    
    def handle_purr_command(self, client_socket):
        with self.lock:
            if not self.clients:
                self.send_to_client(client_socket, "🐾 No cats purring here!")
                return
            
            cats = list(self.clients.values())
            response = f"🐱 Cats in chat: {', '.join(cats)}"
            self.send_to_client(client_socket, response)
    
    def handle_client(self, client_socket):
        try:
            client_socket.settimeout(60)
            
            try:
                cat_name = client_socket.recv(BUFFER_SIZE).decode(FORMAT).strip()
                if not cat_name:
                    return
            except:
                return
            
            with self.lock:
                while cat_name in self.clients.values():
                    try:
                        client_socket.send(f"Name '{cat_name}' taken. Choose another:".encode(FORMAT))
                        cat_name = client_socket.recv(BUFFER_SIZE).decode(FORMAT).strip()
                        if not cat_name:
                            return
                    except:
                        return
                
                self.clients[client_socket] = cat_name
            
            try:
                welcome_msg = f"Welcome to Cat Chat, {cat_name}! 🐾\n" \
                            f"{CAT_ASCII}\n" \
                            f"Commands:\n" \
                            f"@catnip - Get a cat fact\n" \
                            f"@purr - See who's here\n" \
                            f"@nap - Exit\n"
                client_socket.send(welcome_msg.encode(FORMAT))
            except:
                self.remove_client(client_socket)
                return
            
            self.broadcast(f"🐱 {cat_name} has entered the chatroom!", client_socket)
            
            while self.running:
                try:
                    message = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                    
                    if not message:
                        break
                    
                    if message.strip() == "@catnip":
                        self.handle_catnip_command(client_socket)
                    elif message.strip() == "@purr":
                        self.handle_purr_command(client_socket)
                    elif message.strip() == "@nap":
                        self.send_to_client(client_socket, "Goodbye from the cat chat! 🐾")
                        break
                    else:
                        self.broadcast(f"{cat_name}: {message}", client_socket)
                        
                except socket.timeout:
                    try:
                        client_socket.send("ping".encode(FORMAT))
                    except:
                        break
                    continue
                except ConnectionResetError:
                    break
                except Exception as e:
                    print(f"Client error: {e}")
                    break
                
        except Exception as e:
            if self.running:
                print(f"Handler error: {e}")
        finally:
            self.remove_client(client_socket)

    def shutdown(self):
        print("Starting shutdown...")
        self.running = False
        
        shutdown_message = "🐾 Server closing. Thanks for purring with us!"
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    self.send_to_client(client_socket, shutdown_message)
                    time.sleep(0.1)
                    client_socket.close()
                except:
                    pass
            
            self.clients.clear()
        
        try:
            self.server_socket.close()
        except:
            pass
        
        print("Server closed.")
        
    def cleanup(self):
        self.running = False
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        try:
            self.server_socket.close()
        except:
            pass
        
        print("Cleanup complete.")

if __name__ == "__main__":
    server = CatChatServer(HOST, PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🐾 Keyboard interrupt. Shutting down...")
        server.shutdown()
        sys.exit(0)
    finally:
        print("Server terminated.")