"""Command-line entry point, mirroring make_rst.main's file-walking and output shape."""

from __future__ import annotations

import argparse
from pathlib import Path

from c3_godot_docs_gen.parse import parse_registry
from c3_godot_docs_gen.render import render_class_markdown, render_index_markdown
from c3_godot_docs_gen.resolve import class_filename


def generate(
    xml_dir: Path, output_dir: Path, dry_run: bool = False, index: bool = False
) -> list[str]:
    registry = parse_registry(xml_dir)

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    for name, class_def in sorted(registry.items()):
        if class_def.is_private:
            continue
        filename = class_filename(name)
        if not dry_run:
            (output_dir / filename).write_text(
                render_class_markdown(class_def, registry), encoding="utf-8"
            )
        generated.append(filename)

    if index:
        if not dry_run:
            (output_dir / "index.md").write_text(
                render_index_markdown(registry), encoding="utf-8"
            )
        generated.append("index.md")

    return generated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert Godot doctool XML into Markdown docs."
    )
    parser.add_argument(
        "path", help="Directory containing the doctool-exported XML files."
    )
    parser.add_argument("output", help="Output directory for generated Markdown.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write files, just report what would be generated.",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Also generate an index.md file.",
    )
    args = parser.parse_args(argv)

    generated = generate(
        Path(args.path), Path(args.output), dry_run=args.dry_run, index=args.index
    )
    for name in generated:
        print(name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
