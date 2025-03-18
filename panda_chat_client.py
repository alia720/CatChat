import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QInputDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal, QObject, Qt

# Client Configuration
HOST = '127.0.0.1'
PORT = 5555
BUFFER_SIZE = 1024
FORMAT = 'utf-8'

class MessageReceiver(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.running = True

    def run(self):
        while self.running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                if message:
                    self.message_received.emit(message)
                else:
                    self.message_received.emit("Disconnected from server.")
                    self.running = False
                    break
            except Exception:
                self.message_received.emit("Error receiving message.")
                self.running = False
                break

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panda Chat")
        self.resize(700, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: #90EE90; font-family: Helvetica;")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

        self.init_ui()

        self.username = self.get_username()
        if not self.username:
            sys.exit()
        self.connect_to_server()

        # Create a MessageReceiver object and run it in a separate thread
        self.receiver = MessageReceiver(self.client_socket)
        self.receiver.message_received.connect(self.append_message)
        self.receiver_thread = threading.Thread(target=self.receiver.run, daemon=True)
        self.receiver_thread.start()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Chat display area (read-only)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("background-color: #1e1e1e; border: none; font-size: 14px;")
        self.layout.addWidget(self.chat_area)

        # Bottom layout: message entry and Send button
        bottom_layout = QHBoxLayout()
        self.message_entry = QLineEdit()
        self.message_entry.setStyleSheet(
            "background-color: #2e2e2e; border: none; padding: 10px; font-size: 14px;"
        )
        self.message_entry.setPlaceholderText("Type your message here...")
        self.message_entry.returnPressed.connect(self.send_message)
        bottom_layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3e3e3e;
                border: 2px solid #3e3e3e;
                border-radius: 20px;
                padding: 10px 20px;
                color: #90EE90;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)

        self.layout.addLayout(bottom_layout)

    def get_username(self):
        # Use a standard input dialog; you can replace this with a custom dialog if desired.
        username, ok = QInputDialog.getText(self, "Panda Chat", "Enter your panda name:")
        if ok and username.strip():
            return username.strip()
        return None

    def connect_to_server(self):
        try:
            self.client_socket.connect((HOST, PORT))
            self.running = True
            self.client_socket.send(self.username.encode(FORMAT))
            self.append_message(f"Connected to the server as {self.username}.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Unable to connect to server: {e}")
            sys.exit()

    def append_message(self, message):
        self.chat_area.append(message)

    def send_message(self):
        message = self.message_entry.text().strip()
        if message:
            try:
                self.client_socket.send(message.encode(FORMAT))
                if message != "@leaves":
                    self.append_message(f"You: {message}")
                else:
                    self.append_message("You have left the chat.")
                    self.running = False
                self.message_entry.clear()
            except Exception:
                self.append_message("Error sending message.")

    def closeEvent(self, event):
        try:
            if self.running:
                self.client_socket.send("@leaves".encode(FORMAT))
            self.running = False
            self.client_socket.close()
        except Exception:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
