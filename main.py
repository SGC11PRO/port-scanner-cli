import sys
from src import scanner

def main() -> None:
    target_ip = input ("[-] Introduce la IP objetivo: ").strip()
    start_port = int(input ("[-] Puerto inicial: ").strip())
    end_port = int(input ("[-] Puerto final: ").strip())
    max_workers = int(input ("[-] Número máximo de hilos (threads): ").strip())
    
    print (f"\n[*] Escaneando {target_ip} desde el puerto {start_port} hasta el puerto {end_port}...\n")
    
    open_ports = scanner.scan_range(target_ip, start_port, end_port, max_workers=max_workers)
    
    print (f"\n[*] Escaneo completado. Puertos abiertos: {len(open_ports)}")
    if open_ports:
        print (open_ports)
        
        
if __name__ == "__main__":
    main()