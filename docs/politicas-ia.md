# docs/politicas-ia.md — Ciberdefensa contra IA

Reglas con las que se construyó y se usa la herramienta. Estado real de cada una:

| Regla | Estado |
|---|---|
| No guardar secretos: el repositorio ignora `.env`, `*.key`, `*.pem` (`.gitignore`) y las configuraciones generadas usan marcadores `CAMBIAR_*`, nunca claves reales | Cumplida |
| Validar entradas: CIDR, prefijo IPv6, ISP y AS se validan con Pydantic en el backend; se rechazan valores como `999.1.1.1/24` o `2001:db8;rm -rf` (pruebas P03-P08) | Cumplida |
| Advertir configuraciones inseguras: toda configuración generada desactiva Telnet/HTTP, exige SSHv2 y deja el asesor crítico señalando los secretos por reemplazar | Cumplida: la topología importada se valida y se advierte de equipos aislados, un solo core o falta de ISP (pruebas P19-P26) |
| Prompt injection: el agente del chat es por reglas (no ejecuta instrucciones escondidas en archivos) y el backend no envía datos del usuario a ningún modelo de IA | Cumplida (revisar si se conecta un LLM) |
| Revisión humana: ningún comando se aplica solo; el envío por SSH está simulado y requiere aprobación | Cumplida |
| No pegar datos reales en la IA: IPs, credenciales o `.env` reales no se comparten en el chat | Práctica personal |

Topologías importadas: se valida el formato, los nombres (solo letras, números, - y _), roles, IPs y enlaces; el contenido nunca se ejecuta y se escapa antes de mostrarlo en pantalla. Solo se acepta el formato JSON descrito en el manual.
