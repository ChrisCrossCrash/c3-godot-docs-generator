"""Name resolution and type/link rendering, mirroring make_type/make_enum in make_rst.py."""

from __future__ import annotations

from c3_godot_docs_gen.model import ClassDef

GODOT_DOCS_BASE = "https://docs.godotengine.org/en/stable/classes/class_{}.html"


def class_filename(class_name: str) -> str:
    return f"{class_name}.md"


def godot_doc_url(type_name: str) -> str:
    return GODOT_DOCS_BASE.format(type_name.lower())


def resolve_class_ref(
    class_name: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    if class_name == current_class:
        return f"**{class_name}**"
    class_def = registry.get(class_name)
    if class_def is not None:
        if class_def.is_private:
            return f"`{class_name}`"
        return f"[`{class_name}`]({class_filename(class_name)})"
    return f"[`{class_name}`]({godot_doc_url(class_name)})"


def resolve_type(
    type_name: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    if type_name == "void":
        return "`void`"

    if type_name.endswith("[]"):
        elem = type_name[: -len("[]")]
        array_link = resolve_class_ref("Array", registry, current_class)
        return f"{array_link}[{resolve_type(elem, registry, current_class)}]"

    if type_name.startswith("Dictionary[") and type_name.endswith("]"):
        inner = type_name[len("Dictionary[") : -1]
        key, _, value = inner.partition(", ")
        dict_link = resolve_class_ref("Dictionary", registry, current_class)
        return (
            f"{dict_link}[{resolve_type(key, registry, current_class)}, "
            f"{resolve_type(value, registry, current_class)}]"
        )

    return resolve_class_ref(type_name, registry, current_class)


def resolve_class_ref_html(
    class_name: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    """Like resolve_class_ref, but as a bare HTML fragment (no backticks) for
    embedding inside a single continuous <code> element."""
    if class_name == current_class:
        return class_name
    class_def = registry.get(class_name)
    if class_def is not None:
        if class_def.is_private:
            return class_name
        return f'<a href="{class_filename(class_name)}">{class_name}</a>'
    return f'<a href="{godot_doc_url(class_name)}">{class_name}</a>'


def resolve_type_html(
    type_name: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    if type_name == "void":
        return "void"

    if type_name.endswith("[]"):
        elem = type_name[: -len("[]")]
        array_link = resolve_class_ref_html("Array", registry, current_class)
        return f"{array_link}[{resolve_type_html(elem, registry, current_class)}]"

    if type_name.startswith("Dictionary[") and type_name.endswith("]"):
        inner = type_name[len("Dictionary[") : -1]
        key, _, value = inner.partition(", ")
        dict_link = resolve_class_ref_html("Dictionary", registry, current_class)
        return (
            f"{dict_link}[{resolve_type_html(key, registry, current_class)}, "
            f"{resolve_type_html(value, registry, current_class)}]"
        )

    return resolve_class_ref_html(type_name, registry, current_class)


def parse_link_target(link_target: str, current_class: str) -> tuple[str, str]:
    if "." in link_target:
        cls, _, name = link_target.rpartition(".")
        return cls, name
    return current_class, link_target


def resolve_member_link(
    link_target: str, kind: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    cls, name = parse_link_target(link_target, current_class)
    anchor = f"{kind}-{name}"
    label = f"{name}()" if kind == "method" else name

    class_def = registry.get(cls)
    if class_def is None or class_def.is_private:
        return f"`{label}`"
    if cls == current_class:
        return f"[`{label}`](#{anchor})"
    return f"[`{label}`]({class_filename(cls)}#{anchor})"


def resolve_constant_ref(
    link_target: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    cls, name = parse_link_target(link_target, current_class)
    class_def = registry.get(cls)
    if class_def is None or class_def.is_private:
        return f"`{name}`"

    anchor: str | None = None
    if any(c.name == name for c in class_def.constants):
        anchor = f"constant-{name}"
    else:
        for enum_def in class_def.enums.values():
            if name in enum_def.values:
                anchor = f"enum-{enum_def.name}-{name}"
                break

    if anchor is None:
        return f"`{name}`"
    if cls == current_class:
        return f"[`{name}`](#{anchor})"
    return f"[`{name}`]({class_filename(cls)}#{anchor})"


def resolve_enum_ref(
    enum_ref: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    pos = enum_ref.rfind(".")
    if pos >= 0:
        cls = enum_ref[:pos]
        enum_name = enum_ref[pos + 1 :]
    else:
        cls = current_class
        enum_name = enum_ref

    class_def = registry.get(cls)
    if class_def is None or class_def.is_private or enum_name not in class_def.enums:
        return f"`{enum_ref}`"

    anchor = f"enum-{enum_name}"
    if cls == current_class:
        return f"[`{enum_name}`](#{anchor})"
    return f"[`{enum_name}`]({class_filename(cls)}#{anchor})"


def resolve_enum_ref_html(
    enum_ref: str, registry: dict[str, ClassDef], current_class: str
) -> str:
    pos = enum_ref.rfind(".")
    if pos >= 0:
        cls = enum_ref[:pos]
        enum_name = enum_ref[pos + 1 :]
    else:
        cls = current_class
        enum_name = enum_ref

    class_def = registry.get(cls)
    if class_def is None or class_def.is_private or enum_name not in class_def.enums:
        return enum_ref

    anchor = f"enum-{enum_name}"
    if cls == current_class:
        return f'<a href="#{anchor}">{enum_name}</a>'
    return f'<a href="{class_filename(cls)}#{anchor}">{enum_name}</a>'
