# c3-godot-docs-gen

Converts Godot's `--doctool` XML class-reference output into Markdown
documentation (GitHub-Flavored Markdown), for GDScript-only projects.

## Installation

```sh
pip install c3-godot-docs-gen
```

## Usage

**1. Export class-reference XML from your Godot project:**

```sh
godot --doctool path/to/xml_output --gdscript-docs res://path/to/your/scripts
```

This produces one `.xml` file per class (e.g. `MyClass.xml`).

**2. Generate Markdown documentation:**

```sh
c3-godot-docs-gen path/to/xml_output docs/api
```

- `path` — directory containing the doctool-exported XML files.
- `output` — output directory for generated Markdown.
- `--dry-run` — print the filenames that would be generated without writing them.

This writes one `ClassName.md` file per public class, plus an `index.md`
listing all public classes.

## Development

Set up the dev environment:

```sh
poetry install
```

Run the test suite:

```sh
pytest
```

The implementation is split into independently-testable layers:

| Module | Responsibility |
|---|---|
| `model.py` | Dataclasses for the parsed class model (`ClassDef`, `MethodDef`, `PropertyDef`, `SignalDef`, `ConstantDef`, `EnumDef`). |
| `parse.py` | Parses doctool XML into the model and builds the class registry. |
| `resolve.py` | Resolves class/member/enum/constant references into Markdown links and anchors. |
| `bbcode.py` | Converts Godot's BBCode-like markup in descriptions into Markdown. |
| `render.py` | Renders a parsed class into a Markdown page. |
| `cli.py` | Command-line entry point; orchestrates parsing, rendering, and file output. |

Tests live under `tests/`, with one test file per module and shared XML
fixtures in `tests/fixtures/xml/`.
