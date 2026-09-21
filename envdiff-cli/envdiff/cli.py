from __future__ import annotations

import sys

import click

from .ai import explain
from .differ import compute_changes
from .loaders import load_snapshot
from .report import render_console, render_html, write_html


@click.group()
@click.version_option(package_name="envdiff")
def main():
    """envdiff -- find out why it works in DEV but breaks in QA."""


@main.command()
@click.argument("baseline", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--html", "html_path", type=click.Path(), default=None,
              help="Write an HTML report to this path.")
@click.option("--no-ai", is_flag=True, help="Skip the AI-generated impact summary.")
@click.option("--provider", type=click.Choice(["anthropic", "openai"]), default=None,
              help="Force an AI provider (default: auto-detect from env vars).")
def compare(baseline, target, html_path, no_ai, provider):
    """Compare BASELINE (e.g. dev.json) against TARGET (e.g. qa.json)."""
    baseline_data = load_snapshot(baseline)
    target_data = load_snapshot(target)

    changes = compute_changes(baseline_data, target_data)

    if no_ai:
        explanation = "(AI summary skipped -- omit --no-ai to enable it.)"
    else:
        explanation = explain(changes, provider)

    click.echo(render_console(changes, explanation))

    if html_path:
        write_html(html_path, render_html(changes, explanation, baseline, target))
        click.echo(f"\nHTML report written to {html_path}")

    if any(c.severity == "high" for c in changes):
        sys.exit(1)


if __name__ == "__main__":
    main()
