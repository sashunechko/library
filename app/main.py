from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.routers import authors, books, copies, loans, readers

app = FastAPI(title="Library Management", version="0.1.0")

app.include_router(authors.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(copies.router, prefix="/api/v1")
app.include_router(readers.router, prefix="/api/v1")
app.include_router(loans.router, prefix="/api/v1")


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Conflict: duplicate value"})


@app.get("/health")
async def health():
    return {"status": "ok"}
