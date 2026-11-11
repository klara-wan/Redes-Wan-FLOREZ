# docs/seguridad.md — Medidas de seguridad aplicadas

## Contraseñas y secretos
- El repositorio no contiene claves ni tokens; `.gitignore` excluye `.env`, `*.key` y `*.pem`.
- Las configuraciones generadas usan marcadores `CAMBIAR_*`; el usuario debe reemplazarlos y guardarlos en un vault, no en el código.
- El auditor detecta claves incrustadas (`password`, `secret`, etc.) y **las enmascara** al mostrarlas.

## Validación de entradas (backend, Pydantic)
- Bloque IPv4 exacto, prefijo IPv6, IP y AS del ISP; cantidades de usuarios con límites.
- Topologías: nombres solo con letras, números, `-` y `_`; roles y marcas permitidos; enlaces solo entre equipos existentes; máximo 200 equipos y 1000 enlaces.
- Tamaño máximo de la configuración a auditar: 200 000 caracteres.
- En el navegador todo texto externo se escapa antes de mostrarse (evita inyectar HTML o scripts).

## Configuraciones seguras por defecto
Todas las marcas generan: SSHv2 sin Telnet ni HTTP, usuario administrador local, SNMPv3, NTP, Syslog, STP con protección BPDU, DHCP Snooping y lista de acceso para el plano de gestión. Cada configuración generada se audita y las pruebas exigen cero hallazgos altos (P35).

## Accesos y operación
- Ningún comando se aplica solo: el envío por SSH está simulado y requiere aprobación humana.
- El backend es stateless y no guarda datos de clientes. CORS configurable con `NETPLAN_CORS`.
- Auditoría de acciones con fecha y usuario en la herramienta.

## Limitaciones conocidas
- No hay autenticación real: los roles de usuario son informativos hasta conectar JWT.
- Los marcadores `CAMBIAR_*` siguen siendo responsabilidad del usuario.
- El auditor usa reglas por patrón; no reemplaza una revisión de seguridad completa.
