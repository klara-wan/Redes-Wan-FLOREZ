# docs/pruebas.md — Reporte de pruebas

Ejecutadas con `cd backend && pytest -v` (resultado real, se repite en la sustentación).

## Qué probé
- [P01] subnetting sede a -> OK
- [P02] total direcciones 1440 -> OK
- [P03] rechaza cidr invalido -> OK
- [P04] rechaza direccion que no es red -> OK
- [P05] rechaza ipv6 como base -> OK
- [P06] bloque insuficiente -> OK
- [P07] ipv6 64 por vlan -> OK
- [P08] rechaza prefijo ipv6 malicioso -> OK
- [P09] clasifica pequena -> OK
- [P10] clasifica empresarial -> OK
- [P11] redundancia mejora puntaje -> OK
- [P12] puntaje nunca 100 con secretos de ejemplo -> OK
- [P13] config por marca incluye vlan ip y host[cisco] -> OK
- [P13] config por marca incluye vlan ip y host[huawei] -> OK
- [P13] config por marca incluye vlan ip y host[fortinet] -> OK
- [P13] config por marca incluye vlan ip y host[mikrotik] -> OK
- [P13] config por marca incluye vlan ip y host[juniper] -> OK
- [P13] config por marca incluye vlan ip y host[aruba] -> OK
- [P14] config cisco exacta -> OK
- [P15] sin secretos reales en configs -> OK
- [P16] no habilita telnet ni http cisco -> OK
- [P17] excel tiene hojas vlsm -> OK
- [P18] docx valido -> OK

## Resultado
Pruebas superadas: 23 de 23 = 100% de confianza

## Qué falta / errores encontrados
- La carga (importar) de topología aún no existe, por eso no tiene pruebas.
- No hay pruebas de la interfaz web (index.html) ni del envío real por SSH (está simulado).
- Las configuraciones se verifican por contenido, no se han probado en equipos reales; el 100% mide solo lo que está cubierto.
