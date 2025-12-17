# simulate_clients.py
import socket
import time
import random

HOST = "127.0.0.1"
PORTS = [2222, 8021, 8080]
COMMANDS = [
    "ls -la",
    "whoami",
    "pwd",
    "cat /etc/passwd",
    "cd /var/log",
    "uname -a",
    "id",
    "ls /home",
    "GET /index.html",
    "POST /login"
]

def simulate_once(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((HOST, port))
        # optionally receive banner
        try:
            banner = s.recv(1024)
            # print("Banner:", banner.decode(errors='ignore'))
        except:
            pass
        for _ in range(random.randint(1,4)):
            cmd = random.choice(COMMANDS)
            s.send((cmd + "\r\n").encode())
            try:
                data = s.recv(4096)
                # print("Response:", data.decode(errors='ignore'))
            except:
                pass
            time.sleep(random.uniform(0.5, 1.8))
        s.close()
    except Exception as e:
        print(f"Simulate error on port {port}: {e}")

if __name__ == "__main__":
    # do multiple simulated clients
    for _ in range(6):
        port = random.choice(PORTS)
        simulate_once(port)
        time.sleep(random.uniform(0.5, 1.5))
    print("Simulation finished.")