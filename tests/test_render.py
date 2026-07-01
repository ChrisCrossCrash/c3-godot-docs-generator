from c3_godot_docs_gen.parse import parse_registry
from c3_godot_docs_gen.render import render_class_markdown


def test_title_and_inherits(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert md.startswith("# C3Http.Session\n")
    assert (
        "**Inherits:** [`RefCounted`](https://docs.godotengine.org/en/stable/classes/class_refcounted.html)"
        in md
    )


def test_properties_table_excludes_private(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert "## Properties" in md
    assert "max_connections_per_host" in md
    assert "idle_timeout" in md
    assert "_pool" not in md
    assert "_mutex" not in md


def test_methods_table_excludes_private(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert "## Methods" in md
    assert "close" in md
    assert "checkout" in md
    assert "_make_key" not in md


def test_property_description_has_anchor_and_cross_ref(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert '<a id="property-idle_timeout"></a>' in md
    assert '<a id="property-max_connections_per_host"></a>' in md


def test_method_description_has_anchor(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert '<a id="method-close"></a>' in md
    assert '<a id="method-prune"></a>' in md
    assert "[`idle_timeout`](#property-idle_timeout)" in md


def test_enum_rendering_with_anchors(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.RequestError"], registry)

    assert "## Constants" in md
    assert "### enum `Kind`" in md
    assert '<a id="enum-Kind"></a>' in md
    assert '<a id="enum-Kind-TRANSPORT"></a>' in md
    assert "`TRANSPORT`" in md
    assert "`0`" in md


def test_standalone_constant_rendering(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http"], registry)

    assert "## Constants" in md
    assert '<a id="constant-VERSION"></a>' in md
    assert "VERSION" in md


def test_method_signature_includes_param_types(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http"], registry)

    assert "func request(" in md


def test_method_signature_wraps_multiple_params_one_per_line(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http"], registry)

    string_link = (
        '<a href="https://docs.godotengine.org/en/stable/classes/class_string.html">'
        "String</a>"
    )
    assert f"    url: {string_link},\n" in md
    assert md.count("<code>") == md.count("</code>")


def test_method_signature_single_param_stays_on_one_line(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert "func checkout(key: " in md
    assert "func checkout(\n" not in md


def test_method_signature_no_params(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Session"], registry)

    assert "func close() -> void:" in md


def test_member_enum_type_links_to_enum_anchor(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.RequestError"], registry)

    assert "[`Kind`](#enum-Kind)" in md


def test_return_type_referencing_private_class_is_not_linked(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    md = render_class_markdown(registry["C3Http.Mock"], registry)

    assert "`C3Http._Stub`" in md
    assert "[`C3Http._Stub`](C3Http._Stub.md)" not in md
