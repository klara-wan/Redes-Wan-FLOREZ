"""Pruebas de la auditoría de seguridad. Ejecutar desde /backend:  pytest -v"""
import pytest

from app import configs, engine
from app.schemas import Project
from app.security_audit import audit

def rules(text): return {f["rule"] for f in audit(text)["findings"]}

def test_p27_detecta_telnet():
    assert "TELNET" in rules("line vty 0 4\n transport input telnet")

def test_p28_no_marca_telnet_desactivado():
    assert "TELNET" not in rules("undo telnet server enable\nstelnet server enable")

def test_p29_detecta_http_y_no_marca_no_http():
    assert "HTTP" in rules("ip http server") and "HTTP" not in rules("no ip http server\nip http secure-server")

def test_p30_detecta_snmp_v2c():
    assert "SNMP_V2" in rules("snmp-server community public RO")

def test_p31_detecta_secreto_y_lo_enmascara():
    r = audit("username admin password Cisco123")
    assert r["findings"][0]["rule"] == "SECRETO" and "Cisco123" not in r["findings"][0]["text"]

def test_p32_acepta_marcadores_cambiar():
    assert "SECRETO" not in rules("enable secret CAMBIAR_CLAVE\n/user add name=a password=CAMBIAR_CLAVE")

def test_p33_detecta_acl_abierta_y_ssh_v1():
    assert {"ACL_ANY", "SSH_V1"} <= rules("permit ip any any\nip ssh version 1")

def test_p34_advierte_si_no_hay_ssh():
    assert "SIN_SSH" in rules("a\nb\nc\nd\ne\nf")

@pytest.mark.parametrize("vendor", ["cisco", "huawei", "fortinet", "mikrotik", "juniper", "aruba"])
def test_p35_configs_generadas_no_tienen_hallazgos_altos(vendor):
    p = Project(name="S", base_cidr="172.16.0.0/21", vendor=vendor,
                floors=[{"name": "Piso 1", "users": 200}, {"name": "Piso 2", "users": 50}])
    rows = engine.plan_vlsm(p)
    for name, cfg in configs.build_devices(p, rows, engine.classify(p, rows)).items():
        assert audit(cfg)["counts"]["alto"] == 0, (vendor, name)
