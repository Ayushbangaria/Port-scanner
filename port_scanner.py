#!/usr/bin/env python3
"""
Simple TCP Port Scanner
Use only on your own machine, your lab, or systems you have permission to scan.

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

# Names of some common ports
COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt",
}


def parse_ports(port_arg):
    """Convert '1-100' or '22,80,443' into a sorted list of port numbers."""
    ports = set()
    for part in port_arg.split(","):
        part = part.strip()
        if "-" in part:
            # Range such as 1-100
            start, end = part.split("-")
            ports.update(range(int(start), int(end) + 1))
        else:
            # Single port such as 80
            ports.add(int(part))
    # Keep only valid port numbers (1-65535)
    return sorted(p for p in ports if 1 <= p <= 65535)


def scan_port(host, port, timeout):
    """Check a single port. If it is open, return (port, banner), else None."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            # connect_ex returns 0 when the connection succeeds (port is open)
            if s.connect_ex((host, port)) == 0:
                banner = ""
                try:
                    # Try to read the service banner (greeting text), if any
                    s.settimeout(1)
                    banner = s.recv(100).decode(errors="ignore").strip()
                except Exception:
                    # Many services send nothing until we talk first; ignore
                    pass
                return port, banner
    except Exception:
        # Any connection error means we treat the port as closed/unreachable
        pass
    return None


def main():
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Simple TCP port scanner")
    parser.add_argument("target", help="IP address or hostname to scan")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="Ports to scan, e.g. 1-1024 or 22,80,443 (default: 1-1024)")
    parser.add_argument("-t", "--threads", type=int, default=100,
                        help="Number of threads (default: 100)")
    parser.add_argument("--timeout", type=float, default=1.0,
                        help="Connection timeout in seconds (default: 1.0)")
    args = parser.parse_args()

    # Resolve the hostname to an IP address
    try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"[!] Could not resolve host: {args.target}")
        sys.exit(1)

    ports = parse_ports(args.ports)
    print(f"[*] Target: {args.target} ({ip})")
    print(f"[*] Scanning {len(ports)} ports...\n")

    start = time.time()
    open_ports = []

    # Scan many ports at the same time using a pool of threads
    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        results = pool.map(lambda p: scan_port(ip, p, args.timeout), ports)
        for result in results:
            if result:
                port, banner = result
                # Look up the service name, or show "unknown"
                service = COMMON_SERVICES.get(port, "unknown")
                line = f"[+] Port {port:<5} OPEN   {service}"
                if banner:
                    # Show only the first 50 characters of the banner
                    line += f"   | {banner[:50]}"
                print(line)
                open_ports.append(port)

    elapsed = time.time() - start
    print(f"\n[*] Scan complete: {len(open_ports)} open port(s), {elapsed:.2f}s")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Exit cleanly if the user presses Ctrl+C
        print("\n[!] Scan stopped by user.")
        sys.exit(0)