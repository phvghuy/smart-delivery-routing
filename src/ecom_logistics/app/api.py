from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ecom_logistics.shared.exceptions import DomainValidationError, NotFoundError, ConflictError, BusinessRuleViolation
from ecom_logistics.auth.presentation.router import router as auth_router
from ecom_logistics.linehaul.hub.presentation.router import router as hub_router

app = FastAPI(title="Ecom Logistics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sdr-admin.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainValidationError)
async def domain_validation_handler(request, exc: DomainValidationError):
    return JSONResponse(status_code=422, content={"errors": [
        {"field": e.field, "message": e.message} for e in exc.errors
    ]})


@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(BusinessRuleViolation)
async def business_rule_handler(request, exc: BusinessRuleViolation):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(auth_router)
app.include_router(hub_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
