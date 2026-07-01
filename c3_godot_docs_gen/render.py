"""Per-class Markdown rendering, mirroring make_rst_class's section order."""

from __future__ import annotations

import html

from c3_godot_docs_gen.bbcode import bbcode_to_markdown
from c3_godot_docs_gen.model import ClassDef, ParameterDef, TypeRef
from c3_godot_docs_gen.resolve import (
    class_filename,
    resolve_class_ref,
    resolve_enum_ref,
    resolve_enum_ref_html,
    resolve_type,
    resolve_type_html,
)


def _render_member_type(
    type_ref: TypeRef, registry: dict[str, ClassDef], current_class: str
) -> str:
    if type_ref.enum:
        return resolve_enum_ref(type_ref.enum, registry, current_class)
    return resolve_type(type_ref.type_name, registry, current_class)


def _render_member_type_html(
    type_ref: TypeRef, registry: dict[str, ClassDef], current_class: str
) -> str:
    if type_ref.enum:
        return resolve_enum_ref_html(type_ref.enum, registry, current_class)
    return resolve_type_html(type_ref.type_name, registry, current_class)


def _format_params_html(
    params: list[ParameterDef], registry: dict[str, ClassDef], current_class: str
) -> str:
    """Renders a parameter list as a bare HTML fragment (no backticks) so it can be
    embedded inside a single continuous <code> element alongside linked type names."""
    parts = []
    for p in params:
        type_html = _render_member_type_html(p.type_name, registry, current_class)
        piece = f"{html.escape(p.name)}: {type_html}"
        if p.default_value is not None:
            piece += f" = {html.escape(p.default_value)}"
        parts.append(piece)
    return ", ".join(parts)


def render_class_markdown(class_def: ClassDef, registry: dict[str, ClassDef]) -> str:
    cc = class_def.name
    lines: list[str] = []

    lines.append(f"# {cc}")
    lines.append("")

    if class_def.deprecated is not None:
        lines.append(f"**Deprecated:** {class_def.deprecated}")
        lines.append("")
    if class_def.experimental is not None:
        lines.append(f"**Experimental:** {class_def.experimental}")
        lines.append("")

    if class_def.inherits:
        lines.append(
            f"**Inherits:** {resolve_class_ref(class_def.inherits, registry, cc)}"
        )
        lines.append("")

    brief = bbcode_to_markdown(class_def.brief_description, cc, registry)
    if brief:
        lines.append(brief)
        lines.append("")

    description = bbcode_to_markdown(class_def.description, cc, registry)
    if description and description != brief:
        lines.append("## Description")
        lines.append("")
        lines.append(description)
        lines.append("")

    properties = class_def.public_properties()
    methods = class_def.public_methods()
    signals = class_def.public_signals()

    if properties:
        lines.append("## Properties")
        lines.append("")
        lines.append("| Type | Name | Default |")
        lines.append("|------|------|---------|")
        for p in properties:
            type_md = _render_member_type(p.type_name, registry, cc)
            default_cell = f"`{p.default_value}`" if p.default_value is not None else ""
            lines.append(
                f"| {type_md} | [`{p.name}`](#property-{p.name}) | {default_cell} |"
            )
        lines.append("")

    if methods:
        lines.append("## Methods")
        lines.append("")
        lines.append("| Returns | Signature |")
        lines.append("|---------|-----------|")
        for m in methods:
            ret_md = _render_member_type(m.return_type, registry, cc)
            sig_html = _format_params_html(m.parameters, registry, cc)
            name_link = f'<a href="#method-{m.name}">{html.escape(m.name)}</a>'
            lines.append(f"| {ret_md} | <code>{name_link}({sig_html})</code> |")
        lines.append("")

    if signals:
        lines.append("## Signals")
        lines.append("")
        lines.append("| Signal |")
        lines.append("|--------|")
        for s in signals:
            sig_html = _format_params_html(s.parameters, registry, cc)
            name_link = f'<a href="#signal-{s.name}">{html.escape(s.name)}</a>'
            lines.append(f"| <code>{name_link}({sig_html})</code> |")
        lines.append("")

    if class_def.constants or class_def.enums:
        lines.append("## Constants")
        lines.append("")
        for c in class_def.constants:
            lines.append(f'<a id="constant-{c.name}"></a>')
            lines.append("")
            lines.append(
                f"**<code>{html.escape(c.name)} = {html.escape(c.value)}</code>**"
            )
            desc = bbcode_to_markdown(c.description, cc, registry)
            if desc:
                lines.append("")
                lines.append(desc)
            lines.append("")

        for enum_name, enum_def in class_def.enums.items():
            kind_word = "bitfield" if enum_def.is_bitfield else "enum"
            lines.append(f'<a id="enum-{enum_name}"></a>')
            lines.append("")
            lines.append(f"### {kind_word} `{enum_name}`")
            lines.append("")
            lines.append("| Name | Value | Description |")
            lines.append("|------|-------|-------------|")
            for v in enum_def.values.values():
                desc_cell = bbcode_to_markdown(v.description, cc, registry)
                desc_cell = desc_cell.replace("\n", " ").replace("|", "\\|")
                anchor = f'<a id="enum-{enum_name}-{v.name}"></a>'
                lines.append(f"| {anchor} `{v.name}` | `{v.value}` | {desc_cell} |")
            lines.append("")

    if properties:
        lines.append("## Property Descriptions")
        lines.append("")
        for p in properties:
            type_html = _render_member_type_html(p.type_name, registry, cc)
            default_suffix = (
                f" = {html.escape(p.default_value)}"
                if p.default_value is not None
                else ""
            )
            lines.append(f'<a id="property-{p.name}"></a>')
            lines.append("")
            lines.append(
                f"### <code>{type_html} {html.escape(p.name)}{default_suffix}</code>"
            )
            lines.append("")
            desc = bbcode_to_markdown(p.description, cc, registry)
            if desc:
                lines.append(desc)
                lines.append("")

    if methods:
        lines.append("## Method Descriptions")
        lines.append("")
        for m in methods:
            ret_html = _render_member_type_html(m.return_type, registry, cc)
            sig_html = _format_params_html(m.parameters, registry, cc)
            lines.append(f'<a id="method-{m.name}"></a>')
            lines.append("")
            lines.append(
                f"### <code>{ret_html} {html.escape(m.name)}({sig_html})</code>"
            )
            lines.append("")
            desc = bbcode_to_markdown(m.description, cc, registry)
            if desc:
                lines.append(desc)
                lines.append("")

    if signals:
        lines.append("## Signal Descriptions")
        lines.append("")
        for s in signals:
            sig_html = _format_params_html(s.parameters, registry, cc)
            lines.append(f'<a id="signal-{s.name}"></a>')
            lines.append("")
            lines.append(f"### <code>{html.escape(s.name)}({sig_html})</code>")
            lines.append("")
            desc = bbcode_to_markdown(s.description, cc, registry)
            if desc:
                lines.append(desc)
                lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_index_markdown(registry: dict[str, ClassDef]) -> str:
    lines = ["# Class Reference", "", "## Classes", ""]
    public_names = sorted(name for name, c in registry.items() if not c.is_private)
    for name in public_names:
        lines.append(f"- [`{name}`]({class_filename(name)})")
    return "\n".join(lines).strip() + "\n"
