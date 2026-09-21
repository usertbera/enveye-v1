from __future__ import annotations

import os

from .differ import Change

SYSTEM_PROMPT = (
    "You are a senior DevOps engineer. You are given a list of configuration "
    "differences between a baseline environment (e.g. DEV, where things work) "
    "and a target environment (e.g. QA, where something is broken). "
    "For each change that plausibly explains a functional failure, write one "
    "short, plain-language bullet describing the likely user-visible impact. "
    "Skip changes that are clearly cosmetic or expected (e.g. timestamps, "
    "hostnames, build IDs). Be concrete and specific, referencing the key name. "
    "Keep the whole response under 200 words. If nothing looks impactful, say so."
)


def explain(changes: list[Change], provider: str | None = None) -> str:
    if not changes:
        return "No differences found."

    provider = provider or _detect_provider()
    if provider is None:
        return (
            "(No AI provider configured -- set ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "to get a plain-language impact summary, or pass --no-ai to suppress "
            "this message.)"
        )

    diff_text = _format_changes(changes[:40])  # cap to keep the prompt small
    if provider == "anthropic":
        return _explain_anthropic(diff_text)
    if provider == "openai":
        return _explain_openai(diff_text)
    raise ValueError(f"Unknown AI provider: {provider}")


def _format_changes(changes: list[Change]) -> str:
    lines = []
    for c in changes:
        if c.kind == "missing":
            lines.append(f"- MISSING in target: {c.path} (was {c.old!r} in baseline)")
        elif c.kind == "added":
            lines.append(f"- ADDED in target: {c.path} = {c.new!r}")
        elif c.kind == "changed":
            lines.append(f"- CHANGED: {c.path} went from {c.old!r} to {c.new!r}")
        elif c.kind == "type_changed":
            lines.append(f"- TYPE CHANGED: {c.path} went from {c.old!r} to {c.new!r}")
    return "\n".join(lines)


def _detect_provider() -> str | None:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None


def _explain_anthropic(diff_text: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=os.getenv("ENVDIFF_ANTHROPIC_MODEL", "claude-sonnet-5"),
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": diff_text}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()


def _explain_openai(diff_text: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("ENVDIFF_OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": diff_text},
        ],
    )
    return response.choices[0].message.content.strip()
