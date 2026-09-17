from fastapi import FastAPI

from neso_api.routes.model_runs import router

app = FastAPI(title="NESO Strategy & Policy API", version="0.2.0")
app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health."""
    return {"status": "ok"}
