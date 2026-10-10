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
- [P19] topologia valida -> OK
- [P20] rechaza nombre repetido -> OK
- [P21] rechaza enlace a equipo inexistente -> OK
- [P22] rechaza enlace consigo mismo -> OK
- [P23] rechaza nombre con script o comandos -> OK
- [P24] rechaza ip invalida y rol desconocido -> OK
- [P25] advierte equipo aislado -> OK
- [P26] advierte un solo core y falta isp -> OK

## Resultado
Pruebas superadas: 31 de 31 = 100% de confianza

## Qué falta / errores encontrados
- No hay pruebas automáticas de la interfaz web (index.html): la carga de topología del navegador se probó a mano.
- El envío real por SSH está simulado y no se prueba.
- Las configuraciones se verifican por contenido, no se han probado en equipos reales; el porcentaje mide solo lo que está cubierto.
