"""Pruebas de carga de topología. Ejecutar desde /backend:  pytest -v"""
import pytest
from pydantic import ValidationError

from app.topology import Topology, analyze_topology

D = [{"name": "ISP-1", "role": "isp"}, {"name": "CORE-1", "role": "core", "ip": "10.0.0.1"}, {"name": "ACC-1", "role": "access"}]
L = [{"a": "ISP-1", "b": "CORE-1", "type": "wan"}, {"a": "CORE-1", "b": "ACC-1", "type": "trunk"}]


def topo(devices=D, links=L):
    return Topology(devices=devices, links=links)


def test_p19_topologia_valida():
    t = topo()
    assert len(t.devices) == 3 and len(t.links) == 2

def test_p20_rechaza_nombre_repetido():
    with pytest.raises(ValidationError): topo(devices=D + [{"name": "ACC-1", "role": "access"}])

def test_p21_rechaza_enlace_a_equipo_inexistente():
    with pytest.raises(ValidationError): topo(links=[{"a": "CORE-1", "b": "NO-EXISTE"}])

def test_p22_rechaza_enlace_consigo_mismo():
    with pytest.raises(ValidationError): topo(links=[{"a": "CORE-1", "b": "CORE-1"}])

def test_p23_rechaza_nombre_con_script_o_comandos():
    with pytest.raises(ValidationError): topo(devices=[{"name": "<script>x</script>", "role": "core"}])
    with pytest.raises(ValidationError): topo(devices=[{"name": "SW1; reload", "role": "core"}])

def test_p24_rechaza_ip_invalida_y_rol_desconocido():
    with pytest.raises(ValidationError): topo(devices=[{"name": "A", "role": "core", "ip": "999.1.1.1"}])
    with pytest.raises(ValidationError): topo(devices=[{"name": "A", "role": "hacker"}])

def test_p25_advierte_equipo_aislado():
    assert any("aislado" in w for w in analyze_topology(topo(devices=D + [{"name": "SOLO", "role": "access"}])))

def test_p26_advierte_un_solo_core_y_falta_isp():
    w = analyze_topology(topo(devices=[{"name": "C", "role": "core"}, {"name": "A", "role": "access"}], links=[{"a": "C", "b": "A"}]))
    assert any("punto único" in x for x in w) and any("ISP" in x for x in w)
