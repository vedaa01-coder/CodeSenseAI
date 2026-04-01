from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

from .embed import embed_texts
from .vector_store import search_index
from .search_route import STORE
from .llm import ask_llm

router = APIRouter()


class ExplainRequest(BaseModel):
    question: str


# ---------------------------------------------------------------------------
# Question classification
# ---------------------------------------------------------------------------

_WHERE_KEYWORDS = {"where", "find", "located", "location", "which file", "which function"}
_IMPACT_KEYWORDS = {"affect", "affected", "impact", "change", "break", "depend", "depends", "if i", "what happens"}

def classify_question(question: str) -> str:
    q = question.lower()
    if any(kw in q for kw in _WHERE_KEYWORDS):
        return "where"
    if any(kw in q for kw in _IMPACT_KEYWORDS):
        return "impact"
    return "understand"


# ---------------------------------------------------------------------------
# Relevance filtering and scoring
# ---------------------------------------------------------------------------

def is_relevant(file_name: str) -> bool:
    f = file_name.lower()
    return "__pycache__" not in f and "test" not in f


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z_]+", text.lower())


def keyword_score(chunk: dict, query_tokens: list[str]) -> int:
    text_tokens = tokenize(chunk["file"] + " " + chunk["function"] + " " + chunk["code"])
    return len(set(text_tokens) & set(query_tokens))


def structure_score(chunk: dict) -> int:
    fn = chunk["function"].lower()
    score = 0
    if "extract" in fn or "process" in fn:
        score += 2
    if "index" in fn or "build" in fn:
        score += 2
    if "search" in fn or "query" in fn:
        score += 1
    if "test" in fn:
        score -= 2
    return score


# ---------------------------------------------------------------------------
# Impact analysis
# ---------------------------------------------------------------------------

def find_callers(target_function: str, chunks: list[dict]) -> list[dict]:
    """Find every function in the codebase that calls target_function."""
    pattern = re.compile(rf"\b{re.escape(target_function)}\s*\(")
    callers = []
    for c in chunks:
        if c["function"] == target_function:
            continue
        if pattern.search(c["code"]):
            callers.append({
                "target_function": target_function,
                "caller_function": c["function"],
                "caller_file": c["file"],
            })
    return callers


def build_impact_info(results: list[dict], chunks: list[dict]) -> list[dict]:
    """For each result function, find everything that calls it."""
    impact = []
    seen = set()
    for r in results:
        for caller in find_callers(r["function"], chunks):
            key = (caller["caller_file"], caller["caller_function"], caller["target_function"])
            if key not in seen:
                seen.add(key)
                impact.append(caller)
    return impact


# ---------------------------------------------------------------------------
# Pasted code detection
# ---------------------------------------------------------------------------

_CODE_BLOCK = re.compile(r"```(?:\w+)?\n?(.*?)```", re.DOTALL)

def extract_pasted_chunks(question: str) -> tuple[list[dict], str]:
    """Extract code blocks from the question. Returns (chunks, cleaned_question)."""
    chunks = []
    matches = _CODE_BLOCK.findall(question)
    for i, code in enumerate(matches):
        code = code.strip()
        if code:
            chunks.append({
                "file": "pasted code",
                "function": f"snippet_{i + 1}",
                "code": code,
                "snippet": code[:400],
                "distance": 0.0,
                "keyword_score": 0,
                "structure_score": 0,
            })
    cleaned = _CODE_BLOCK.sub("", question).strip()
    return chunks, cleaned


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.post("/explain")
def explain(req: ExplainRequest):
    pasted_chunks, clean_question = extract_pasted_chunks(req.question)

    if STORE["index"] is None and not pasted_chunks:
        raise HTTPException(status_code=400, detail="Upload a file or paste some code to get started")

    question_type = classify_question(clean_question)
    query_tokens = tokenize(clean_question)

    index_results = []
    if STORE["index"] is not None:
        total = len(STORE["chunks"])
        qvec = embed_texts([clean_question])[0]
        distances, indices = search_index(STORE["index"], qvec, k=total)

        for d, i in zip(distances, indices):
            c = STORE["chunks"][i]
            if not is_relevant(c["file"]):
                continue
            index_results.append({
                "file": c["file"],
                "function": c["function"],
                "code": c["code"],
                "snippet": c["code"][:400],
                "distance": float(d),
                "keyword_score": keyword_score(c, query_tokens),
                "structure_score": structure_score(c),
            })

        index_results.sort(key=lambda x: (-x["keyword_score"], -x["structure_score"], x["distance"]))

    # Pasted code always comes first so it gets priority in the LLM context
    results = pasted_chunks + index_results

    impact_info = build_impact_info(results, STORE["chunks"]) if question_type == "impact" and STORE["chunks"] else []

    answer = ask_llm(clean_question or req.question, results, question_type=question_type, impact_info=impact_info)

    for r in results:
        r.pop("code", None)

    return {"answer": answer, "results": results}
