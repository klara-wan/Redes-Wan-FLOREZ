# NetPlan backend (FastAPI)
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000   # docs: http://localhost:8000/docs
Variable opcional: NETPLAN_CORS="https://tu-dominio" (por defecto "*", solo desarrollo).
El backend es stateless: el frontend envía el proyecto completo en cada llamada, así el cliente puede
cambiar la infraestructura en cualquier momento y volver a analizar.
