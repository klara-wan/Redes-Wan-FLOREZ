"""API de NetPlan. Stateless: cada petición trae el proyecto completo (el cliente puede cambiarlo cuando quiera)."""
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from . import advisor, configs, engine, exports
from .schemas import Project
from .topology import Topology, analyze_topology

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("netplan")

app = FastAPI(title="NetPlan API", version="0.2")
# En producción fijar NETPLAN_CORS al dominio del frontend; "*" es solo para desarrollo.
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("NETPLAN_CORS", "*").split(","),
                   allow_methods=["POST", "GET"], allow_headers=["*"])


def _run(p: Project) -> dict:
    """Pipeline único: plan → clasificación → evaluación → configuración por equipo."""
    try:
        rows = engine.plan_vlsm(p)
    except ValueError as e:                      # bloque base insuficiente
        raise HTTPException(status_code=422, detail=str(e))
    cls = engine.classify(p, rows)
    ev = advisor.evaluate(p, rows, cls)
    log.info("proyecto=%s tipo=%s puntaje=%s", p.name, cls["type"], ev["score"])
    return {"plan": rows, "classification": cls, "evaluation": ev, "devices": configs.build_devices(p, rows, cls)}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/projects/analyze")
def analyze(p: Project) -> dict:
    """Devuelve plan VLSM, clasificación, puntaje crítico y comandos por equipo."""
    return _run(p)


@app.post("/api/projects/export/xlsx")
def export_xlsx(p: Project) -> Response:
    r = _run(p)
    data = exports.build_xlsx(p, r["plan"], r["classification"], r["evaluation"])
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="enrutamiento_vlsm.xlsx"'})


@app.post("/api/projects/export/docx")
def export_docx(p: Project) -> Response:
    r = _run(p)
    data = exports.build_docx(p, r["plan"], r["classification"], r["evaluation"])
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": 'attachment; filename="infraestructura_red.docx"'})


@app.post("/api/topology/validate")
def validate_topology(t: Topology) -> dict:
    """Valida una topología importada (formato, nombres, IPs, enlaces) y devuelve advertencias de diseño."""
    return {"devices": len(t.devices), "links": len(t.links), "warnings": analyze_topology(t)}
