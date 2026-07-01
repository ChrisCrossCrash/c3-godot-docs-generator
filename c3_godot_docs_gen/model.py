"""Dataclasses modeling Godot's doctool XML class-reference output."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TypeRef:
    type_name: str
    enum: str = ""
    is_bitfield: bool = False


@dataclass
class ParameterDef:
    name: str
    type_name: TypeRef
    default_value: str | None = None


@dataclass
class MethodDef:
    name: str
    return_type: TypeRef
    parameters: list[ParameterDef]
    description: str
    qualifiers: str = ""
    deprecated: str | None = None
    experimental: str | None = None

    @property
    def is_static(self) -> bool:
        return "static" in self.qualifiers.split()

    @property
    def is_private(self) -> bool:
        return self.name.startswith("_")


@dataclass
class PropertyDef:
    name: str
    type_name: TypeRef
    description: str
    default_value: str | None = None
    setter: str = ""
    getter: str = ""
    deprecated: str | None = None
    experimental: str | None = None

    @property
    def is_private(self) -> bool:
        return self.name.startswith("_")


@dataclass
class ConstantDef:
    name: str
    value: str
    enum: str | None
    description: str


@dataclass
class EnumDef:
    name: str
    is_bitfield: bool
    values: dict[str, ConstantDef] = field(default_factory=dict)


@dataclass
class SignalDef:
    name: str
    parameters: list[ParameterDef]
    description: str
    deprecated: str | None = None
    experimental: str | None = None

    @property
    def is_private(self) -> bool:
        return self.name.startswith("_")


@dataclass
class ClassDef:
    name: str
    inherits: str | None
    brief_description: str
    description: str
    methods: list[MethodDef] = field(default_factory=list)
    properties: dict[str, PropertyDef] = field(default_factory=dict)
    constants: list[ConstantDef] = field(default_factory=list)
    enums: dict[str, EnumDef] = field(default_factory=dict)
    signals: list[SignalDef] = field(default_factory=list)
    deprecated: str | None = None
    experimental: str | None = None

    @property
    def is_private(self) -> bool:
        return any(segment.startswith("_") for segment in self.name.split("."))

    def public_methods(self) -> list[MethodDef]:
        return [m for m in self.methods if not m.is_private]

    def public_properties(self) -> list[PropertyDef]:
        return [p for p in self.properties.values() if not p.is_private]

    def public_signals(self) -> list[SignalDef]:
        return [s for s in self.signals if not s.is_private]

    def find_method(self, name: str) -> MethodDef | None:
        for m in self.methods:
            if m.name == name:
                return m
        return None
