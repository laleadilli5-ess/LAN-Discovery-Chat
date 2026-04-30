import socket
import threading
import time
import json
import signal
import sys

PORT = 5005 
HB_INTERVAL = 2 # Heartbeat interval
TIMEOUT = 10    # After 10s of silence, peer is removed

MY_IP = socket.gethostbyname(socket.gethostname())
MY_ID = str(time.time())
peers = {} # {peer_id: {'ip': ip, 'last_seen': time}}
lock = threading.Lock()

def send_broadcast(msg_type, text=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    payload = {"type": msg_type, "sender_ip": MY_IP, "sender_id": MY_ID, "text": text}
    try:
        sock.sendto(json.dumps(payload).encode('utf-8'), ('<broadcast>', PORT))
    except: pass
    finally: sock.close()

def heartbeat_sender():
    while True:
        send_broadcast('HEARTBEAT')
        time.sleep(HB_INTERVAL)

def liveness_monitor():
    while True:
        now = time.time()
        with lock:
            to_remove = [pid for pid, info in peers.items() if now - info['last_seen'] > TIMEOUT]
            for pid in to_remove:
                print(f"\n[TIMEOUT]: Peer {peers[pid]['ip']} has disappeared.")
                del peers[pid]
                print("> ", end="", flush=True)
        time.sleep(2)

def receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PORT))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data.decode('utf-8'))
            if msg['sender_id'] != MY_ID:
                pid = msg['sender_id']
                with lock:
                    if pid not in peers and msg['type'] != 'LEAVE':
                        print(f"\n[NEW PEER]: {msg['sender_ip']} joined.")
                    if msg['type'] == 'LEAVE':
                        if pid in peers:
                            print(f"\n[LEFT]: {msg['sender_ip']} left.")
                            del peers[pid]
                    else:
                        peers[pid] = {'ip': msg['sender_ip'], 'last_seen': time.time()}
                        if msg['type'] == 'CHAT':
                            print(f"\n[MSG FROM {msg['sender_ip']}]: {msg['text']}")
                print("> ", end="", flush=True)
        except: pass

if __name__ == "__main__":
    print(f"--- LAN PROJECT (IP: {MY_IP}) ---")
    threading.Thread(target=receiver, daemon=True).start()
    threading.Thread(target=heartbeat_sender, daemon=True).start()
    threading.Thread(target=liveness_monitor, daemon=True).start()
    
    send_broadcast('JOIN')
    
    while True:
        try:
            cmd = input("> ")
            if cmd.lower() == 'exit':
                send_broadcast('LEAVE')
                break
            elif cmd.lower() == 'list':
                with lock:
                    print(f"Active Peers: {[p['ip'] for p in peers.values()]}")
            else:
                send_broadcast('CHAT', cmd)
        except KeyboardInterrupt:
            send_broadcast('LEAVE')
            break