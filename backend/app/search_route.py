from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .config import settings
from .ingest import extract_functions
from .embed import embed_texts
from .vector_store import build_index, search_index
from .chat_store import save_chat_index, load_chat_index, list_saved_chats, delete_chat_index

router = APIRouter()

STORE = {"chunks": [], "index": None, "dim": None}

class IndexRequest(BaseModel):
    folder: str = settings.DEFAULT_FOLDER
    chat_id: str = ""

class SearchRequest(BaseModel):
    query: str
    k: int = settings.DEFAULT_K

@router.post("/index")
def index_code(req: IndexRequest):
    chunks = extract_functions(req.folder)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks found")

    texts = [c["code"] for c in chunks]
    vectors = embed_texts(texts)
    index, dim = build_index(vectors)

    STORE["chunks"] = chunks
    STORE["index"] = index
    STORE["dim"] = dim

    if req.chat_id:
        save_chat_index(req.chat_id, chunks, index, dim)

    return {"indexed": True, "chunks": len(chunks), "dim": dim}


@router.post("/chats/{chat_id}/activate")
def activate_chat(chat_id: str):
    chunks, index, dim = load_chat_index(chat_id)
    if index is None:
        raise HTTPException(status_code=404, detail="No saved index for this chat")
    STORE["chunks"] = chunks
    STORE["index"] = index
    STORE["dim"] = dim
    return {"activated": True, "chat_id": chat_id, "chunks": len(chunks)}


@router.get("/chats")
def get_chats():
    return {"chats": list_saved_chats()}


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    delete_chat_index(chat_id)
    return {"deleted": True}

@router.post("/search")
def search_code(req: SearchRequest):
    if STORE["index"] is None:
        raise HTTPException(status_code=400, detail="Run /index first")

    qvec = embed_texts([req.query])[0]
    distances, indices = search_index(STORE["index"], qvec, k=req.k)

    results = []
    for rank, (d, i) in enumerate(zip(distances, indices), start=1):
        c = STORE["chunks"][i]
        penalty = 0.25 if "test" in c.get("tags", []) else 0.0
        results.append({
            "rank": rank,
            "distance": d,
            "file": c["file"],
            "function": c["function"],
            "snippet": c["code"][:250]
        })

    return {"query": req.query, "results": results}