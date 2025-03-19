# Panda Chat Application

## Overview
Panda Chat is a fun, themed chat application split into these 2 parts:

- **Server**: A multi-threaded server that handles multiple client connections, broadcasting messages, and processing special commands.
- **Client**: A GUI client built with Tkinter, featuring a custom title bar, buttons, and an engaging interface for chatting as a panda.

## Features
- **Multi-User Chat**: The server supports multiple clients simultaneously via threading.
- **Panda Decorations**: Enjoy random panda emojis, a custom ASCII art welcome, and fun panda facts.
- **Special Commands**:
  - `@bamboo` – Displays a random panda fact.
  - `@grove` – Shows a list of connected users.
  - `@leaves` – Allows a user to exit the chat gracefully.
- **Custom GUI**: The client includes a customized title bar and rounded buttons for an enhanced user experience.
- **Graceful Shutdown**: The server implements signal handling to cleanly shutdown and notify connected users.

## Installation & Running Instructions

### Requirements
- **Python 3.x**: The project uses standard libraries such as socket, threading, select, and tkinter (which is typically bundled with Python).
- **Tkinter**: Ensure that Tkinter is installed (it usually comes with Python on most systems).

### Running the Server
1. Open a terminal window.
2. Navigate to the project directory.
3. Start the server by running:
   ```bash
   python panda_chat_server.py


### Running the Client(s)
1. Open another terminal (or run on a different machine if you wish to connect over a network).
2. Navigate to the project directory.
3. Start the client by running:
    ```bash
    python panda_chat_client.py


## Challenges Faced
- Concurrency & Thread Safety: Managing multiple client connections simultaneously required careful synchronization, particularly when updating shared resources.
- GUI Customization: Creating a custom title bar and rounded buttons in Tkinter was non-trivial due to the need to override native window decorations.
- Graceful Shutdown: Ensuring that all sockets close properly and clients are notified during a shutdown involved careful exception handling and signal management.

## Extra Features
- Panda ASCII Art: Adds a playful element to the welcome message.
- Custom Title Bar & Rounded Buttons: Enhances the visual appeal and usability of the chat client.
- Enhanced Feedback: Timestamps, decorations, and user-friendly messages make the chat experience more engaging.