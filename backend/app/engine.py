"""Motor de planeación: VLSM IPv4, /64 IPv6 por VLAN y clasificación del proyecto."""
import math
from ipaddress import IPv4Network

from .schemas import Project


def block_size(hosts: int) -> int:
    """Menor potencia de 2 que cubre hosts + red + broadcast (mínimo /30)."""
    size = 4
    while size < hosts + 2:
        size *= 2
    return size


def plan_vlsm(p: Project) -> list[dict]:
    """VLSM clásico: pisos de mayor a menor, bloques sucesivos alineados dentro del bloque base."""
    base = IPv4Network(p.base_cidr)
    pointer, end = int(base.network_address), int(base.broadcast_address) + 1
    rows = []
    for i, f in enumerate(sorted(p.floors, key=lambda x: x.users, reverse=True)):
        required = math.ceil(f.users * (1 + p.growth_pct / 100))   # incluye margen de crecimiento
        size = block_size(required)
        pointer += (-pointer) % size                               # alinear al tamaño del bloque
        if pointer + size > end:
            raise ValueError(f"El bloque {p.base_cidr} no alcanza para '{f.name}' (con {p.growth_pct}% de crecimiento)")
        net = IPv4Network((pointer, 32 - int(math.log2(size))))
        hosts = list(net.hosts())
        rows.append({
            "name": f.name, "users": f.users, "required": required, "vlan": 10 * (i + 1),
            "network": str(net.network_address), "prefix": net.prefixlen, "mask": str(net.netmask),
            "gateway": str(hosts[0]), "first": str(hosts[0]), "last": str(hosts[-1]),
            "broadcast": str(net.broadcast_address), "usable": len(hosts),
            "v6": f"{p.v6_prefix}:{i + 1:x}::/64", "v6_gw": f"{p.v6_prefix}:{i + 1:x}::1",
        })
        pointer += size
    return rows


def classify(p: Project, rows: list[dict]) -> dict:
    """Decide si el cliente necesita red empresarial o pequeña y explica por qué."""
    total = sum(f.users for f in p.floors)
    reasons = []
    if total >= 200: reasons.append(f"{total} usuarios (umbral empresarial: 200)")
    if len(p.floors) >= 4: reasons.append(f"{len(p.floors)} pisos/áreas (umbral: 4)")
    if p.redundancy or p.dual_isp: reasons.append("exige alta disponibilidad")
    enterprise = bool(reasons)
    return {
        "type": "empresarial" if enterprise else "pequeña",
        "total_users": total, "floors": len(p.floors),
        "reasons": reasons or [f"{total} usuarios y {len(p.floors)} áreas: caben en un diseño colapsado"],
        # Pila de protocolos recomendada según el tipo
        "routing": ["OSPFv2/v3 (área 0)", "BGP externo al ISP", "HSRP/VRRP", "ACL", "STP rápido"] if enterprise
                   else ["Ruta estática por defecto", "NAT en el borde", "ACL", "STP rápido"],
    }
