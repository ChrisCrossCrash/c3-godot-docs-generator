# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
# Install dependencies
poetry install

# Run all tests
pytest

# Run a single test file
pytest tests/test_render.py

# Run a single test by name
pytest tests/test_render.py -k "test_name"

# Lint
flake8

# Format
black .

# Run the CLI
c3-godot-docs-gen path/to/xml_output -o docs/api
```

Flake8 max line length is 110; `E203` is ignored.

## Architecture

The pipeline is a strict one-way chain:

```
XML files → parse.py → model.py → (resolve.py, bbcode.py) → render.py → cli.py → .md files
```

**`model.py`** — Pure dataclasses: `ClassDef`, `MethodDef`, `PropertyDef`, `SignalDef`, `ConstantDef`, `EnumDef`, `ParameterDef`, `TypeRef`. No parsing or rendering logic here. Privacy (underscore prefix on any name segment) is determined by `is_private` properties on the dataclasses.

**`parse.py`** — Reads Godot `--doctool` XML files and produces a `registry: dict[str, ClassDef]`. Entry point is `parse_registry(xml_dir)`.

**`resolve.py`** — Converts type names and cross-references into Markdown links. Knows about the registry; links to local `.md` files for classes in the registry, or to `docs.godotengine.org` for Godot built-ins. Private classes are rendered as inline code, not links.

**`bbcode.py`** — Converts Godot's BBCode-like description markup (`[method X]`, `[param X]`, `[b]`, etc.) into Markdown. Calls into `resolve.py` for cross-reference tags.

**`render.py`** — Takes a `ClassDef` + registry and returns a complete Markdown string. Entry points: `render_class_markdown(class_def, registry)` and `render_index_markdown(registry)`.

**`cli.py`** — `generate()` wires the pipeline together; `main()` is the argparse entry point. Skips private classes and writes one `.md` per public class plus an `index.md`.

## Tests

One test file per module (`test_parse.py`, `test_render.py`, etc.). Shared XML fixtures live in `tests/fixtures/xml/` — these are real Godot doctool XML files for a `C3Http` library used as the test corpus. `tests/conftest.py` holds shared fixtures.
