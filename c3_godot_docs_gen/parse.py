"""XML -> model parsing, mirroring make_rst.py's State.parse_class."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from c3_godot_docs_gen.model import (
    ClassDef,
    ConstantDef,
    EnumDef,
    MethodDef,
    ParameterDef,
    PropertyDef,
    SignalDef,
    TypeRef,
)


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _type_ref(el: ET.Element) -> TypeRef:
    return TypeRef(
        type_name=el.get("type", "void"),
        enum=el.get("enum", ""),
        is_bitfield=el.get("is_bitfield", "") == "true",
    )


def _parse_params(method_el: ET.Element) -> list[ParameterDef]:
    params = sorted(method_el.findall("param"), key=lambda p: int(p.get("index", "0")))
    return [
        ParameterDef(
            name=p.get("name", ""),
            type_name=_type_ref(p),
            default_value=p.get("default"),
        )
        for p in params
    ]


def _parse_method(method_el: ET.Element) -> MethodDef:
    return_el = method_el.find("return")
    return_type = (
        _type_ref(return_el) if return_el is not None else TypeRef(type_name="void")
    )
    return MethodDef(
        name=method_el.get("name", ""),
        return_type=return_type,
        parameters=_parse_params(method_el),
        description=_text(method_el.find("description")),
        qualifiers=method_el.get("qualifiers", ""),
        deprecated=method_el.get("deprecated"),
        experimental=method_el.get("experimental"),
    )


def _parse_member(member_el: ET.Element) -> PropertyDef:
    return PropertyDef(
        name=member_el.get("name", ""),
        type_name=_type_ref(member_el),
        description=_text(member_el),
        default_value=member_el.get("default"),
        setter=member_el.get("setter", ""),
        getter=member_el.get("getter", ""),
        deprecated=member_el.get("deprecated"),
        experimental=member_el.get("experimental"),
    )


def _parse_signal(signal_el: ET.Element) -> SignalDef:
    return SignalDef(
        name=signal_el.get("name", ""),
        parameters=_parse_params(signal_el),
        description=_text(signal_el.find("description")),
        deprecated=signal_el.get("deprecated"),
        experimental=signal_el.get("experimental"),
    )


def _parse_constants(
    constants_el: ET.Element | None,
) -> tuple[list[ConstantDef], dict[str, EnumDef]]:
    constants: list[ConstantDef] = []
    enums: dict[str, EnumDef] = {}
    if constants_el is None:
        return constants, enums

    for c in constants_el.findall("constant"):
        constant = ConstantDef(
            name=c.get("name", ""),
            value=c.get("value", ""),
            enum=c.get("enum"),
            description=_text(c),
        )
        if constant.enum:
            enum_def = enums.setdefault(
                constant.enum,
                EnumDef(
                    name=constant.enum, is_bitfield=c.get("is_bitfield", "") == "true"
                ),
            )
            enum_def.values[constant.name] = constant
        else:
            constants.append(constant)

    return constants, enums


def parse_class_file(xml_path: Path) -> ClassDef:
    root = ET.parse(xml_path).getroot()

    constants, enums = _parse_constants(root.find("constants"))

    members_el = root.find("members")
    properties = {
        m.get("name", ""): _parse_member(m)
        for m in (members_el.findall("member") if members_el is not None else [])
    }

    methods_el = root.find("methods")
    methods = [
        _parse_method(m)
        for m in (methods_el.findall("method") if methods_el is not None else [])
    ]

    signals_el = root.find("signals")
    signals = [
        _parse_signal(s)
        for s in (signals_el.findall("signal") if signals_el is not None else [])
    ]

    return ClassDef(
        name=root.get("name", ""),
        inherits=root.get("inherits") or None,
        brief_description=_text(root.find("brief_description")),
        description=_text(root.find("description")),
        methods=methods,
        properties=properties,
        constants=constants,
        enums=enums,
        signals=signals,
        deprecated=root.get("deprecated"),
        experimental=root.get("experimental"),
    )


def parse_registry(xml_dir: Path) -> dict[str, ClassDef]:
    registry: dict[str, ClassDef] = {}
    for xml_path in sorted(xml_dir.glob("*.xml")):
        class_def = parse_class_file(xml_path)
        registry[class_def.name] = class_def
    return registry
