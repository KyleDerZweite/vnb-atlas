from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import areas, coverage, federal_states, health, lookup, operators, search


def create_app() -> FastAPI:
    app = FastAPI(
        title="Deutschland VNB Atlas API",
        description=(
            "API fuer ein lokales MVP mit Mock-Daten. "
            "Die Anwendung ist deutschlandweit ausgelegt; im MVP sind nur NRW-Pilotdaten befuellt. "
            "Die gelieferten Flaechen sind nicht amtlich und zeigen keine echten VNB-Zustaendigkeiten."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(coverage.router)
    app.include_router(federal_states.router)
    app.include_router(operators.router)
    app.include_router(areas.router)
    app.include_router(search.router)
    app.include_router(lookup.router)
    return app


app = create_app()
