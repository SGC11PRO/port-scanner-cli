import socket
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_port (target_ip: str, port: int, timeout: float = 1.0) -> bool:
    # Intenta conectarse a un puerto concreto de una IP
    # Devuelve true si está abierto, false si no.
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    result = sock.connect_ex((target_ip, port)) # sock.connect_ex devuelve 0 si la conexión fue exitosa, o un código de error si no lo fue.
    sock.close()
    
    return result == 0 # Devuelve true si result == 0 -> connect_ex fue exitoso

def scan_range (target_ip: str, start_port: int, end_port: int, timeout: float = 1.0, max_workers: int = 100) -> list[int]:
    # Escanea un rango de puertos en una IP objetivo
    # Devuelve una lista de puertos abiertos.
    
    open_ports = []
    total_ports = range(start_port, end_port + 1)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_port, target_ip, port, timeout): port for port in total_ports}
    
        for future in tqdm(as_completed(futures), total=len(futures), desc="[-] Escaneando puertos", unit="puerto"):
            port = futures[future]
            if future.result():
                open_ports.append(port)
                tqdm.write(f"[+] Puerto {port} abierto")
    
    open_ports.sort() # Ordena la lista de puertos abiertos antes de devolverla
    return open_ports