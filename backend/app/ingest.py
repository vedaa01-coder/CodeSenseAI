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


# C/C++: return_type function_name(
_C_FUNCTION = re.compile(
    r"^(?![\s#])(?:[\w\*\s]+?)\s+(\w+)\s*\([^;]*\)\s*\{",
    re.MULTILINE,
)

# Ruby: def method_name or def self.method_name
_RUBY_DEF = re.compile(r"^\s*def\s+(self\.)?(\w+)", re.MULTILINE)

# Go: func (receiver) FuncName( or func FuncName(
_GO_FUNC = re.compile(r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(", re.MULTILINE)


def _extract_c_functions(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower()
    skip = {"if", "else", "for", "while", "switch", "return", "sizeof", "typedef"}
    for match in _C_FUNCTION.finditer(source):
        fn_name = match.group(1)
        if fn_name in skip:
            continue
        brace_pos = source.find("{", match.start())
        if brace_pos == -1:
            continue
        body = _extract_block(source, brace_pos)
        full_code = source[match.start(): brace_pos + len(body)]
        chunks.append({"file": file_path, "function": fn_name, "code": full_code[:1500], "tags": ["test"] if is_test else []})
    return chunks


def _extract_ruby_functions(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower() or "spec" in file_path.lower()
    lines = source.splitlines()
    for i, line in enumerate(lines):
        m = _RUBY_DEF.match(line)
        if not m:
            continue
        fn_name = m.group(2)
        depth = 0
        body_lines = []
        for j in range(i, len(lines)):
            l = lines[j]
            body_lines.append(l)
            depth += len(re.findall(r"\b(def|do|if|unless|while|until|for|begin|class|module)\b", l))
            depth -= len(re.findall(r"\bend\b", l))
            if j > i and depth <= 0:
                break
        chunks.append({"file": file_path, "function": fn_name, "code": "\n".join(body_lines)[:1500], "tags": ["test"] if is_test else []})
    return chunks


def _extract_go_functions(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower()
    for match in _GO_FUNC.finditer(source):
        fn_name = match.group(1)
        brace_pos = source.find("{", match.start())
        if brace_pos == -1:
            continue
        body = _extract_block(source, brace_pos)
        full_code = source[match.start(): brace_pos + len(body)]
        chunks.append({"file": file_path, "function": fn_name, "code": full_code[:1500], "tags": ["test"] if is_test else []})
    return chunks


# ── Brace-delimited languages (Rust, Swift, Kotlin, C#, PHP, Scala, Dart) ──

_RUST_FN    = re.compile(r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*[<(]")
_SWIFT_FUNC = re.compile(r"(?:(?:public|private|internal|open|fileprivate)\s+)?(?:static\s+)?func\s+(\w+)\s*[<(]")
_KOTLIN_FUN = re.compile(r"(?:(?:public|private|protected|internal|override|suspend)\s+)*fun\s+(\w+)\s*[<(]")
_CSHARP_METHOD = re.compile(
    r"(?:public|private|protected|internal|static|override|virtual|async)\s+"
    r"(?:[\w<>\[\]]+\s+)+(\w+)\s*\("
)
_PHP_FUNC   = re.compile(r"(?:public|private|protected|static|\s)*function\s+(\w+)\s*\(")
_SCALA_DEF  = re.compile(r"(?:def)\s+(\w+)\s*[(\[]")
_DART_FUNC  = re.compile(r"(?:(?:void|Future|Stream|String|int|double|bool|dynamic|var|List|Map)\s+)(\w+)\s*\(")
_LUA_FUNC   = re.compile(r"(?:local\s+)?function\s+(\w+)\s*\(")
_PERL_SUB   = re.compile(r"^sub\s+(\w+)\s*\{", re.MULTILINE)
_BASH_FUNC  = re.compile(r"^(?:function\s+)?(\w+)\s*\(\s*\)\s*\{", re.MULTILINE)


def _extract_brace_functions(source: str, file_path: str, pattern: re.Pattern, skip: set = None) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower() or "spec" in file_path.lower()
    skip = skip or set()
    for match in pattern.finditer(source):
        fn_name = match.group(1)
        if fn_name in skip:
            continue
        brace_pos = source.find("{", match.start())
        if brace_pos == -1:
            continue
        body = _extract_block(source, brace_pos)
        full_code = source[match.start(): brace_pos + len(body)]
        chunks.append({"file": file_path, "function": fn_name, "code": full_code[:1500], "tags": ["test"] if is_test else []})
    return chunks


# ── End-delimited languages (Elixir) ─────────────────────────────────────────

_ELIXIR_DEF = re.compile(r"^\s*(?:def|defp)\s+(\w+)", re.MULTILINE)
_END_KEYWORDS = re.compile(r"\b(def|defp|do)\b")
_END_WORD = re.compile(r"\bend\b")


def _extract_elixir_functions(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower()
    lines = source.splitlines()
    for i, line in enumerate(lines):
        m = _ELIXIR_DEF.match(line)
        if not m:
            continue
        fn_name = m.group(1)
        depth, body_lines = 0, []
        for j in range(i, len(lines)):
            l = lines[j]
            body_lines.append(l)
            depth += len(_END_KEYWORDS.findall(l))
            depth -= len(_END_WORD.findall(l))
            if j > i and depth <= 0:
                break
        chunks.append({"file": file_path, "function": fn_name, "code": "\n".join(body_lines)[:1500], "tags": ["test"] if is_test else []})
    return chunks


# ── R ─────────────────────────────────────────────────────────────────────────

_R_FUNC = re.compile(r"(\w+)\s*<-\s*function\s*\(")


def _extract_r_functions(source: str, file_path: str) -> list[dict]:
    chunks = []
    is_test = "test" in file_path.lower()
    for match in _R_FUNC.finditer(source):
        fn_name = match.group(1)
        brace_pos = source.find("{", match.start())
        if brace_pos == -1:
            continue
        body = _extract_block(source, brace_pos)
        full_code = source[match.start(): brace_pos + len(body)]
        chunks.append({"file": file_path, "function": fn_name, "code": full_code[:1500], "tags": ["test"] if is_test else []})
    return chunks


def extract_functions(folder_path: str):
    chunks = []
    root = Path(folder_path)

    for file in root.rglob("*"):
        if any(part in SKIP_DIRS for part in file.parts):
            continue

        suffix = file.suffix.lower()

        try:
            source = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if suffix == ".py":
            try:
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        code = ast.get_source_segment(source, node)
                        if code:
                            chunks.append({"file": str(file), "function": node.name, "code": code, "tags": ["test"] if "test" in str(file).lower() else []})
            except Exception:
                continue

        elif suffix in {".js", ".ts", ".jsx", ".tsx"}:
            chunks.extend(_extract_js_functions(source, str(file)))

        elif suffix == ".java":
            chunks.extend(_extract_java_methods(source, str(file)))

        elif suffix in {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}:
            chunks.extend(_extract_c_functions(source, str(file)))

        elif suffix == ".rb":
            chunks.extend(_extract_ruby_functions(source, str(file)))

        elif suffix == ".go":
            chunks.extend(_extract_go_functions(source, str(file)))

        elif suffix == ".rs":
            chunks.extend(_extract_brace_functions(source, str(file), _RUST_FN))

        elif suffix == ".swift":
            chunks.extend(_extract_brace_functions(source, str(file), _SWIFT_FUNC))

        elif suffix in {".kt", ".kts"}:
            chunks.extend(_extract_brace_functions(source, str(file), _KOTLIN_FUN))

        elif suffix in {".cs"}:
            chunks.extend(_extract_brace_functions(source, str(file), _CSHARP_METHOD, skip={"if", "while", "for", "foreach", "switch"}))

        elif suffix == ".php":
            chunks.extend(_extract_brace_functions(source, str(file), _PHP_FUNC))

        elif suffix in {".scala", ".sc"}:
            chunks.extend(_extract_brace_functions(source, str(file), _SCALA_DEF))

        elif suffix == ".dart":
            chunks.extend(_extract_brace_functions(source, str(file), _DART_FUNC, skip={"if", "while", "for", "switch"}))

        elif suffix == ".lua":
            chunks.extend(_extract_brace_functions(source, str(file), _LUA_FUNC))

        elif suffix in {".pl", ".pm"}:
            chunks.extend(_extract_brace_functions(source, str(file), _PERL_SUB))

        elif suffix in {".sh", ".bash"}:
            chunks.extend(_extract_brace_functions(source, str(file), _BASH_FUNC))

        elif suffix == ".ex" or suffix == ".exs":
            chunks.extend(_extract_elixir_functions(source, str(file)))

        elif suffix == ".r":
            chunks.extend(_extract_r_functions(source, str(file)))

    return chunks