"""Asesor crítico: puntaje de éxito y hallazgos. Es determinista (reglas) para ser auditable.
Punto de extensión: `narrative()` puede enviarse a un LLM (p. ej. API de Claude) desde el servidor,
nunca desde el navegador, para no exponer credenciales."""
from .schemas import Project


def evaluate(p: Project, rows: list[dict], cls: dict) -> dict:
    """Parte de 100 y resta por cada debilidad. Es intencionalmente exigente."""
    ent = cls["type"] == "empresarial"
    f: list[dict] = []

    def add(sev: str, area: str, issue: str, fix: str, pen: int):
        f.append({"severity": sev, "area": area, "issue": issue, "fix": fix, "penalty": pen})

    if not p.redundancy:
        add("crítico" if ent else "medio", "Disponibilidad", "Core/distribución sin redundancia: punto único de falla.",
            "Segundo equipo con HSRP/VRRP y enlaces en port-channel (LACP).", 20 if ent else 8)
    if not p.dual_isp:
        add("crítico" if ent else "medio", "WAN", "Un solo ISP: una caída del proveedor deja sin servicio a todos.",
            "Segundo ISP con BGP (multihoming) o enlace de respaldo LTE.", 15 if ent else 5)
    if p.growth_pct < 20:
        add("alto", "Capacidad", f"Crecimiento previsto {p.growth_pct}%: sin margen para nuevos usuarios.",
            "Dimensionar con 20-30% de holgura; reasignar el direccionamiento cuesta mucho más después.", 10)
    tight = [r["name"] for r in rows if r["usable"] < r["users"] * 1.2]
    if tight:
        add("alto", "Direccionamiento", f"Subredes sin holgura del 20%: {', '.join(tight)}.",
            "Aumentar el crecimiento esperado o pedir un bloque base mayor.", 10)
    base_size = 2 ** (32 - int(p.base_cidr.split("/")[1]))
    used = sum(r["usable"] + 2 for r in rows)
    util = used / base_size * 100
    if util > 95: add("crítico", "Direccionamiento", f"Bloque base al {util:.0f}%: prácticamente agotado.", "Solicitar un bloque mayor.", 20)
    elif util > 80: add("alto", "Direccionamiento", f"Bloque base al {util:.0f}%: poco espacio libre.", "Reservar espacio para nuevas VLAN.", 10)
    big = [r["name"] for r in rows if r["prefix"] <= 23]
    if big:
        add("medio", "Diseño L2", f"Dominios de broadcast muy grandes (/23 o mayor): {', '.join(big)}.",
            "Segmentar en VLAN de 250 hosts o menos para contener broadcast.", 10)
    if ent:
        add("alto", "Seguridad", "Sin control de acceso por puerto (802.1X/NAC).", "RADIUS + 802.1X con VLAN dinámica.", 8)
        add("medio", "Operación", "Sin respaldo automático de configuraciones ni monitoreo activo.",
            "Respaldo diario a Git (Oxidized/RANCID) y monitoreo con SNMPv3 + Zabbix/Prometheus.", 4)
    add("medio", "Seguridad", "Secretos como marcadores CAMBIAR_* dentro de la configuración.",
        "Gestionar credenciales con un vault y rotarlas; nunca dejar claves por defecto.", 5)
    add("bajo", "Operación", "Sin red de gestión fuera de banda.", "VLAN/VRF de gestión dedicada y consola serial remota.", 5)
    score = max(0, 100 - sum(x["penalty"] for x in f))
    verdict = "Sólido" if score >= 85 else "Aceptable con mejoras" if score >= 65 else "Deficiente: no apto para producción"
    return {"score": score, "verdict": verdict, "findings": sorted(f, key=lambda x: -x["penalty"])}


def narrative(p: Project, cls: dict, ev: dict) -> list[str]:
    """Texto explicativo de la infraestructura para el documento Word."""
    return [
        f"El proyecto '{p.name}' se clasificó como red {cls['type']}: " + "; ".join(cls["reasons"]) + ".",
        f"Topología: ISP/WAN → core → distribución → un switch de acceso por piso ({cls['floors']} áreas). "
        f"Cada piso es una VLAN con su subred IPv4 (VLSM sobre {p.base_cidr}) y un /64 IPv6 (prefijo {p.v6_prefix}::/48).",
        "Protocolos de enrutamiento: " + ", ".join(cls["routing"]) + ".",
        "Seguridad aplicada en cada equipo: SSHv2 sin Telnet/HTTP, AAA local, SNMPv3, NTP, Syslog, STP con protección BPDU, "
        "DHCP Snooping y listas de acceso para el plano de gestión.",
        f"Evaluación crítica: {ev['score']}% ({ev['verdict']}). Se detectaron {len(ev['findings'])} aspectos a mejorar; "
        "los de mayor impacto se listan en la sección de mejoras.",
    ]
