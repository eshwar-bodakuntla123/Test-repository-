from fastapi import FastAPI

from neso_api.routes import model_runs

app = FastAPI(
    title="NESO Emissions API",
    version="0.1.0",
)

app.include_router(model_runs.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
