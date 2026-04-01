import tempfile
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional

from .ingest import extract_functions
from .embed import embed_texts
from .vector_store import build_index
from .search_route import STORE
from .chat_store import save_chat_index

router = APIRouter()


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    chat_id: Optional[str] = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    tmp_dir = tempfile.mkdtemp()

    try:
        for upload in files:
            dest = Path(tmp_dir) / upload.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            contents = await upload.read()
            dest.write_bytes(contents)

        chunks = extract_functions(tmp_dir)
        if not chunks:
            raise HTTPException(status_code=400, detail="No functions found in uploaded files")

        vectors = embed_texts([c["code"] for c in chunks])
        index, dim = build_index(vectors)

        STORE["chunks"] = chunks
        STORE["index"] = index
        STORE["dim"] = dim

        if chat_id:
            save_chat_index(chat_id, chunks, index, dim)

        file_names = [f.filename for f in files]
        return {"indexed": True, "chunks": len(chunks), "files": file_names}

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
