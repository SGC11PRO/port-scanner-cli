# Port Scanner CLI

A concurrent TCP port scanner built with Python to learn networking fundamentals and socket programming.

Built as a learning project ahead of starting a Computer Engineering degree, with a focus on cybersecurity.

---

## Disclaimer — Read before using

This tool is intended **exclusively for educational purposes and for scanning systems you own or are explicitly authorized to test** (e.g. your own machine, your own local network, or platforms designed for legal practice such as TryHackMe or HackTheBox).

Scanning systems without authorization may be illegal depending on your jurisdiction. The author takes no responsibility for misuse of this tool.

---

## Overview

Given a target IP address and a port range, this tool checks which TCP ports are open by attempting a real TCP handshake against each one. It uses multithreading to scan hundreds of ports in seconds instead of minutes, and displays live progress in the terminal.

## Features

- Scans any TCP port range on a given IPv4 address
- Concurrent scanning using a thread pool (configurable worker count)
- Live progress bar with real-time count of ports scanned
- Simple, dependency-light implementation built on Python's standard library (plus `tqdm` for the progress bar)

## How it works

| Concept | What it does | Why it matters |
|---|---|---|
| TCP three-way handshake | Attempts a real connection to each port | A completed handshake means a service is listening (port open) |
| `socket.connect_ex()` | Attempts the connection without raising exceptions | Returns `0` on success, an error code otherwise — cleaner for scanning many ports in a loop |
| Timeout per port | Caps how long each attempt waits for a response | Prevents the scan from hanging indefinitely on filtered ports |
| `ThreadPoolExecutor` | Runs many port checks concurrently instead of one by one | Turns a scan that could take minutes into one that takes seconds |

## Project structure

```
port-scanner-cli/
│
├── main.py                 # CLI entry point
├── src/
│   └── scanner.py          # Port scanning logic (sequential check + concurrent range scan)
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Getting started

### Requirements

- Python 3.10+

### Installation

```bash
git clone https://github.com/your-username/port-scanner-cli.git
cd port-scanner-cli
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Usage

```bash
python main.py
```

You'll be prompted for a target IP address and a port range. The tool will scan the range concurrently and print any open ports found, along with a live progress bar.

**Example:**
```
[-] Introduce la IP objetivo: 127.0.0.1
[-] Puerto inicial: 1
[-] Puerto final: 500

[*] Escaneando 127.0.0.1 desde el puerto 1 hasta el puerto 500...

[-] Escaneando puertos: 100%|██████████| 500/500 [00:03<00:00, 142.85puerto/s]
[+] Puerto 135 abierto
[+] Puerto 445 abierto

[*] Escaneo completado. Puertos abiertos: 2
[135, 445]
```

## What I learned building this

- The fundamentals of how TCP/IP addressing works: IP addresses identify machines, ports identify services within them
- The TCP three-way handshake, and how a port scanner uses it to detect open ports
- Why UDP scanning requires a different approach, since UDP is connectionless
- The real-world cost of a sequential scan when ports are filtered (each check blocks until timeout), and how threading solves it
- Using `concurrent.futures.ThreadPoolExecutor` to run many I/O-bound tasks in parallel, including tracking results back to their original input via a futures-to-port mapping
- Why concurrency has practical limits (system resources, network load) rather than always using as many threads as possible

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.