import socket
import threading
import random
import sys
import os
import time

# Client Configuration
HOST = '127.0.0.1'  # localhost
PORT = 5555         # port number
BUFFER_SIZE = 1024
FORMAT = 'utf-8'

# Panda ASCII art for welcome screen
PANDA_ASCII = """
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣦⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢿⣿⠟⠋⠉⠀⠀⠀⠀⠉⠑⠢⣄⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣦⡀
⠀⣀⠀⠀⢀⡏⠀⢀⣴⣶⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⠇
⣾⣿⣿⣦⣼⡀⠀⢺⣿⣿⡿⠃⠀⠀⠀⠀⣠⣤⣄⠀⠀⠈⡿⠋⠀
⢿⣿⣿⣿⣿⣇⠀⠤⠌⠁⠀⡀⢲⡶⠄⢸⣏⣿⣿⠀⠀⠀⡇⠀⠀
⠈⢿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠈⠉⠓⠂⠀⠙⠛⠛⠠⠀⡸⠁⠀⠀
⠀⠀⠻⣿⣿⣿⣿⣿⣿⣷⣦⣄⣀⠀⠀⠀⠀⠑⠀⣠⠞⠁⠀⠀⠀
⠀⠀⠀⢸⡏⠉⠛⠛⠛⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠸⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⢿⣿⣿⣿⣿⡄⠀⠀⠀⠀
⠀⠀⠀⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⡀⠀⠀⠀
⠀⠀⠀⢸⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⡇⠀⠀⠀
⠀⠀⠀⢸⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⡟⠻⠿⠟⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣿⣶⠶⠤⠤⢤⣶⣾⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠹⣿⣿⣿⠏⠀⠀⠀⠈⢿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠉⠉⠀⠀⠀⠀⠀⠀⠉⠉
  Panda Chat
"""

class PandaChatClient:
    def __init__(self, host, port):
        """Initialize the client with host and port."""
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        
    def clear_screen(self):
        """Clear the terminal screen based on OS."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_welcome(self):
        """Display welcome screen with ASCII art."""
        self.clear_screen()
        print(PANDA_ASCII)
        print("\nWelcome to the Panda Chat Room!")
        print("Connect with other pandas from around the world!")
        print("\nSpecial commands:")
        print("  @bamboo - Get a random panda fact")
        print("  @grove - See who's in the chat")
        print("  @leaves - Exit the chat")
        print("\n" + "-" * 50)
        
    def connect(self):
        """Connect to the server and set up the client."""
        try:
            self.client_socket.connect((self.host, self.port))
            self.running = True
            
            self.display_welcome()
            
            # Get user's panda name
            panda_name = input("\nEnter your panda name: ")
            while not panda_name.strip():
                panda_name = input("Panda name cannot be empty. Try again: ")
                
            # Send panda name to server
            self.client_socket.send(panda_name.encode(FORMAT))
            
            # Start thread to receive messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Main loop for sending messages
            self.send_messages()
            
        except ConnectionRefusedError:
            print("\n🚫 Could not connect to the server. Is it running?")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
        finally:
            self.client_socket.close()
    
    def receive_messages(self):
        """Continuously receive and display messages from the server."""
        while self.running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                if message:
                    print(f"\n{message}")
                    print("> ", end="", flush=True)  # Show prompt again
                else:
                    # Empty message usually means server disconnected
                    print("\n🚫 Lost connection to the server.")
                    self.running = False
                    break
            except Exception as e:
                if self.running:  # Only show error if not deliberately disconnected
                    print(f"\n❌ Error receiving message: {e}")
                self.running = False
                break
    
    def send_messages(self):
        """Handle user input and send messages to the server."""
        try:
            # Wait for welcome message
            time.sleep(0.5)
            
            while self.running:
                message = input("> ")
                
                if not self.running:
                    break
                
                # Check for leave command
                if message.strip() == "@leaves":
                    self.client_socket.send(message.encode(FORMAT))
                    print("\n🍃 Leaving the bamboo forest...")
                    self.running = False
                    time.sleep(1)  # Wait for server response before exiting
                    break
                
                # Send the message
                self.client_socket.send(message.encode(FORMAT))
                
        except KeyboardInterrupt:
            print("\n🍃 Leaving the bamboo forest...")
            try:
                self.client_socket.send("@leaves".encode(FORMAT))
            except:
                pass
            self.running = False
        except Exception as e:
            if self.running:  # Only show error if not deliberately disconnected
                print(f"\n❌ Error sending message: {e}")
            self.running = False

if __name__ == "__main__":
    client = PandaChatClient(HOST, PORT)
    client.connect()