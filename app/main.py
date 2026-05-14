from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.fornecimentos import empresa_router, router as fornecimentos_router
from app.core.config import get_settings
from app.db.session import check_database


settings = get_settings()

app = FastAPI(
    title="Portal B2B - Fornecimentos Service",
    description="Microsservico responsavel por ofertas de produtos feitas por empresas com perfil FORNECEDOR.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fornecimentos_router)
app.include_router(empresa_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/db", tags=["Health"])
def health_db() -> dict[str, str]:
    check_database()
    return {"status": "ok", "database": "connected"}
