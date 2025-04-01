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

## Challenges Faced
- **UTF-8 Message Handling**: Ensuring proper encoding/decoding of messages, especially with emojis and when messages split across network packets.
- **Concurrency Management**: Coordinating multiple client connections while maintaining thread safety for shared resources.
- **UI/UX Design**: Creating a visually appealing, cat-themed interface that maintains usability and charm.
- **Network Resilience**: Implementing robust error handling for network disconnections and transmission issues.

## Extra Features
- **Cat Name Selection**: Users can choose their own cat name when joining the chat.
- **Message Buffering**: Advanced handling of incomplete UTF-8 sequences for reliable communication.
- **Responsive Design**: The chat interface adapts to window resizing for a better user experience.
- **Visual Feedback**: Clear visual indications when messages are sent and received.

## Future Enhancements
- **Direct Messages**: Allow cats to send private whispers to each other.
- **File Sharing**: Implement the ability to share images and files with other cats.
- **Custom Avatars**: Allow users to select or upload cat avatars.
- **Chat Rooms**: Support for multiple chat rooms or "cat colonies".