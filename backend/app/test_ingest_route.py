from fastapi import APIRouter
from .ingest import extract_functions

router = APIRouter()

@router.get("/test-ingest")
def test_ingest():
    chunks = extract_functions("backend")  # ✅ only scan backend
    return {"chunks_found": len(chunks), "sample": chunks[:3]}