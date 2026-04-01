from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .search_route import router as search_router
from .explain_route import router as explain_router
from .test_ingest_route import router as test_ingest_router
from .upload_route import router as upload_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "backend running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(search_router)
app.include_router(explain_router)
app.include_router(test_ingest_router)
app.include_router(upload_router)
