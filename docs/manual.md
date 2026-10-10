# Manual de usuario — NetPlan

NetPlan ayuda a diseñar una red: calcula el direccionamiento (VLSM IPv4 y /64 IPv6), genera los comandos de cada equipo, evalúa el diseño y exporta Excel y Word.

## 1. Requisitos
- Un navegador moderno (para `index.html`).
- Python 3.10 o superior (solo para el backend: evaluación, Excel y Word).

## 2. Puesta en marcha
1. Backend (en una terminal): `cd backend`, luego `pip install -r requirements.txt` y `uvicorn app.main:app --port 8000`.
2. Frontend: abrir `index.html` con doble clic.
3. Comprobar el backend en http://localhost:8000/api/health (debe responder `{"status":"ok"}`).

## 3. Cómo usarla (pestañas)
| Pestaña | Para qué sirve |
|---|---|
| 01 Topología | Diagrama de los clientes creados. |
| 02 Clientes | Alta de un cliente con usuarios y servicios (datos, voz, video, IoT); asigna subred y VLAN. |
| 03 Sedes (VLSM) | Ingresa nombre, bloque base (ej. `172.16.0.0/21`), prefijo IPv6 y los pisos con sus usuarios. Muestra la tabla VLSM y el diagrama de la sede. El botón **Editar** carga la sede en el formulario para cambiarla. |
| 04 Configuración | Elige sede, marca, modelo, versión y opciones de seguridad; muestra los comandos listos para copiar. |
| 05 Auditoría | Registro de acciones con fecha y usuario. |
| 06 Agente IA | Chat por reglas: crear cliente, estado del pool, ir a topología, preparar configuración. |
| 07 Usuarios | Crear usuarios y cambiar de sesión; historial de sesiones. |
| 08 Proyecto | Con el backend encendido: clasifica la red, calcula el porcentaje de éxito, lista mejoras, muestra los comandos de cada equipo y descarga Excel y Word. |

## 4. Paso a paso: de los datos a los comandos
1. En **Sedes (VLSM)** escribe el nombre, el bloque base y los pisos con sus usuarios; pulsa **Calcular direccionamiento VLSM**.
2. Revisa la tabla: red, prefijo, máscara, primera/última IP, broadcast, hosts útiles e IPv6.
3. En **Proyecto** elige la sede, la marca (Cisco, MikroTik, Huawei, Juniper, Aruba) y la versión; marca si hay redundancia o ISP redundante y el crecimiento esperado.
4. Pulsa **Analizar proyecto**. Elige un equipo (CORE, DIST, ACC-...) para ver sus comandos.
5. Descarga el Excel (tablas VLSM y evaluación) y el Word (explicación de la infraestructura).

## 5. Cómo leer el porcentaje de éxito
Parte de 100% y resta por cada debilidad (sin redundancia, un solo ISP, sin margen de crecimiento, subredes justas, bloque casi agotado, secretos de ejemplo). Cada hallazgo trae su mejora. Con las claves de ejemplo y sin red de gestión fuera de banda no se llega a 100%.

## 6. Seguridad y buenas prácticas
- Reemplaza todos los `CAMBIAR_*` por valores propios antes de aplicar una configuración; nunca los guardes en el repositorio (usa `.env`, que está en `.gitignore`).
- Revisa cada comando antes de pegarlo en un equipo y pruébalo primero en un laboratorio.
- No uses IPs ni credenciales reales de producción en el chat ni en capturas.

## 7. Pruebas
`cd backend && pytest -v` ejecuta las pruebas; el resultado está en `docs/pruebas.md`.

## 8. Problemas frecuentes
| Síntoma | Solución |
|---|---|
| "No se pudo conectar al backend" | Inicia `uvicorn app.main:app --port 8000` y revisa la URL en la pestaña Proyecto. |
| "Datos inválidos" al analizar | El bloque debe ser una dirección de red exacta (`172.16.0.0/21`, no `172.16.0.5/21`). |
| "El bloque no alcanza" | Usa un bloque mayor o reduce el crecimiento esperado. |
| Al recargar se pierden los datos | El estado vive en memoria; exporta el Excel antes de cerrar. |

## 9. Limitaciones actuales
- El envío por SSH está simulado: los comandos se copian y se pegan a mano.
- Los roles de usuario son informativos; no hay inicio de sesión real.
- La importación de topologías y la marca Fortinet en la interfaz web están pendientes (Fortinet sí se genera en el backend).
