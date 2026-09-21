from __future__ import annotations

import html
from pathlib import Path

from .differ import Change

SEVERITY_COLOR = {"high": "#dc2626", "medium": "#d97706", "low": "#65a30d"}
SEVERITY_LABEL = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}


def render_console(changes: list[Change], explanation: str) -> str:
    lines = [f"envdiff -- {len(changes)} difference(s) found\n"]
    for c in changes:
        label = SEVERITY_LABEL[c.severity]
        lines.append(f"[{label:>6}] {c.kind:<12} {c.path}  ({c.old!r} -> {c.new!r})")
    lines.append("\nLikely impact:\n" + explanation)
    return "\n".join(lines)


def render_html(changes: list[Change], explanation: str, baseline_label: str, target_label: str) -> str:
    rows = "\n".join(_row_html(c) for c in changes) or "<tr><td colspan='5'>No differences found.</td></tr>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>envdiff report -- {html.escape(baseline_label)} vs {html.escape(target_label)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, sans-serif; margin: 2rem; color: #1f2937; background: #f9fafb; }}
  h1 {{ font-size: 1.25rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; background: #fff; }}
  th, td {{ text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid #e5e7eb; font-size: 0.85rem; vertical-align: top; }}
  th {{ background: #f3f4f6; }}
  .badge {{ display: inline-block; padding: 0.1rem 0.5rem; border-radius: 999px; color: #fff; font-size: 0.7rem; font-weight: 600; }}
  .impact {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1rem; margin-top: 1.5rem; white-space: pre-wrap; }}
  code {{ background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 0.25rem; }}
</style>
</head>
<body>
  <h1>envdiff: {html.escape(baseline_label)} &rarr; {html.escape(target_label)}</h1>
  <p>{len(changes)} difference(s) found.</p>
  <table>
    <thead><tr><th>Severity</th><th>Type</th><th>Key</th><th>Baseline value</th><th>Target value</th></tr></thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <div class="impact">
    <strong>Likely impact</strong><br><br>
    {html.escape(explanation).replace(chr(10), "<br>")}
  </div>
</body>
</html>
"""


def _row_html(c: Change) -> str:
    color = SEVERITY_COLOR[c.severity]
    label = SEVERITY_LABEL[c.severity]
    return (
        "<tr>"
        f"<td><span class='badge' style='background:{color}'>{label}</span></td>"
        f"<td>{html.escape(c.kind)}</td>"
        f"<td><code>{html.escape(c.path)}</code></td>"
        f"<td>{html.escape(repr(c.old))}</td>"
        f"<td>{html.escape(repr(c.new))}</td>"
        "</tr>"
    )


def write_html(path: str | Path, html_content: str) -> None:
    Path(path).write_text(html_content, encoding="utf-8")
