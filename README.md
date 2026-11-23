# Port-scanner
#!/usr/bin/env python3
"""
Simple TCP Port Scanner
Sirf apne machine / lab / un systems par use karo jinki permission ho.

Usage:
    python port_scanner.py 127.0.0.1
    python port_scanner.py scanme.nmap.org -p 1-1024
    python port_scanner.py 192.168.1.1 -p 22,80,443 -t 200
"""

import argparse
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Kuch common ports ke naam
COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt",
}


def parse_ports(port_arg):
    """'1-100' ya '22,80,443' ko list of ints mein convert karta hai."""
    ports = set()
    for part in port_arg.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 1 <= p <= 65535)


def scan_port(host, port, timeout):
    """Ek port check karta hai. Open ho to (port, banner) return karta hai."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                banner = ""
                try:
                    s.settimeout(1)
                    banner = s.recv(100).decode(errors="ignore").strip()
                except Exception:
                    pass
                return port, banner
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description="Simple TCP port scanner")
    parser.add_argument("target", help="IP address ya hostname")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="Ports, e.g. 1-1024 ya 22,80,443 (default: 1-1024)")
    parser.add_argument("-t", "--threads", type=int, default=100,
                        help="Threads ki sankhya (default: 100)")
    parser.add_argument("--timeout", type=float, default=1.0,
                        help="Timeout seconds mein (default: 1.0)")
    args = parser.parse_args()

    try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"[!] Host resolve nahi hua: {args.target}")
        sys.exit(1)

    ports = parse_ports(args.ports)
    print(f"[*] Target: {args.target} ({ip})")
    print(f"[*] {len(ports)} ports scan ho rahe hain...\n")

    start = time.time()
    open_ports = []

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        results = pool.map(lambda p: scan_port(ip, p, args.timeout), ports)
        for result in results:
            if result:
                port, banner = result
                service = COMMON_SERVICES.get(port, "unknown")
                line = f"[+] Port {port:<5} OPEN   {service}"
                if banner:
                    line += f"   | {banner[:50]}"
                print(line)
                open_ports.append(port)

    elapsed = time.time() - start
    print(f"\n[*] Scan complete: {len(open_ports)} open port(s), {elapsed:.2f}s")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] User ne scan rok diya.")
        sys.exit(0)
