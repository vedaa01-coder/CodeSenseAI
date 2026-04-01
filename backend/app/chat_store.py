import json
import faiss
from pathlib import Path

CHAT_DATA_DIR = Path("backend/.chat_data")


def _chat_dir(chat_id: str) -> Path:
    return CHAT_DATA_DIR / chat_id


def save_chat_index(chat_id: str, chunks: list, index, dim: int):
    d = _chat_dir(chat_id)
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "chunks.json", "w") as f:
        json.dump(chunks, f)
    faiss.write_index(index, str(d / "index.faiss"))


def load_chat_index(chat_id: str):
    d = _chat_dir(chat_id)
    if not d.exists():
        return None, None, None
    with open(d / "chunks.json") as f:
        chunks = json.load(f)
    index = faiss.read_index(str(d / "index.faiss"))
    return chunks, index, index.d


def list_saved_chats() -> list[str]:
    if not CHAT_DATA_DIR.exists():
        return []
    return [p.name for p in CHAT_DATA_DIR.iterdir() if p.is_dir()]


def delete_chat_index(chat_id: str):
    import shutil
    d = _chat_dir(chat_id)
    if d.exists():
        shutil.rmtree(d)
