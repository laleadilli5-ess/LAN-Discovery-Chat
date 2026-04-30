# LAN-Discovery-Chat
Decentralized P2P LAN Discovery and Chat tool using UDP Broadcast with Liveness Detection(Heartbeat&amp;Timeout).
This is a Peer-to-Peer (P2P) chat application for local networks. It allows computers on the same WiFi/LAN to find each other automatically and chat without needing a central server. 

## How it works
The project uses **UDP Broadcasting** to handle node discovery. Since there is no server, every node (terminal) is responsible for keeping track of its neighbors.

### Key Logic:
*   **Discovery:** When you start the app, it sends a `JOIN` message to the whole network. Other active nodes hear this and add you to their list.
*   **Liveness (Heartbeats):** To make sure everyone is still online, each node sends a "Heartbeat" signal every 2 seconds.
*   **Disappearance Handling:** If a node doesn't send a signal for 10 seconds, the system assumes it crashed or disconnected and removes it from the list.
*   **Graceful Exit:** If you type `exit`, it sends a `LEAVE` message so others can remove you instantly.

## Technical Details
*   **Language:** Python 3
*   **Networking:** UDP Socket Programming
*   **Concurrency:** Python `threading` (used for running the receiver and the liveness monitor in the background).
*   **Data Format:** JSON (used for sending structured messages like type, sender_ip, and text).

## How to Run
1. Open your terminal.
2. Run the script:
   ```bash
   python node.py
Open more terminals to see them connect to each other.

Commands:

Type anything to send a message.

list: See who is currently online.

exit: Leave the chat.

## Code Structure
- `receiver()`: A background thread that listens for incoming UDP packets on Port 5005.
- `heartbeat_sender()`: Periodically broadcasts a keep-alive signal to the network.
- `liveness_monitor()`: Scans the peer list and removes any node that has been inactive for more than 10 seconds.
- `send_broadcast()`: A helper function that packs data into JSON format and broadcasts it.

