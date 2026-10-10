"""Generador de configuración por equipo. Tabla de plantillas por fabricante (data-driven):
agregar una marca = agregar una entrada en SYNTAX. Los marcadores CAMBIAR_* deben reemplazarse."""
from ipaddress import IPv4Network

from .schemas import Project

IFACE = {"cisco": "GigabitEthernet1/0/", "mikrotik": "ether", "huawei": "GigabitEthernet0/0/",
         "juniper": "ge-0/0/", "aruba": "1/1/", "fortinet": "port"}
COMMENT = {"cisco": "!", "aruba": "!"}  # el resto usa '#'

# Claves: host, harden (base de seguridad), vlan, svi, access, trunk, static (ruta por defecto),
# ospf (cabecera) + ospf_net (por red), bgp. Placeholders entre llaves.
SYNTAX = {
 "cisco": {
  "host": "hostname {n}\nip routing\nipv6 unicast-routing",
  "harden": "ip domain-name netplan.local\ncrypto key generate rsa modulus 2048\nip ssh version 2\nno ip http server\nip http secure-server\naaa new-model\naaa authentication login default local\nusername netadmin privilege 15 secret CAMBIAR_CLAVE\nservice password-encryption\nip access-list standard MGMT\n permit 10.0.0.0 0.0.0.255\nline vty 0 15\n transport input ssh\n login local\n exec-timeout 10 0\n access-class MGMT in\nspanning-tree mode rapid-pvst\nspanning-tree portfast bpduguard default\nip dhcp snooping\nntp server 0.pool.ntp.org\nlogging host 10.0.0.50\nsnmp-server group NETPLAN v3 priv\nsnmp-server user monitor NETPLAN v3 auth sha CAMBIAR_AUTH priv aes 128 CAMBIAR_PRIV",
  "vlan": "vlan {id}\n name {name}",
  "svi": "interface Vlan{id}\n description {name}\n ip address {gw4} {mask}\n ipv6 address {gw6}/64\n no shutdown",
  "access": "interface {port}\n switchport mode access\n switchport access vlan {id}\n switchport port-security maximum 3\n spanning-tree bpduguard enable",
  "trunk": "interface {port}\n switchport mode trunk\n switchport trunk allowed vlan {ids}",
  "static": "ip route 0.0.0.0 0.0.0.0 {isp_ip}",
  "ospf": "router ospf 1\n router-id {rid}\n default-information originate", "ospf_net": " network {net} {wild} area 0",
  "bgp": "router bgp {asn}\n neighbor {isp_ip} remote-as {isp_as}\n neighbor {isp_ip} password CAMBIAR_BGP\n address-family ipv4\n  network {bnet} mask {bmask}"},
 "mikrotik": {
  "host": "/system identity set name={n}",
  "harden": "/interface bridge add name=bridge1 vlan-filtering=yes protocol-mode=rstp\n/ip ssh set strong-crypto=yes\n/ip service disable telnet,ftp,www,api\n/user add name=netadmin group=full password=CAMBIAR_CLAVE\n/system ntp client set enabled=yes servers=0.pool.ntp.org\n/system logging action add name=remoto target=remote remote=10.0.0.50\n/system logging add topics=info action=remoto\n/snmp set enabled=yes\n/ip firewall filter add chain=input connection-state=established,related action=accept\n/ip firewall filter add chain=input protocol=tcp dst-port=22 src-address=10.0.0.0/24 action=accept\n/ip firewall filter add chain=input action=drop",
  "vlan": "/interface vlan add name=vlan{id} vlan-id={id} interface=bridge1 comment={name}",
  "svi": "/ip address add address={gw4}/{pfx} interface=vlan{id}\n/ipv6 address add address={gw6}/64 interface=vlan{id}",
  "access": "/interface bridge port add bridge=bridge1 interface={port} pvid={id} bpdu-guard=yes edge=yes",
  "trunk": "/interface bridge port add bridge=bridge1 interface={port}\n/interface bridge vlan add bridge=bridge1 tagged={port},bridge1 vlan-ids={ids}",
  "static": "/ip route add dst-address=0.0.0.0/0 gateway={isp_ip}",
  "ospf": "/routing ospf instance add name=o1 router-id={rid}\n/routing ospf area add name=a0 area-id=0.0.0.0 instance=o1", "ospf_net": "/routing ospf interface-template add area=a0 networks={net}/{pfx}",
  "bgp": "/routing bgp connection add name=isp remote.address={isp_ip} remote.as={isp_as} local.role=ebgp as={asn}"},
 "huawei": {
  "host": "sysname {n}",
  "harden": "rsa local-key-pair create\nstelnet server enable\nundo telnet server enable\nundo http server enable\nuser-interface vty 0 4\n authentication-mode aaa\n protocol inbound ssh\naaa\n local-user netadmin password irreversible-cipher CAMBIAR_CLAVE\n local-user netadmin privilege level 15\n local-user netadmin service-type ssh\nstp mode rstp\nstp bpdu-protection\ndhcp enable\ndhcp snooping enable\nntp-service unicast-server 0.pool.ntp.org\ninfo-center loghost 10.0.0.50\nsnmp-agent sys-info version v3\nacl 2000\n rule 5 permit source 10.0.0.0 0.0.0.255\n rule 10 deny",
  "vlan": "vlan {id}\n description {name}",
  "svi": "interface Vlanif{id}\n ip address {gw4} {mask}\n ipv6 enable\n ipv6 address {gw6}/64",
  "access": "interface {port}\n port link-type access\n port default vlan {id}\n stp edged-port enable",
  "trunk": "interface {port}\n port link-type trunk\n port trunk allow-pass vlan {ids_sp}",
  "static": "ip route-static 0.0.0.0 0.0.0.0 {isp_ip}",
  "ospf": "ospf 1 router-id {rid}\n area 0.0.0.0", "ospf_net": "  network {net} {wild}",
  "bgp": "bgp {asn}\n peer {isp_ip} as-number {isp_as}\n ipv4-family unicast\n  network {bnet} {bmask}\n  peer {isp_ip} enable"},
 "juniper": {
  "host": "set system host-name {n}",
  "harden": "set system services ssh protocol-version v2\nset system services ssh root-login deny\ndelete system services telnet\nset system login user netadmin class super-user authentication plain-text-password\nset system ntp server 0.pool.ntp.org\nset system syslog host 10.0.0.50 any notice\nset protocols rstp\nset snmp v3 usm local-engine user monitor authentication-sha authentication-password CAMBIAR_AUTH\nset firewall family inet filter MGMT term ssh from source-address 10.0.0.0/24\nset firewall family inet filter MGMT term ssh then accept\nset firewall family inet filter MGMT term deny then discard",
  "vlan": "set vlans {name} vlan-id {id}",
  "svi": "set interfaces irb unit {id} family inet address {gw4}/{pfx}\nset interfaces irb unit {id} family inet6 address {gw6}/64\nset vlans {name} l3-interface irb.{id}",
  "access": "set interfaces {port} unit 0 family ethernet-switching vlan members {name}\nset protocols rstp interface {port} edge\nset protocols rstp bpdu-block-on-edge",
  "trunk": "set interfaces {port} unit 0 family ethernet-switching interface-mode trunk\nset interfaces {port} unit 0 family ethernet-switching vlan members [ {names} ]",
  "static": "set routing-options static route 0.0.0.0/0 next-hop {isp_ip}",
  "ospf": "set routing-options router-id {rid}", "ospf_net": "set protocols ospf area 0.0.0.0 interface irb.{id}",
  "bgp": "set routing-options autonomous-system {asn}\nset protocols bgp group ISP type external\nset protocols bgp group ISP peer-as {isp_as}\nset protocols bgp group ISP neighbor {isp_ip}"},
 "aruba": {
  "host": "hostname {n}",
  "harden": "ssh server vrf default\nno telnet server vrf default\nuser netadmin group administrators password plaintext CAMBIAR_CLAVE\nspanning-tree\nspanning-tree mode rpvst\ndhcpv4-snooping\nntp server 0.pool.ntp.org\nlogging 10.0.0.50\nsnmpv3 user monitor auth sha auth-pass plaintext CAMBIAR_AUTH priv aes priv-pass plaintext CAMBIAR_PRIV\nhttps-server vrf default",
  "vlan": "vlan {id}\n name {name}",
  "svi": "interface vlan {id}\n ip address {gw4}/{pfx}\n ipv6 address {gw6}/64",
  "access": "interface {port}\n no routing\n vlan access {id}\n spanning-tree bpdu-guard",
  "trunk": "interface {port}\n no routing\n vlan trunk allowed {ids}",
  "static": "ip route 0.0.0.0/0 {isp_ip}",
  "ospf": "router ospf 1\n router-id {rid}\n area 0.0.0.0", "ospf_net": "interface vlan {id}\n ip ospf 1 area 0.0.0.0",
  "bgp": "router bgp {asn}\n neighbor {isp_ip} remote-as {isp_as}\n address-family ipv4 unicast\n  network {bnet}/{bpfx}\n  neighbor {isp_ip} activate"},
 "fortinet": {
  "host": "config system global\n set hostname {n}\nend",
  "harden": "config system global\n set admintimeout 10\n set strong-crypto enable\nend\nconfig system admin\n edit \"netadmin\"\n  set accprofile \"super_admin\"\n  set password CAMBIAR_CLAVE\n next\nend\nconfig system ntp\n set ntpsync enable\nend\nconfig log syslogd setting\n set status enable\n set server 10.0.0.50\nend\nconfig system snmp user\n edit \"monitor\"\n  set security-level auth-priv\n  set auth-proto sha\n  set auth-pwd CAMBIAR_AUTH\n  set priv-proto aes\n  set priv-pwd CAMBIAR_PRIV\n next\nend\nconfig system interface\n edit \"port1\"\n  set allowaccess ping ssh https\n next\nend",
  "vlan": "config system interface\n edit \"vlan{id}\"\n  set vdom \"root\"\n  set interface \"{parent}\"\n  set vlanid {id}\n  set alias \"{name}\"\n  set ip {gw4} {mask}\n  set allowaccess ping\n  config ipv6\n   set ip6-address {gw6}/64\n  end\n next\nend",
  "svi": "# FortiOS: la IP y el IPv6 ya quedaron definidos en la interfaz VLAN {id}",
  "access": "# FortiGate es firewall: los puertos de acceso se gestionan con FortiSwitch (switch-controller)",
  "trunk": "config system interface\n edit \"{port}\"\n  set allowaccess ping\n next\nend",
  "static": "config router static\n edit 1\n  set gateway {isp_ip}\n  set device \"port1\"\n next\nend",
  "ospf": "config router ospf\n set router-id {rid}\n config area\n  edit 0.0.0.0\n  next\n end\nend", "ospf_net": "config router ospf\n config network\n  edit {id}\n   set prefix {net} {mask}\n  next\n end\nend",
  "bgp": "config router bgp\n set as {asn}\n config neighbor\n  edit {isp_ip}\n   set remote-as {isp_as}\n  next\n end\n config network\n  edit 1\n   set prefix {bnet} {bmask}\n  next\n end\nend"},
}


def _fmt(tpl: str, **kw) -> str:
    return tpl.format(**kw)


def build_devices(p: Project, rows: list[dict], cls: dict) -> dict[str, str]:
    """Devuelve {nombre_equipo: configuración}. Pequeña: core+distribución colapsados. Empresarial: core, distribución(es) y acceso."""
    s, pre, cm = SYNTAX[p.vendor], IFACE[p.vendor], COMMENT.get(p.vendor, "#")
    base = IPv4Network(p.base_cidr)
    ent = cls["type"] == "empresarial"
    ids = [r["vlan"] for r in rows]
    common = dict(isp_ip=p.isp_ip, isp_as=p.isp_as, asn=p.local_as, bnet=str(base.network_address),
                  bmask=str(base.netmask), bpfx=base.prefixlen, ids=",".join(map(str, ids)),
                  ids_sp=" ".join(map(str, ids)), parent=f"{pre}2", names=" ".join(r["name"].replace(" ", "_").upper() for r in rows))

    def vr(r):  # variables de una VLAN
        net = IPv4Network(f"{r['network']}/{r['prefix']}")
        return dict(common, id=r["vlan"], name=r["name"].replace(" ", "_").upper(), gw4=r["gateway"], mask=r["mask"],
                    pfx=r["prefix"], gw6=r["v6_gw"], net=r["network"], wild=str(net.hostmask))

    def head(name, role):
        return [f"{cm} NetPlan | {p.name} | {role} | {p.vendor} {p.version}".strip(),
                f"{cm} Reemplazar todos los CAMBIAR_* antes de aplicar", _fmt(s["host"], n=name), s["harden"]]

    def l3_block(rid):  # VLAN + SVI + enrutamiento
        out = [_fmt(s["vlan"], **vr(r)) for r in rows] + [_fmt(s["svi"], **vr(r)) for r in rows]
        if ent:  # empresarial: OSPF interno + BGP al ISP
            out.append(_fmt(s["ospf"], rid=rid, **common))
            out += [_fmt(s["ospf_net"], **vr(r)) for r in rows]
            out.append(_fmt(s["bgp"], **common))
        else:    # pequeña: ruta por defecto al ISP (NAT en el router de borde)
            out.append(_fmt(s["static"], **common))
        return out

    devices: dict[str, str] = {}
    cores = ["CORE-DIST"] if not ent else ["CORE"] + (["CORE-2"] if p.redundancy else [])
    for i, n in enumerate(cores):
        body = head(n, "core" if ent else "core+distribución") + l3_block(f"10.255.255.{i + 1}")
        body += [_fmt(s["trunk"], port=f"{pre}{k + 1}", **common) for k in range(len(rows))] if not ent else []
        devices[n] = "\n".join(body)
    if ent:
        dists = ["DIST-1"] + (["DIST-2"] if p.redundancy else [])
        for i, n in enumerate(dists):
            body = head(n, "distribución") + l3_block(f"10.255.254.{i + 1}")
            body += [_fmt(s["trunk"], port=f"{pre}{k + 1}", **common) for k in range(len(rows))]
            devices[n] = "\n".join(body)
    for k, r in enumerate(rows):
        v = vr(r)
        n = f"ACC-{r['name'].replace(' ', '-').upper()}"
        body = head(n, "acceso") + [_fmt(s["vlan"], **v), f"{cm} Replicar el bloque 'access' en los puertos 1-24",
                                    _fmt(s["access"], port=f"{pre}1", **v), _fmt(s["trunk"], port=f"{pre}48", **common)]
        devices[n] = "\n".join(body)
    return devices
