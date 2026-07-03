from __future__ import annotations

import ipaddress
import os
import socket
import sys
import time
from typing import Callable

from src import scanner


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
WHITE = "\033[97m"
GRAY = "\033[90m"


def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def supports_unicode() -> bool:
    encoding = sys.stdout.encoding or ""
    return "utf" in encoding.lower()


def stylize(text: str, code: str) -> str:
    if not supports_color():
        return text
    return f"{code}{text}{RESET}"


def banner() -> str:
    title = "PORT SCANNER CLI"
    subtitle = "Detección rápida, visual y precisa de puertos TCP abiertos"
    if supports_unicode():
        border = "═" * 62
        top = f"╔{border}╗"
        title_line = f"║ {title.center(60)} ║"
        subtitle_line = f"║ {subtitle.center(60)} ║"
        bottom = f"╚{border}╝"
    else:
        border = "=" * 62
        top = f"+{border}+"
        title_line = f"| {title.center(60)} |"
        subtitle_line = f"| {subtitle.center(60)} |"
        bottom = f"+{border}+"

    return "\n".join(
        [
            stylize(top, CYAN),
            stylize(title_line, BOLD + WHITE),
            stylize(subtitle_line, DIM + GRAY),
            stylize(bottom, CYAN),
        ]
    )


def prompt_text(message: str) -> str:
    value = input(stylize(message, WHITE)).strip()
    if not value:
        raise ValueError("El valor no puede estar vacío.")
    return value


def prompt_int(message: str, minimum: int, maximum: int) -> int:
    value = int(prompt_text(message))
    if not minimum <= value <= maximum:
        raise ValueError(f"El valor debe estar entre {minimum} y {maximum}.")
    return value


def resolve_target(target: str) -> str:
    try:
        return str(ipaddress.ip_address(target))
    except ValueError:
        return socket.gethostbyname(target)


def get_service_name(port: int) -> str:
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def format_port_rows(open_ports: list[int]) -> list[str]:
    rows = []
    for port in open_ports:
        service = get_service_name(port)
        rows.append(f"  {stylize(str(port).rjust(5), GREEN)}  {stylize('tcp', CYAN)}  {stylize(service, MAGENTA)}")
    return rows


def render_progress() -> Callable[[int, int, int, bool], None]:
    start_time = time.time()
    filled_char = "█" if supports_unicode() else "#"
    empty_char = "░" if supports_unicode() else "-"

    def progress(completed: int, total: int, port: int, is_open: bool) -> None:
        width = 28
        filled = int(width * completed / total) if total else width
        bar = filled_char * filled + empty_char * (width - filled)
        elapsed = max(time.time() - start_time, 0.001)
        speed = completed / elapsed
        status = stylize("OPEN", GREEN) if is_open else stylize("CLOSED", GRAY)
        line = (
            f"\r{stylize('[', CYAN)}{stylize(bar, BLUE)}{stylize(']', CYAN)} "
            f"{completed:>4}/{total:<4}  {status}  puerto {port:<5}  "
            f"{stylize(f'{speed:5.1f} ports/s', DIM + GRAY)}"
        )
        print(line, end="", flush=True)

    return progress


def box_line(label: str, value: str) -> str:
    inner_width = 66
    content = f"{label}: {value}"[:inner_width].ljust(inner_width)
    if supports_unicode():
        return stylize(f"│ {content} │", WHITE)
    return stylize(f"| {content} |", WHITE)


def print_summary(target: str, resolved_target: str, start_port: int, end_port: int, max_workers: int, timeout: float, open_ports: list[int], elapsed: float) -> None:
    print()
    if supports_unicode():
        top = "┌" + "─" * 68 + "┐"
        bottom = "└" + "─" * 68 + "┘"
    else:
        top = "+" + "-" * 68 + "+"
        bottom = "+" + "-" * 68 + "+"

    print(stylize(top, CYAN))
    print(box_line("Objetivo", target))
    print(box_line("Resuelto", resolved_target))
    print(box_line("Rango", f"{start_port} - {end_port}"))
    print(box_line("Hilos", str(max_workers)))
    print(box_line("Timeout", f"{timeout:.2f} s"))
    print(box_line("Tiempo", f"{elapsed:.2f} s"))
    print(stylize(bottom, CYAN))
    print()

    if open_ports:
        print(stylize(f"Puertos abiertos detectados: {len(open_ports)}", GREEN + BOLD))
        print(stylize("Port   Proto  Service", DIM + GRAY))
        print(stylize("" + "-" * 26, GRAY))
        for row in format_port_rows(open_ports):
            print(row)
    else:
        print(stylize("No se detectaron puertos abiertos en el rango analizado.", YELLOW + BOLD))


def main() -> None:
    print(banner())
    print(stylize("Introduce los datos del análisis. El objetivo puede ser una IP o un host resoluble.\n", DIM + GRAY))

    try:
        target = prompt_text("[-] Objetivo: ")
        resolved_target = resolve_target(target)
        start_port = prompt_int("[-] Puerto inicial [1-65535]: ", 1, 65535)
        end_port = prompt_int("[-] Puerto final [1-65535]: ", 1, 65535)
        max_workers = prompt_int("[-] Máximo de hilos [1-1000]: ", 1, 1000)
        timeout = float(prompt_text("[-] Timeout por puerto en segundos [ej. 1.0]: "))

        print()
        print(stylize(f"[*] Escaneando {resolved_target} de {start_port} a {end_port}...", CYAN + BOLD))
        print(stylize("    Progreso en tiempo real y lista final completa al terminar.\n", DIM + GRAY))

        progress = render_progress()
        started_at = time.time()
        open_ports = scanner.scan_range(
            resolved_target,
            start_port,
            end_port,
            timeout=timeout,
            max_workers=max_workers,
            progress_callback=progress,
        )
        elapsed = time.time() - started_at

        print()
        print_summary(target, resolved_target, start_port, end_port, max_workers, timeout, open_ports, elapsed)

    except ValueError as exc:
        print(stylize(f"[!] Entrada no válida: {exc}", RED + BOLD), file=sys.stderr)
        raise SystemExit(1) from exc
    except socket.gaierror as exc:
        print(stylize(f"[!] No se pudo resolver el objetivo: {exc}", RED + BOLD), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()