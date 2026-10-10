"""Carga y validación de topologías (dispositivos y enlaces).
Toda entrada externa se trata como NO confiable: se valida formato, nombres, roles, IPs y enlaces."""
import re
from ipaddress import IPv4Address
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Role = Literal["isp", "firewall", "router", "core", "distribution", "access", "server"]
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,29}$")       # sin espacios ni símbolos de comandos/HTML
VENDORS = {"", "cisco", "huawei", "fortinet", "mikrotik", "juniper", "aruba"}


class Device(BaseModel):
    name: str
    role: Role
    vendor: str = ""
    ip: str = ""

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        if not NAME_RE.fullmatch(v):
            raise ValueError("nombre inválido: use letras, números, '-' y '_' (máx. 30)")
        return v

    @field_validator("vendor")
    @classmethod
    def _vendor(cls, v: str) -> str:
        if v.lower() not in VENDORS:
            raise ValueError("marca no soportada")
        return v.lower()

    @field_validator("ip")
    @classmethod
    def _ip(cls, v: str) -> str:
        return str(IPv4Address(v)) if v else v                    # ValueError => 422


class Link(BaseModel):
    a: str
    b: str
    type: Literal["wan", "lan", "trunk"] = "lan"


class Topology(BaseModel):
    devices: list[Device] = Field(min_length=1, max_length=200)
    links: list[Link] = Field(default_factory=list, max_length=1000)

    @model_validator(mode="after")
    def _consistency(self):
        names = [d.name for d in self.devices]
        if len(set(names)) != len(names):
            raise ValueError("hay nombres de dispositivo repetidos")
        seen = set()
        for l in self.links:
            if l.a not in names or l.b not in names:
                raise ValueError(f"enlace con dispositivo inexistente: {l.a} - {l.b}")
            if l.a == l.b:
                raise ValueError(f"enlace de un dispositivo consigo mismo: {l.a}")
            key = frozenset((l.a, l.b))
            if key in seen:
                raise ValueError(f"enlace repetido: {l.a} - {l.b}")
            seen.add(key)
        return self


def analyze_topology(t: Topology) -> list[str]:
    """Advertencias de diseño (no bloquean la carga): aislados, un solo core, sin ISP."""
    degree = {d.name: 0 for d in t.devices}
    for l in t.links:
        degree[l.a] += 1
        degree[l.b] += 1
    w = [f"{n} no tiene enlaces (equipo aislado)." for n, g in degree.items() if g == 0 and len(t.devices) > 1]
    cores = [d for d in t.devices if d.role == "core"]
    if not cores:
        w.append("No hay equipo core.")
    elif len(cores) == 1 and any(d.role == "access" for d in t.devices):
        w.append("Un solo core: punto único de falla.")
    if not any(d.role == "isp" for d in t.devices):
        w.append("No hay ISP/WAN definido.")
    return w
