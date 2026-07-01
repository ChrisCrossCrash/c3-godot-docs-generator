"""BBCode -> Markdown text conversion, mirroring format_text_block in make_rst.py."""

from __future__ import annotations

import re

from c3_godot_docs_gen.model import ClassDef
from c3_godot_docs_gen.resolve import (
    resolve_class_ref,
    resolve_constant_ref,
    resolve_enum_ref,
    resolve_member_link,
)

CODEBLOCK_RE = re.compile(r"\[codeblock\](.*?)\[/codeblock\]", re.DOTALL)

_CROSSLINK_KINDS = {
    "member": "property",
    "method": "method",
    "constructor": "method",
    "operator": "method",
    "signal": "signal",
    "annotation": "annotation",
    "theme_item": "theme_item",
}


def bbcode_to_markdown(
    text: str, current_class: str, registry: dict[str, ClassDef]
) -> str:
    if not text:
        return ""

    chunks: list[str] = []
    pos = 0
    for m in CODEBLOCK_RE.finditer(text):
        before_md = _convert_inline(
            _paragraphs(text[pos : m.start()]), current_class, registry
        )
        if before_md.strip():
            chunks.append(before_md.strip())
        chunks.append(_render_codeblock(m.group(1)))
        pos = m.end()

    tail_md = _convert_inline(_paragraphs(text[pos:]), current_class, registry)
    if tail_md.strip():
        chunks.append(tail_md.strip())

    return "\n\n".join(chunks)


def _paragraphs(text: str) -> str:
    lines = [line.strip() for line in text.split("\n")]
    return "\n\n".join(line for line in lines if line)


def _render_codeblock(code: str) -> str:
    lines = code.split("\n")
    non_empty = [line for line in lines if line.strip()]
    base = min((len(line) - len(line.lstrip("\t")) for line in non_empty), default=0)

    dedented = []
    for line in lines:
        if not line.strip():
            dedented.append("")
            continue
        tabs = len(line) - len(line.lstrip("\t"))
        dedented.append("    " * max(tabs - base, 0) + line.lstrip("\t"))

    code_text = "\n".join(dedented).strip("\n")
    return f"```gdscript\n{code_text}\n```"


def _parse_tag(tag_text: str) -> tuple[bool, str, str]:
    closing = tag_text.startswith("/")
    body = tag_text[1:] if closing else tag_text
    if "=" in body:
        name, _, arg = body.partition("=")
    elif " " in body:
        name, _, arg = body.partition(" ")
    else:
        name, arg = body, ""
    return closing, name.strip(), arg.strip()


def _convert_inline(
    text: str, current_class: str, registry: dict[str, ClassDef]
) -> str:
    out: list[str] = []
    pos = 0
    while True:
        start = text.find("[", pos)
        if start == -1:
            out.append(text[pos:])
            break
        out.append(text[pos:start])

        end = text.find("]", start + 1)
        if end == -1:
            out.append(text[start:])
            break

        tag_text = text[start + 1 : end]

        if tag_text in registry:
            out.append(resolve_class_ref(tag_text, registry, current_class))
            pos = end + 1
            continue

        replacement, new_pos = _convert_tag(
            tag_text, text, end, current_class, registry
        )
        out.append(replacement)
        pos = new_pos

    return "".join(out)


def _convert_tag(
    tag_text: str,
    text: str,
    end: int,
    current_class: str,
    registry: dict[str, ClassDef],
) -> tuple[str, int]:
    closing, name, arg = _parse_tag(tag_text)

    if name == "code":
        close_idx = text.find("[/code]", end + 1)
        if close_idx == -1:
            return f"`{tag_text}`", end + 1
        content = text[end + 1 : close_idx].replace("\n", " ")
        return f"`{content}`", close_idx + len("[/code]")

    if name == "kbd":
        close_idx = text.find("[/kbd]", end + 1)
        if close_idx == -1:
            return f"`{tag_text}`", end + 1
        content = text[end + 1 : close_idx]
        return f"`{content}`", close_idx + len("[/kbd]")

    if name == "url":
        close_idx = text.find("[/url]", end + 1)
        if close_idx == -1:
            return f"`{tag_text}`", end + 1
        title = text[end + 1 : close_idx]
        url = arg if arg else title
        return f"[{title}]({url})", close_idx + len("[/url]")

    if name == "b":
        return "**", end + 1
    if name == "i":
        return "*", end + 1
    if name == "u":
        return "</u>" if closing else "<u>", end + 1
    if name == "center":
        return "", end + 1
    if name == "br":
        return "\n\n", end + 1
    if name == "lb":
        return "[", end + 1
    if name == "rb":
        return "]", end + 1
    if name == "param":
        return f"`{arg}`", end + 1
    if name == "enum":
        return resolve_enum_ref(arg, registry, current_class), end + 1
    if name == "constant":
        return resolve_constant_ref(arg, registry, current_class), end + 1
    if name in _CROSSLINK_KINDS:
        return (
            resolve_member_link(arg, _CROSSLINK_KINDS[name], registry, current_class),
            end + 1,
        )

    return f"`{tag_text}`", end + 1
