# CodeSenseAI

An AI-powered tool that helps developers understand any codebase — without being handed the answer.

Upload your code files, ask questions in plain English, and get explanations that teach you how things work. CodeSenseAI acts like a Socratic mentor: it explains, guides, and asks questions back — it never just gives you the fix.

---

## What it does

- **Understand code** — Ask "how does this work?" and get a plain-English explanation grounded in your actual code
- **Find things** — Ask "where is X implemented?" and get pointed to the exact file and function
- **Trace impact** — Ask "what would break if I change this?" and see every function that depends on it
- **Paste code in chat** — Drop a snippet directly into the chat without uploading anything
- **Never gives the answer** — Designed for learning. It guides you to figure it out yourself.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router, Vite |
| Backend | FastAPI, Python 3.9 |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector search | FAISS |
| LLM | Anthropic Claude Haiku |
| Persistence | localStorage (chat history) + FAISS index saved to disk |

---

## Supported languages

Python, JavaScript, TypeScript, Java, Go, C, C++, Rust, Swift, Kotlin, C#, PHP, Scala, Dart, Ruby, Lua, Elixir, Perl, Bash, R

---

## Features

- Drag-and-drop file upload — drop any code file and start asking questions
- Multi-chat system — separate chats each with their own code index
- Persistent chats — messages and indexes survive page refreshes
- Auto-named chats — chat names itself from your first question
- Right-click to rename or delete chats
- Collapsible source snippets — answers are clean, code is there if you want it
- Question type detection — adapts its response based on whether you're asking how, where, or what-if

---

## How it works

1. **Upload** — Drop code files into the chat. The backend extracts every function using AST parsing (Python) or regex (all other languages).
2. **Index** — Each function is embedded into a vector using Sentence Transformers and stored in a FAISS index saved to disk per chat.
3. **Ask** — Your question is embedded and compared against the index. The top matches are ranked by semantic similarity, keyword overlap, and structural signals.
4. **Explain** — The ranked code chunks are passed to Claude Haiku with a strict Socratic system prompt. It explains what the code does, never what to change.

---

## Running locally

**Backend**
```bash
cd CodeSenseAI
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

**Environment variables**

Create `backend/.env`:
```
ANTHROPIC_API_KEY=your_key_here
```

---

## Project structure

```
CodeSenseAI/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI app + CORS
│       ├── ingest.py        # Function extraction (20 languages)
│       ├── embed.py         # Sentence Transformer embeddings
│       ├── vector_store.py  # FAISS index build + search
│       ├── explain_route.py # Question classification + ranking + LLM call
│       ├── upload_route.py  # File upload endpoint
│       ├── search_route.py  # Index + chat management endpoints
│       ├── chat_store.py    # Save/load FAISS indexes per chat
│       └── llm.py           # Anthropic Claude integration + Socratic prompt
└── frontend/
    └── src/
        ├── pages/
        │   ├── home.jsx     # Landing page
        │   └── chat.jsx     # Chat UI with sidebar + multi-chat
        ├── layouts/
        │   └── app_layout.jsx
        └── lib/
            └── api.js       # HTTP client
```

---

## Sample files

The `sample_code/` directory contains Java files (`BankAccount.java`, `StudentGrades.java`) you can use to try the tool immediately without needing your own codebase.
