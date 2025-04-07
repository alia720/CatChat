# Cat Chat Application

## Overview
Cat Chat is a playful, feline-themed chat application divided into two components:

- **Server**: A multi-threaded server handling multiple client connections, broadcasting messages, and responding to special commands.
- **Client**: A GUI client built with Tkinter, featuring a soft color palette and an engaging interface for chatting as a cat.

## Features
- **Multi-User Chat**: The server supports multiple clients simultaneously via threading.
- **Cat Decorations**: Chat messages adorned with cat emojis and playful feline-themed elements.
- **Special Commands**:
  - `@nap` – Allows a user to gracefully exit the chat.
  - `@catnip` – Displays a random cat fact.
  - `@purr` – Shows a list of all connected cats.
- **Cat-Themed GUI**: Soft pastel interface with cat-themed elements for an enhanced user experience.
- **UTF-8 Support**: Robust handling of message encoding for reliable emoji and special character transmission.
- **Graceful Shutdown**: Both server and client implement proper shutdown protocols to ensure clean disconnections.

## Installation & Running Instructions

### Requirements
- **Python 3.x**: The project uses standard libraries including socket, threading, and tkinter (typically bundled with Python).
- **Tkinter**: Ensure that Tkinter is installed (usually comes with Python installations).

### Running the Server
1. Open a terminal window.
2. Navigate to the project directory.
3. Start the server by running:
   ```bash
   python cat_chat_server.py
   ```

### Running the Client(s)
1. Open another terminal (or run on a different machine for network connections).
2. Navigate to the project directory.
3. Start the client by running:
   ```bash
   python cat_chat_client.py
   ```
