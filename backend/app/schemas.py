"""Esquemas de entrada (validación estricta con Pydantic: nunca confiar en la entrada del cliente)."""
import re
from ipaddress import ip_network, ip_address
from typing import Literal
from pydantic import BaseModel, Field, field_validator

Vendor = Literal["cisco", "mikrotik", "huawei", "juniper", "aruba", "fortinet"]


class Floor(BaseModel):
    """Un piso/área con la cantidad de usuarios que debe soportar."""
    name: str = Field(min_length=1, max_length=40)
    users: int = Field(ge=1, le=100_000)


class Project(BaseModel):
    """Proyecto completo. Se reenvía entero en cada llamada (API stateless)."""
    name: str = Field(min_length=1, max_length=80)
    base_cidr: str                                  # bloque IPv4 asignado a la sede
    v6_prefix: str = "2001:db8:1"                   # /48 de la sede (documentación RFC 3849 por defecto)
    floors: list[Floor] = Field(min_length=1, max_length=200)
    vendor: Vendor = "cisco"
    version: str = ""
    redundancy: bool = False                        # ¿hay segundo equipo core/distribución?
    dual_isp: bool = False                          # ¿hay dos enlaces a ISP distintos?
    growth_pct: int = Field(0, ge=0, le=500)        # crecimiento de usuarios esperado
    isp_ip: str = "203.0.113.1"                     # vecino BGP / gateway del ISP (ejemplo RFC 5737)
    isp_as: int = Field(64500, ge=1, le=4_294_967_295)
    local_as: int = Field(65001, ge=1, le=4_294_967_295)

    @field_validator("base_cidr")
    @classmethod
    def _valid_cidr(cls, v: str) -> str:
        net = ip_network(v, strict=True)            # ValueError => HTTP 422 automático
        if net.version != 4:
            raise ValueError("base_cidr debe ser IPv4")
        return str(net)

    @field_validator("v6_prefix")
    @classmethod
    def _valid_v6(cls, v: str) -> str:
        v = v.rstrip(":")
        if not re.fullmatch(r"[0-9a-fA-F:]{1,30}", v):
            raise ValueError("v6_prefix inválido (ej. 2001:db8:1)")
        return v

    @field_validator("isp_ip")
    @classmethod
    def _valid_isp(cls, v: str) -> str:
        return str(ip_address(v))
