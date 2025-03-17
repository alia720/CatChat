import socket
import threading
import random
import time
import signal
import sys
import select
from datetime import datetime

# Server Configuration
HOST = '127.0.0.1'  # localhost
PORT = 5555         # port number
BUFFER_SIZE = 1024
FORMAT = 'utf-8'

# Panda facts and emojis
PANDA_EMOJIS = ["🐼", "🎋", "🌿", "🍃", "🌱"]
PANDA_FACTS = [
    "Pandas spend around 14 hours a day eating bamboo!",
    "Baby pandas are born pink and weigh only about 100 grams!",
    "A group of pandas is called an embarrassment!",
    "Pandas can swim and are excellent tree climbers!",
    "There are only about 1,800 giant pandas left in the wild.",
    "Giant pandas have a special wrist bone that acts like a thumb for gripping bamboo!",
    "Pandas have 42 teeth designed for crushing tough bamboo!",
    "An adult panda can eat 20-40 pounds of bamboo per day!",
    "Giant pandas have the digestive system of a carnivore, yet they eat bamboo!",
    "Pandas communicate through scent marking, not through vocal sounds!"
]

# Panda-themed decorations
def get_panda_decoration():
    """Returns a random panda-themed decoration."""
    emoji = random.choice(PANDA_EMOJIS)
    decorations = [
        f"{emoji} ",
        f" {emoji} ",
        f"{emoji}{emoji} ",
        f" {emoji} PANDA CHAT {emoji} ",
        f"{emoji} Bamboo Express {emoji} "
    ]
    return random.choice(decorations)

class PandaChatServer:
    def __init__(self, host, port):
        """Initialize the server with host and port."""
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_socket: panda_name}
        self.client_threads = []  # Keep track of client threads
        self.running = True
        self.lock = threading.RLock()
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        print("\n🛑 Shutdown signal received. Shutting down server gracefully...")
        self.shutdown()
        sys.exit(0)  # Force exit after shutdown
        
    def start(self):
        """Start the server and listen for connections."""
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            # Set server socket to non-blocking mode
            self.server_socket.setblocking(0)
            print(f"🎋 Panda Chat Server started on {self.host}:{self.port} 🐼")
            print("Press Ctrl+C to shut down the server gracefully")
            
            # Create a list of sockets to monitor
            inputs = [self.server_socket]
            
            while self.running:
                try:
                    # Use select to wait for I/O readiness with a timeout
                    readable, _, exceptional = select.select(inputs, [], inputs, 1.0)
                    
                    # Check for shutdown flag
                    if not self.running:
                        break
                    
                    # Handle readable sockets
                    for sock in readable:
                        if sock is self.server_socket:
                            # New connection
                            client_socket, client_address = self.server_socket.accept()
                            print(f"New connection from {client_address}")
                            
                            # Start a new thread for each client
                            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                            client_thread.daemon = True
                            client_thread.start()
                            with self.lock:
                                self.client_threads.append(client_thread)
                    
                    # Handle exceptional sockets
                    for sock in exceptional:
                        print(f"Exception on socket {sock}")
                        if sock in inputs:
                            inputs.remove(sock)
                        if sock in self.clients:
                            self.remove_client(sock)
                            
                    # Clean up completed client threads
                    self.clean_finished_threads()
                    
                except Exception as e:
                    if self.running:  # Only print error if not during shutdown
                        print(f"Server loop error: {e}")
                    time.sleep(0.1)  # Prevent CPU spike in case of repeated errors
                
        except Exception as e:
            if self.running:  # Only print error if not during shutdown
                print(f"Server startup error: {e}")
        finally:
            self.cleanup()
    
    def clean_finished_threads(self):
        """Remove completed threads from the list."""
        with self.lock:
            active_threads = []
            for thread in self.client_threads:
                if thread.is_alive():
                    active_threads.append(thread)
            self.client_threads = active_threads
            
    def broadcast(self, message, sender_socket=None):
        """Broadcast a message to all clients except the sender."""
        timestamp = datetime.now().strftime("%H:%M")
        decorated_message = f"[{timestamp}] {get_panda_decoration()}{message}"
        
        with self.lock:
            clients_to_remove = []
            for client_socket in list(self.clients.keys()):
                # Don't send the message back to the sender
                if client_socket != sender_socket:
                    try:
                        client_socket.send(decorated_message.encode(FORMAT))
                    except:
                        # If sending fails, mark client for removal
                        clients_to_remove.append(client_socket)
            
            # Remove failed clients outside the iteration loop
            for client_socket in clients_to_remove:
                self.remove_client(client_socket)
    
    def send_to_client(self, client_socket, message):
        """Send a message to a specific client."""
        if not self.running:
            return  # Don't send messages during shutdown
            
        timestamp = datetime.now().strftime("%H:%M")
        decorated_message = f"[{timestamp}] {get_panda_decoration()}{message}"
        try:
            client_socket.send(decorated_message.encode(FORMAT))
        except:
            self.remove_client(client_socket)
    
    def remove_client(self, client_socket):
        """Remove a client from the server."""
        with self.lock:
            if client_socket in self.clients:
                panda_name = self.clients[client_socket]
                del self.clients[client_socket]
                try:
                    client_socket.close()
                except:
                    pass  # Socket might already be closed
                
                if self.running:  # Only broadcast if server is still running
                    self.broadcast(f"🍃 {panda_name} has left the bamboo forest!")
                print(f"Connection closed: {panda_name}")
    
    def handle_bamboo_command(self, client_socket):
        """Send a random panda fact to the client."""
        fact = random.choice(PANDA_FACTS)
        self.send_to_client(client_socket, f"🎍 Panda Fact: {fact}")
    
    def handle_grove_command(self, client_socket):
        """Send a list of connected users to the client."""
        with self.lock:
            if not self.clients:
                self.send_to_client(client_socket, "🌿 No pandas in the grove right now!")
                return
            
            pandas = list(self.clients.values())
            response = f"🌳 Pandas in the grove: {', '.join(pandas)}"
            self.send_to_client(client_socket, response)
    
    def handle_client(self, client_socket):
        """Handle client connection and messages."""
        try:
            # Set socket timeout to detect disconnections
            client_socket.settimeout(60)  # 60-second timeout
            
            # Get panda name from client
            try:
                panda_name_message = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                if not panda_name_message:
                    return  # Client disconnected before sending name
                panda_name = panda_name_message.strip()
            except socket.timeout:
                print("Client timed out during name selection")
                return
            except Exception as e:
                print(f"Error receiving client name: {e}")
                return
            
            # Check if name is already taken
            with self.lock:
                while panda_name in self.clients.values():
                    try:
                        client_socket.send(f"Name '{panda_name}' is already taken. Please choose another:".encode(FORMAT))
                        panda_name = client_socket.recv(BUFFER_SIZE).decode(FORMAT).strip()
                        if not panda_name:
                            return  # Client disconnected
                    except:
                        return  # Client disconnected or error
                
                # Add client to clients dictionary
                self.clients[client_socket] = panda_name
            
            # Welcome message
            try:
                welcome_msg = f"Welcome to the Panda Chat, {panda_name}! 🐼\n" \
                            f"Special commands:\n" \
                            f"@bamboo - Get a random panda fact\n" \
                            f"@grove - See who's in the chat\n" \
                            f"@leaves - Exit the chat"
                client_socket.send(welcome_msg.encode(FORMAT))
            except:
                self.remove_client(client_socket)
                return
            
            # Announce new client to everyone else
            self.broadcast(f"🌱 {panda_name} has joined the bamboo forest!", client_socket)
            
            # Main client message loop
            while self.running:
                try:
                    message = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                    
                    if not message:
                        break  # Empty message means client disconnected
                    
                    # Handle special commands
                    if message.strip() == "@bamboo":
                        self.handle_bamboo_command(client_socket)
                    elif message.strip() == "@grove":
                        self.handle_grove_command(client_socket)
                    elif message.strip() == "@leaves":
                        self.send_to_client(client_socket, "Goodbye from the bamboo forest! 🎋")
                        break
                    else:
                        # Normal message, broadcast to everyone
                        self.broadcast(f"{panda_name}: {message}", client_socket)
                        
                except socket.timeout:
                    # Send a ping to check if client is still connected
                    try:
                        client_socket.send("ping".encode(FORMAT))
                    except:
                        break  # Client disconnected
                    continue
                except ConnectionResetError:
                    break  # Client force-closed connection
                except ConnectionAbortedError:
                    break  # Connection aborted
                except Exception as e:
                    print(f"Error handling client message: {e}")
                    break
                
        except Exception as e:
            if self.running:  # Only print error if not during shutdown
                print(f"Client handler error: {e}")
        finally:
            self.remove_client(client_socket)

    def shutdown(self):
        """Initiate graceful server shutdown."""
        print("Starting server shutdown process...")
        self.running = False
        
        # Notify all clients about the shutdown
        shutdown_message = "🚨 Server is shutting down. Thank you for visiting the Panda Chat! 🐼"
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    self.send_to_client(client_socket, shutdown_message)
                    # Give clients a moment to receive the message before disconnecting
                    time.sleep(0.1)
                    client_socket.close()
                except:
                    pass
            
            # Clear the clients dictionary
            self.clients.clear()
        
        # Close the server socket to stop accepting new connections
        try:
            self.server_socket.close()
        except:
            pass
        
        print("Server shutdown complete.")
        
    def cleanup(self):
        """Clean up resources during shutdown."""
        # Set running flag to False to stop all threads
        self.running = False
        
        # Close all client sockets
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        try:
            self.server_socket.close()
        except:
            pass
        
        print("Server resources cleaned up.")

if __name__ == "__main__":
    server = PandaChatServer(HOST, PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        # This is a fallback in case the signal handler doesn't catch it
        print("\n🛑 Keyboard interrupt received. Shutting down server...")
        server.shutdown()
        sys.exit(0)
    finally:
        print("Server process terminated.")