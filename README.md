# Port Scanner CLI

Una utilidad de línea de comandos para escanear rangos de puertos TCP con una salida visual más clara, progresiva y profesional.

## Uso

1. Ejecuta `python main.py`.
2. Introduce un host o una IP IPv4.
3. Define el puerto inicial, el puerto final, el número de hilos y el timeout por puerto.

## Qué muestra

- Un banner inicial con estilo de terminal.
- Progreso en tiempo real durante el escaneo.
- Una lista final completa de puertos abiertos con servicio detectado cuando existe.

## Notas

- El proyecto ya no depende de paquetes externos.
- Si usas un host en lugar de una IP, primero se resolverá a IPv4.