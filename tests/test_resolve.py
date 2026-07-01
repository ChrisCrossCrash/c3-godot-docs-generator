from c3_godot_docs_gen.parse import parse_registry
from c3_godot_docs_gen.resolve import (
    class_filename,
    parse_link_target,
    resolve_class_ref,
    resolve_enum_ref,
    resolve_member_link,
    resolve_type,
)


def test_resolve_class_ref_links_to_known_class(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_class_ref("C3Http.Session", registry, current_class="C3Http.Options")
    assert md == "[`C3Http.Session`](C3Http.Session.md)"


def test_resolve_class_ref_same_class_is_bold(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_class_ref("C3Http.Session", registry, current_class="C3Http.Session")
    assert md == "**C3Http.Session**"


def test_resolve_class_ref_unknown_links_to_godot_docs(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_class_ref("HTTPClient", registry, current_class="C3Http.Session")
    assert md == "[`HTTPClient`](https://docs.godotengine.org/en/stable/classes/class_httpclient.html)"


def test_resolve_type_void_is_plain_code():
    assert resolve_type("void", {}, current_class="C3Http") == "`void`"


def test_resolve_type_typed_array(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_type("Dictionary[]", registry, current_class="C3Http.Mock")
    assert "Array" in md
    assert "Dictionary" in md


def test_resolve_type_typed_dictionary():
    md = resolve_type("Dictionary[String, int]", {}, current_class="C3Http")
    assert "String" in md
    assert "int" in md
    assert md.count("Dictionary") >= 1


def test_parse_link_target_with_dot():
    assert parse_link_target("C3Http.Options.session", "C3Http.Session") == (
        "C3Http.Options",
        "session",
    )


def test_parse_link_target_without_dot_defaults_to_current_class():
    assert parse_link_target("idle_timeout", "C3Http.Session") == (
        "C3Http.Session",
        "idle_timeout",
    )


def test_resolve_member_link_same_class_uses_bare_anchor(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_member_link(
        "C3Http.Session.idle_timeout", "property", registry, current_class="C3Http.Session"
    )
    assert md == "[`idle_timeout`](#property-idle_timeout)"


def test_resolve_member_link_other_class_links_to_file(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_member_link(
        "C3Http.Options.session", "property", registry, current_class="C3Http.Session"
    )
    assert md == "[`session`](C3Http.Options.md#property-session)"


def test_resolve_member_link_method_appends_call_parens(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_member_link("C3Http.request", "method", registry, current_class="C3Http")
    assert md == "[`request()`](#method-request)"


def test_resolve_enum_ref_splits_on_last_dot(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_enum_ref(
        "C3Http.RequestError.Kind", registry, current_class="C3Http.RequestError"
    )
    assert md == "[`Kind`](#enum-Kind)"


def test_resolve_enum_ref_from_other_class(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_enum_ref("C3Http.RequestError.Kind", registry, current_class="C3Http.Response")
    assert md == "[`Kind`](C3Http.RequestError.md#enum-Kind)"


def test_resolve_class_ref_private_class_is_plain_code(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_class_ref("C3Http._Stub", registry, current_class="C3Http.Mock")
    assert md == "`C3Http._Stub`"


def test_resolve_member_link_private_class_is_plain_code(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_member_link(
        "C3Http._Stub.preset", "property", registry, current_class="C3Http.Mock"
    )
    assert md == "`preset`"


def test_resolve_enum_ref_private_class_is_plain_code(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    md = resolve_enum_ref("C3Http._Stub.Kind", registry, current_class="C3Http.Mock")
    assert md == "`C3Http._Stub.Kind`"


def test_class_filename():
    assert class_filename("C3Http.Session") == "C3Http.Session.md"
