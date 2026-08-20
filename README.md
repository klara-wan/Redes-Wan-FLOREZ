# NetPlan — Prototipo de herramienta de planeación de infraestructura de red

Aplicación de una sola página (HTML/CSS/JS, sin dependencias de build) que demuestra
el flujo completo discutido: alta de clientes, motor de subnetting VLSM, asignación
de VLANs, topología generada automáticamente, revisor de configuración en modo
dry-run y auditoría.

## Cómo usarlo
Abrir `index.html` directamente en el navegador. No requiere servidor ni instalación.

## Estado y próximos pasos
Este prototipo mantiene todo el estado en memoria (se pierde al recargar) y simula
el push SSH — es la base de UI/lógica de negocio para conectar después con un
backend real (FastAPI + PostgreSQL + Netmiko/Celery), como se definió en el diseño
de arquitectura.

## Control de versiones
Este proyecto usa Git. Cada cambio relevante debe ir en su propio commit con un
mensaje descriptivo, por ejemplo:

    git add index.html
    git commit -m "feat: agrega validación de pool de direccionamiento agotado"

Para ver el historial: `git log --oneline`
