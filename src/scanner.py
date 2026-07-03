from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional


def scan_port(target_ip: str, port: int, timeout: float = 1.0) -> bool:
    """Return True when a TCP port accepts connections."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        return result == 0


def scan_range(
    target_ip: str,
    start_port: int,
    end_port: int,
    timeout: float = 1.0,
    max_workers: int = 100,
    progress_callback: Optional[Callable[[int, int, int, bool], None]] = None,
) -> list[int]:
    
    # Scan a port range and return a sorted list of open ports.

    if not target_ip:
        raise ValueError("La IP o host objetivo no puede estar vacía.")
    if not 1 <= start_port <= 65535:
        raise ValueError("El puerto inicial debe estar entre 1 y 65535.")
    if not 1 <= end_port <= 65535:
        raise ValueError("El puerto final debe estar entre 1 y 65535.")
    if start_port > end_port:
        raise ValueError("El puerto inicial no puede ser mayor que el puerto final.")
    if timeout <= 0:
        raise ValueError("El timeout debe ser mayor que 0.")
    if max_workers < 1:
        raise ValueError("El número de hilos debe ser al menos 1.")

    open_ports: list[int] = []
    total_ports = range(start_port, end_port + 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_port, target_ip, port, timeout): port for port in total_ports}
        completed = 0
        total = len(futures)

        for future in as_completed(futures):
            port = futures[future]
            is_open = future.result()
            completed += 1

            if is_open:
                open_ports.append(port)

            if progress_callback is not None:
                progress_callback(completed, total, port, is_open)

    open_ports.sort()
    return open_ports