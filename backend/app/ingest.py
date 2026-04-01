import ast
import re
from pathlib import Path

SKIP_DIRS = {"venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "dist", ".next", "build"}

# Matches: function foo(, async function foo(, export function foo(, export default function foo(
_JS_FUNCTION = re.compile(
    r"(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*\("
)
# Matches: const foo = (...) =>, const foo = async (...) =>
_JS_ARROW = re.compile(
    r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>"
)


def _extract_block(source: str, start: int) -> str:
    """Extract a brace-delimited block starting at `start` (index of opening brace)."""
    depth = 0
    i = start
    while i < len(source):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start: i + 1]
        i += 1
    return source[start:]


def _extract_java_methods(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower()
    # Matches constructors: public ClassName(...) {
    constructor_pattern = re.compile(
        r"(?:public|private|protected)\s+([A-Z]\w*)\s*\([^)]*\)\s*\{"
    )
    # Matches regular methods: public [static] returnType methodName(...) {
    method_pattern = re.compile(
        r"(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)\s*\{"
    )
    seen_positions = set()
    for pattern in (constructor_pattern, method_pattern):
        for match in pattern.finditer(source):
            fn_name = match.group(1)
            if fn_name in {"if", "while", "for", "switch"}:
                continue
            if match.start() in seen_positions:
                continue
            seen_positions.add(match.start())
            brace_pos = source.rfind("{", match.start(), match.end())
            body = _extract_block(source, brace_pos)
            full_code = source[match.start(): match.start() + (match.end() - match.start()) + len(body) - 1]
            chunks.append({
                "file": file_path,
                "function": fn_name,
                "code": full_code[:1500],
                "tags": ["test"] if is_test else [],
            })
    return chunks


def _extract_js_functions(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower() or "spec" in file_path.lower()

    for pattern in (_JS_FUNCTION, _JS_ARROW):
        for match in pattern.finditer(source):
            fn_name = match.group(1)
            brace_pos = source.find("{", match.end())
            if brace_pos == -1:
                continue
            code = source[match.start(): brace_pos + 1]
            body = _extract_block(source, brace_pos)
            full_code = source[match.start(): match.start() + len(code) + len(body) - 1]
            chunks.append({
                "file": file_path,
                "function": fn_name,
                "code": full_code[:1500],
                "tags": ["test"] if is_test else [],
            })

    return chunks


def extract_functions(folder_path: str):
    chunks = []
    root = Path(folder_path)

    for file in root.rglob("*"):
        if any(part in SKIP_DIRS for part in file.parts):
            continue

        suffix = file.suffix.lower()

        if suffix == ".py":
            try:
                source = file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        code = ast.get_source_segment(source, node)
                        if code:
                            chunks.append({
                                "file": str(file),
                                "function": node.name,
                                "code": code,
                                "tags": ["test"] if "test" in str(file).lower() else [],
                            })
            except Exception:
                continue

        elif suffix in {".js", ".ts", ".jsx", ".tsx"}:
            try:
                source = file.read_text(encoding="utf-8", errors="ignore")
                chunks.extend(_extract_js_functions(source, str(file)))
            except Exception:
                continue

        elif suffix == ".java":
            try:
                source = file.read_text(encoding="utf-8", errors="ignore")
                chunks.extend(_extract_java_methods(source, str(file)))
            except Exception:
                continue

    return chunks