"""Auditoría de configuraciones: advierte ajustes inseguros (política de ciberdefensa).
Multimarca por patrones de texto. NUNCA devuelve secretos: los enmascara antes de responder."""
import re

_OFF = r"(?!\s*(no|undo|delete)\b)"   # ignora líneas que desactivan la función ("no ...", "undo ...")
# (id, severidad, mensaje, patrón evaluado línea por línea)
RULES = [
    ("TELNET", "alto", "Telnet habilitado: el tráfico y las claves viajan sin cifrar; use SSH.",
     rf"(?i)^{_OFF}.*(transport input (telnet|all)|\btelnet server enable|/ip service enable .*telnet|allowaccess.*\btelnet)"),
    ("HTTP", "alto", "Administración por HTTP sin cifrar; use HTTPS.",
     rf"(?i)^{_OFF}\s*(ip http server|http server enable)\b"),
    ("FTP", "medio", "FTP habilitado: protocolo sin cifrar.",
     rf"(?i)^{_OFF}.*(\bftp server enable|/ip service enable .*ftp)"),
    ("SNMP_V2", "alto", "SNMP v1/v2c con comunidad: use SNMPv3 con autenticación y cifrado.",
     r"(?i)^\s*(snmp-server community|snmp-agent community|set snmp community)\b|/snmp community add .*name=(public|private)\b"),
    ("SSH_V1", "alto", "SSH versión 1 es inseguro; use SSHv2.", r"(?i)\bip ssh version 1\b"),
    ("ACL_ANY", "medio", "ACL que permite todo el tráfico (permit any any).", r"(?i)\bpermit (ip )?any any\b"),
]
# Secretos incrustados: palabra clave + (tipo opcional) + valor. Los marcadores CAMBIAR_* son válidos.
SECRET_RE = re.compile(r"(?i)\b(password|secret|passwd|auth-pwd|priv-pwd|authentication-password|privacy-password)\b[= ]\s*"
                       r"(?:(?:plaintext|irreversible-cipher|cipher|[0-9])\s+)?(\S+)")


def _mask(line: str) -> str:
    m = SECRET_RE.search(line)
    return line if not m else line[: m.start(2)] + "********" + line[m.end(2):]


def audit(text: str) -> dict:
    """Devuelve hallazgos (línea, severidad, regla, mensaje, texto enmascarado) y conteo por severidad."""
    findings = []
    lines = text.splitlines()
    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        for rid, sev, msg, pat in RULES:
            if re.search(pat, line):
                findings.append({"line": n, "severity": sev, "rule": rid, "message": msg, "text": _mask(line)[:100]})
        m = SECRET_RE.search(line)
        if m and not m.group(2).startswith("CAMBIAR_"):
            findings.append({"line": n, "severity": "alto", "rule": "SECRETO",
                             "message": "Contraseña o secreto incrustado en la configuración; use un vault y marcadores.",
                             "text": _mask(line)[:100]})
    if len(lines) > 5 and not re.search(r"(?i)\bssh\b|stelnet", text):
        findings.append({"line": 0, "severity": "medio", "rule": "SIN_SSH", "message": "No se encuentra SSH habilitado.", "text": ""})
    counts = {"alto": 0, "medio": 0}
    for f in findings:
        counts[f["severity"]] += 1
    return {"findings": findings, "counts": counts}
