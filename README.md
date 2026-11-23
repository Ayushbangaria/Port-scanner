# Python TCP Port Scanner

A simple, fast, multi-threaded TCP port scanner written in pure Python. It checks which ports are open on a target machine and tries to identify the service running on each one using banner grabbing.

Built as a beginner-friendly cybersecurity project to understand how network scanning works under the hood, without relying on tools like Nmap.

> **Disclaimer:** Use this tool only on systems you own or have explicit written permission to test. Scanning networks without permission may be illegal in your country. The author is not responsible for any misuse.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Command-Line Options](#command-line-options)
- [Example Output](#example-output)
- [Project Structure](#project-structure)
- [Code Walkthrough](#code-walkthrough)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Legal and Ethical Use](#legal-and-ethical-use)
- [License](#license)

---

## Features

- TCP connect scanning of single ports, lists, or ranges
- Multi-threaded scanning for speed (configurable thread count)
- Banner grabbing to identify services such as SSH, FTP, or VMware daemons
- Built-in names for common services (HTTP, HTTPS, SSH, SMB, MySQL, RDP, and more)
- Hostname resolution (scan by domain name or IP address)
- Configurable connection timeout
- Scan duration reporting
- Clean exit on `Ctrl+C`
- No external dependencies, only the Python standard library

---

## How It Works

The scanner uses a **TCP connect scan**, the simplest and most reliable scanning method:

1. The scanner tries to open a full TCP connection (three-way handshake) to each target port.
2. If the connection succeeds, the port is **open**, because a service is listening on it.
3. If the connection is refused or times out, the port is **closed** or **filtered** (for example, blocked by a firewall).
4. For open ports, the scanner waits briefly for the service to send a **banner**, a short greeting message that often reveals the software name and version.

To keep scans fast, many ports are checked at the same time using a thread pool (`ThreadPoolExecutor`).

```
 +-----------+      TCP SYN       +--------------+
 |  Scanner  | -----------------> | Target port  |
 |           | <----------------- |              |
 +-----------+   SYN/ACK = open   +--------------+
                 RST/timeout = closed or filtered
```

---

## Requirements

- Python 3.7 or newer
- Any operating system (Windows, Linux, macOS)
- No third-party packages needed

Check your Python version:

```bash
python --version
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/python-port-scanner.git
cd python-port-scanner
```

Or simply download `port_scanner.py` and place it in any folder.

---

## Usage

Open a terminal **in the folder that contains the script** and run:

```bash
python port_scanner.py <target> [options]
```

### Examples

Scan your own computer (ports 1 to 1024 by default):

```bash
python port_scanner.py 127.0.0.1
```

Scan all 65,535 ports:

```bash
python port_scanner.py 127.0.0.1 -p 1-65535
```

Scan specific ports only:

```bash
python port_scanner.py 192.168.1.1 -p 22,80,443
```

Scan a range plus extra ports:

```bash
python port_scanner.py 127.0.0.1 -p 1-1000,3306,8080
```

Use more threads and a shorter timeout for a faster scan on localhost:

```bash
python port_scanner.py 127.0.0.1 -t 300 --timeout 0.3
```

Scan the official Nmap test server (allowed by its owners for testing):

```bash
python port_scanner.py scanme.nmap.org -p 1-1024
```

> **Tip:** Do not run the script using the play button in your editor. It needs a target argument, so always run it from a terminal.

---

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `target` | | IP address or hostname to scan (required) | none |
| `--ports` | `-p` | Ports to scan, e.g. `1-1024` or `22,80,443` | `1-1024` |
| `--threads` | `-t` | Number of threads used for scanning | `100` |
| `--timeout` | | Connection timeout in seconds | `1.0` |
| `--help` | `-h` | Show the help message | |

---

## Example Output

```
[*] Target: 127.0.0.1 (127.0.0.1)
[*] Scanning 1024 ports...

[+] Port 135   OPEN   unknown
[+] Port 445   OPEN   SMB
[+] Port 902   OPEN   unknown   | 220 VMware Authentication Daemon Version 1.10: SSL
[+] Port 912   OPEN   unknown   | 220 VMware Authentication Daemon Version 1.0, Serv

[*] Scan complete: 4 open port(s), 11.08s
```

In this example, the banners on ports 902 and 912 reveal that VMware is installed, even though the scanner does not have those ports in its built-in service list. Ports 135 and 445 are standard Windows services (RPC and SMB).

---

## Project Structure

```
python-port-scanner/
|-- port_scanner.py    # The scanner (single file)
|-- README.md          # Project documentation
```

---

## Code Walkthrough

### `COMMON_SERVICES`
A dictionary that maps well-known port numbers to service names (for example, `22 -> SSH`). Ports not in this list are shown as `unknown`. You can add more entries to it.

### `parse_ports(port_arg)`
Converts the user's port string into a sorted list of integers. It understands:
- single ports: `80`
- lists: `22,80,443`
- ranges: `1-1024`
- combinations: `1-1000,3306,8080`

Invalid port numbers (outside 1 to 65535) are discarded.

### `scan_port(host, port, timeout)`
Checks one port:
1. Creates a TCP socket and applies the timeout.
2. Calls `connect_ex()`, which returns `0` if the connection succeeds.
3. If the port is open, it tries to read up to 100 bytes as a banner.
4. Returns `(port, banner)` for open ports, or `None` otherwise.

### `main()`
- Parses command-line arguments with `argparse`.
- Resolves the hostname to an IP address with `socket.gethostbyname()`.
- Runs `scan_port` for every port in parallel using `ThreadPoolExecutor`.
- Prints results as they are collected and shows a summary with the total scan time.

---

## Limitations

- Only **TCP** is supported (no UDP scanning).
- Uses a full **connect scan**, which is reliable but easy for firewalls and intrusion detection systems to log. It is not a stealth scan.
- Banner grabbing only works for services that send a greeting first (SSH, FTP, SMTP, VMware, etc.). Web servers and many others stay silent until they receive a request, so their banner will be empty.
- Only IPv4 is supported.
- A very high thread count on a slow network may cause missed ports or errors.
- Firewalls may silently drop packets, so "closed" can also mean "filtered".

---

## Future Improvements

- Save results to CSV, JSON, or TXT with an `-o` option
- Add names for more services, for example RPC (135) and VMware (902, 912)
- UDP scanning
- SYN (half-open) scanning using Scapy
- Send a probe (such as an HTTP request) to get banners from silent services
- IPv6 support
- Scan an entire subnet (for example `192.168.1.0/24`)
- Simple GUI using Tkinter or a web dashboard using Flask
- Risk report that flags insecure services (Telnet, FTP, open SMB)
- Compare accuracy and speed against Nmap

---

## Legal and Ethical Use

Port scanning is a standard part of security testing, but it must be done responsibly:

- Scan only your own devices, your own lab, or systems where you have written permission.
- Do not scan public servers, company networks, or other people's devices without authorization.
- Safe practice targets: `127.0.0.1` (your own machine), virtual machines in your own lab, or `scanme.nmap.org` (provided by the Nmap project for testing).

---

## License

This project is released under the MIT License. You are free to use, modify, and distribute it, provided the license notice is kept. Add a `LICENSE` file to your repository to make this official.

---

## Author

Created as a cybersecurity learning project. Contributions, issues, and suggestions are welcome.
