import anthropic
from typing import Optional
from .config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


SYSTEM_PROMPT = """You are CodeSense AI — a patient, friendly guide helping someone understand a codebase for the very first time. Assume the person reading your answer has never seen this code before and may not know programming terms.

RULES YOU MUST NEVER BREAK:
- Never write code, pseudocode, or suggest specific fixes
- Never tell the user what to change or how to change it
- Never identify a specific bug, error, or missing symbol — not even hints like "you are missing a semicolon" or "the brace is absent here"
- If the user's code has an error, only tell them which function to look at and suggest they compare it carefully with a similar working function — say nothing more about what is wrong
- Never use jargon without immediately explaining it in plain words

HOW TO WRITE YOUR ANSWERS:
- Start by directly answering what was asked — never open with "I don't see..." or "I couldn't find..." or any hedge
- If the exact thing asked about isn't in the snippets, use what you have and say "here's where that happens" pointing to the closest relevant code
- Write like you are explaining to a curious friend, not writing documentation
- Use simple everyday analogies where possible (e.g. "think of it like a library card catalog")
- Keep sentences short and clear
- Say where things are (file name, function name) but explain what they do in plain words
- End with one simple question that nudges the person to think one step further
- Never use headers, bullet walls, or corporate-sounding language — just talk to them"""


def ask_llm(
    question: str,
    code_chunks: list,
    question_type: str = "understand",
    impact_info: Optional[list] = None,
) -> str:
    # Build code context
    context_parts = []
    for chunk in code_chunks:
        code = chunk["code"][:800]
        context_parts.append(
            f"### File: {chunk['file']}\n### Function: {chunk['function']}\n\n{code}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Build impact section if present
    impact_section = ""
    if impact_info:
        lines = ["### Other code affected by these functions:"]
        for item in impact_info:
            lines.append(f"- `{item['caller_function']}` in `{item['caller_file']}` calls `{item['target_function']}`")
        impact_section = "\n" + "\n".join(lines)

    # Tailor the task instruction based on question type
    if question_type == "where":
        task = (
            "The person wants to find something in the codebase. "
            "Tell them exactly which file and function to look at, and in one or two plain sentences, "
            "explain what that code does so they know they're in the right place."
        )
    elif question_type == "impact":
        task = (
            "The person wants to know what else would be affected if something changes. "
            "In plain words, explain what the code does right now, then name the other parts of the codebase "
            "that are connected to it and why they matter. Do not suggest what to do — just help them see the picture."
        )
    else:
        task = (
            "The person wants to understand how something works. "
            "Give a short, plain-English explanation of what the relevant code does and how the pieces fit together. "
            "Do not over-explain — answer what they asked and nothing more."
        )

    prompt = (
        f"{task}\n\n"
        f"Here are the most relevant code snippets from the codebase:\n\n"
        f"{context}"
        f"{impact_section}\n\n"
        f"Developer's question: {question}"
    )

    message = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
