# honeypot.py
import socket
import threading
import datetime
import json
import time
import os
from typing import Dict, Any

# import your AI engine
from ai_engine import generate_ai_response

CONFIG_PATH = "config.json"

class Honeypot:
    def __init__(self, config: Dict[str, Any]):
        # load config
        self.config = config or {}
        self.bind_ip = self.config.get("bind_ip", "0.0.0.0")
        # ports in config.json are a mapping of port->banner (strings)
        ports_map = self.config.get("ports", {})
        # Accept ports provided as keys (strings) or as list; normalize to dict[int,str]
        self.port_banners = {}
        if isinstance(ports_map, dict):
            for k, v in ports_map.items():
                try:
                    p = int(k)
                    self.port_banners[p] = str(v)
                except Exception:
                    continue
        elif isinstance(ports_map, list):
            for p in ports_map:
                try:
                    self.port_banners[int(p)] = ""
                except Exception:
                    pass
        # fallback default ports if none provided
        if not self.port_banners:
            self.port_banners = {2222: "SSH-2.0-OpenSSH_8.2p1", 8080: "HTTP/1.1 200 OK\r\n\r\n"}

        self.log_dir = self.config.get("log_dir", "logs")
        os.makedirs(self.log_dir, exist_ok=True)

        # allow disabling AI (ai_engine will still fallback)
        self.use_ai = bool(self.config.get("use_ai", True))

        # pass the ai sub-config around
        self.ai_config = self.config.get("ai", {})

    def log_activity(self, port: int, remote_ip: str, input_text: str, output_text: str):
        fname = os.path.join(self.log_dir, f"port_{port}.jsonl")
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "remote_ip": remote_ip,
            "port": port,
            "input": input_text,
            "output": output_text
        }
        try:
            with open(fname, "a", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print(f"[LOG ERROR] Could not write to {fname}: {e}")

    def handle_connection(self, client_sock: socket.socket, addr: tuple, port: int):
        remote_ip = addr[0]
        client_sock.settimeout(10)
        banner = self.port_banners.get(port)
        try:
            if banner:
                # send banner + newline (some services expect CRLF)
                try:
                    client_sock.send((banner + "\r\n").encode())
                except Exception:
                    pass

            buffer = b""
            while True:
                try:
                    data = client_sock.recv(4096)
                except socket.timeout:
                    # no activity - close
                    break
                except Exception:
                    break

                if not data:
                    break

                # accumulate and split by newline so multi-line works
                buffer += data
                # handle every received line separately
                lines = buffer.split(b"\n")
                # keep last partial line in buffer
                buffer = lines.pop() if not buffer.endswith(b"\n") else b""

                for raw in lines:
                    try:
                        cmd = raw.decode("utf-8", errors="ignore").strip()
                    except Exception:
                        cmd = raw.hex()
                    if not cmd:
                        continue

                    # call AI engine to produce a realistic response
                    try:
                        ai_cfg = {"use_ai": self.use_ai, "ai": self.ai_config}
                        response_text = generate_ai_response(cmd, ai_cfg)
                        if response_text is None:
                            response_text = ""
                    except Exception as e:
                        response_text = f"(engine error: {e})"

                    # send response back to the client
                    try:
                        # ensure newline termination
                        client_sock.send((response_text + "\r\n").encode(errors="ignore"))
                    except Exception:
                        pass

                    # log input/output
                    try:
                        self.log_activity(port, remote_ip, cmd, response_text)
                    except Exception as e:
                        print(f"[LOGGING ERROR] {e}")

        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def start_listener(self, port: int):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.bind_ip, port))
            server.listen(8)
            print(f"[+] Listening on {self.bind_ip}:{port}")
            while True:
                try:
                    client, addr = server.accept()
                except Exception as e:
                    print(f"[LISTENER ERROR] accept() failed on port {port}: {e}")
                    time.sleep(1)
                    continue
                t = threading.Thread(target=self.handle_connection, args=(client, addr, port), daemon=True)
                t.start()
        except PermissionError:
            print(f"[!] Permission denied for port {port}. Use a higher port or run with privileges.")
        except Exception as e:
            print(f"[!] Listener for port {port} failed: {e}")

def load_config(path=CONFIG_PATH) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Config file {path} not found. Using defaults.")
        return {}
    except Exception as e:
        print(f"[!] Failed to load config {path}: {e}")
        return {}

def main():
    cfg = load_config()
    honeypot = Honeypot(cfg)

    # start a listener thread per configured port
    for port in honeypot.port_banners.keys():
        t = threading.Thread(target=honeypot.start_listener, args=(port,), daemon=True)
        t.start()

    try:
        print("[*] Honeypot running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down honeypot (keyboard interrupt).")

if __name__ == "__main__":
    main()
