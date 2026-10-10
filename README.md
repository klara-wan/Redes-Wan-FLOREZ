# NetPlan — Herramienta de diseño y gestión de redes WAN

**Autor:** Kevin Santiago Lara Florez· **Repositorio:** https://github.com/klara-wan/Redes-Wan-FLOREZ.git

Calcula subnetting VLSM (IPv4/IPv6), genera configuraciones por equipo para Cisco, Huawei, Fortinet y MikroTik (además de Juniper y Aruba), evalúa el diseño de forma crítica y exporta Excel y Word. Ciberdefensa integrada (ver docs/politicas-ia.md).

## Cómo ejecutarla
1. Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --port 8000`
2. Frontend: abrir `index.html` en el navegador; la pestaña "Proyecto" usa el backend.

## Pruebas y porcentaje de confianza (Corte 3)
- Pruebas superadas: 23 de 23 = 100% (ver docs/pruebas.md). Correr: `cd backend && pytest -v`

## Documentos
- docs/informe-corte2.pdf · docs/informe-corte3.pdf
- docs/manual.md · docs/seguridad.md · docs/politicas-ia.md · docs/pruebas.md

## Capturas (evidencias)
docs/capturas/ (01-subnetting.png ... 10-app-final.png)

## Autoevaluación
| Criterio | ¿Cumplido? | Evidencia |
|---|---|---|
| Subnetting funciona | Sí | 01-subnetting.png |
| Carga de topología | No (pendiente) | 02-topologia.png |
| Config Cisco y Huawei | Sí | 03 / 04 |
| Config Fortinet y MikroTik (C3) | Sí | 06 / 07 |
| Ciberdefensa (politicas-ia.md) | Parcial | 08-ciberdefensa.png |
| Pruebas con porcentaje de confianza (C3) | Sí | docs/pruebas.md |
