# envdiff

Find out why it works in DEV but breaks in QA.

`envdiff` compares two environment snapshots -- env vars, feature flags,
service versions, config keys -- and flags what changed, by severity. Point
it at an API key and it'll add a plain-language note on what's likely to
break.

This is a narrow CLI slice of [EnvEye](../README.md), scoped down to
config/environment drift instead of full VM snapshotting.

## Install

```bash
cd envdiff-cli
pip install -e .
```

## Usage

```bash
envdiff compare dev.json qa.json
```

```bash
envdiff compare dev.json qa.json --html report.html
```

Snapshots can be `.json`, `.yaml`/`.yml`, or `.env` files -- whatever you
already have lying around. See [examples/](examples/) for a sample pair.

### AI impact summary

Set one of these to get a plain-language "likely impact" note:

```bash
export ANTHROPIC_API_KEY=...
# or
export OPENAI_API_KEY=...
```

Pass `--no-ai` to skip the AI call entirely (diff + severity only, no
network calls, no API key needed).

### CI usage

`envdiff compare` exits with status 1 if any high-severity (missing key)
differences are found, so it can gate a CI step:

```bash
envdiff compare known-good.json current.json --no-ai || echo "environment drift detected"
```

## Severity

| Kind | Meaning | Severity |
| --- | --- | --- |
| `missing` | Present in baseline, gone in target | high |
| `changed` / `type_changed` | Value or type differs | medium |
| `added` | New key only in target | low |
