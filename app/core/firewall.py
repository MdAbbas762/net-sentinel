import socket
import threading
import time
from collections import defaultdict
from config import (RATE_LIMIT, TRUSTED_IPS, SECURITY_LEVELS, LOG_FILE,
                    BACKEND_HOST, BACKEND_PORT, FIREWALL_HOST, FIREWALL_PORT,
                    ADMIN_HOST, ADMIN_PORT)

BLACKLIST = set()
request_count = defaultdict(int)
lock = threading.Lock()

def log_event(event, ip, reason="N/A"):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    msg = f"[{timestamp}] {event}: IP={ip}, Reason={reason}\n"
    print(msg.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg)

def rate_limiter(ip):
    request_count[ip] += 1
    if request_count[ip] > RATE_LIMIT:
        BLACKLIST.add(ip)
        log_event("BLOCKED", ip, "Rate limit exceeded")
        return False
    return True

def enforce_mls(ip, level):
    if ip in BLACKLIST:
        log_event("BLOCKED", ip, "Blacklisted")
        return False
    if level > SECURITY_LEVELS["medium"] and ip not in TRUSTED_IPS:
        log_event("BLOCKED", ip, "MLS violation")
        return False
    log_event("ALLOWED", ip, "Access granted")
    return True

def recv_until_headers_end(conn, max_bytes=65536):
    conn.settimeout(3)
    data = b""
    while b"\r\n\r\n" not in data and len(data) < max_bytes:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

def parse_security_level_from_headers(header_bytes):
    level = SECURITY_LEVELS["low"]
    try:
        header_text = header_bytes.decode("iso-8859-1", errors="replace")
        for line in header_text.split("\r\n"):
            if line.lower().startswith("x-sec-level:"):
                value = line.split(":", 1)[1].strip()
                if value.isdigit():
                    level = int(value)
                elif value.lower() in SECURITY_LEVELS:
                    level = SECURITY_LEVELS[value.lower()]
                break
    except Exception:
        pass
    return level

def http_forbidden(conn):
    body = b"403 Forbidden (Blocked by firewall)\n"
    response = (b"HTTP/1.1 403 Forbidden\r\n"
                b"Content-Type: text/plain\r\n"
                b"Connection: close\r\n" +
                f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
    try:
        conn.sendall(response)
    except Exception:
        pass

def proxy_to_backend(client_conn, initial_data):
    backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backend.settimeout(5)
    try:
        backend.connect((BACKEND_HOST, BACKEND_PORT))
        backend.sendall(initial_data)
        client_conn.settimeout(1)
        try:
            while True:
                more = client_conn.recv(4096)
                if not more:
                    break
                backend.sendall(more)
                if len(more) < 4096:
                    break
        except Exception:
            pass
        while True:
            chunk = backend.recv(4096)
            if not chunk:
                break
            client_conn.sendall(chunk)
    finally:
        backend.close()

def handle_client(conn, addr):
    ip = addr[0]
    try:
        data = recv_until_headers_end(conn)
        if not data:
            return
        level = parse_security_level_from_headers(data)
        with lock:
            allowed = rate_limiter(ip) and enforce_mls(ip, level)
        if not allowed:
            http_forbidden(conn)
            return
        proxy_to_backend(conn, data)
    except Exception as exc:
        log_event("ERROR", ip, str(exc))
        http_forbidden(conn)
    finally:
        conn.close()

def start_firewall(host=FIREWALL_HOST, port=FIREWALL_PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(50)
    print(f"[+] Firewall proxy listening on {host}:{port} -> {BACKEND_HOST}:{BACKEND_PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def handle_admin(conn):
    try:
        cmd = conn.recv(1024).decode(errors="ignore").strip()
        parts = cmd.split()
        with lock:
            if len(parts) == 2 and parts[0].upper() == "BLOCK":
                BLACKLIST.add(parts[1])
                log_event("MANUAL BLOCK", parts[1], "Blocked via GUI")
                conn.sendall(b"OK: IP BLOCKED\n")
            elif len(parts) == 2 and parts[0].upper() == "UNBLOCK":
                BLACKLIST.discard(parts[1])
                request_count[parts[1]] = 0
                log_event("UNBLOCKED", parts[1], "Unblocked via GUI")
                conn.sendall(b"OK: IP UNBLOCKED\n")
            else:
                conn.sendall(b"ERROR: INVALID COMMAND\n")
    finally:
        conn.close()

def start_admin_server(host=ADMIN_HOST, port=ADMIN_PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[+] Admin control listening on {host}:{port}")
    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_admin, args=(conn,), daemon=True).start()

def run():
    threading.Thread(target=start_admin_server, daemon=True).start()
    start_firewall()

if __name__ == "__main__":
    run()
