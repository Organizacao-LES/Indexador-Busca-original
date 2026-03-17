# indexadordebusca/backend/app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="IFESDOC - Sistema de Indexação e Busca",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "IFESDOC API running"}