from c3_godot_docs_gen.parse import parse_class_file, parse_registry


def test_parse_class_basics(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.Session.xml")

    assert class_def.name == "C3Http.Session"
    assert class_def.inherits == "RefCounted"
    assert "pool of idle HTTP connections" in class_def.brief_description
    assert "[C3Http.Session]" in class_def.description


def test_parse_members_with_type_default_and_private(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.Session.xml")

    max_conn = class_def.properties["max_connections_per_host"]
    assert max_conn.type_name.type_name == "int"
    assert max_conn.default_value == "6"
    assert not max_conn.is_private

    pool = class_def.properties["_pool"]
    assert pool.is_private


def test_parse_member_with_enum_attribute(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.RequestError.xml")

    kind = class_def.properties["kind"]
    assert kind.type_name.type_name == "int"
    assert kind.type_name.enum == "C3Http.RequestError.Kind"


def test_parse_methods_with_params_and_static_qualifier(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.xml")

    request = class_def.find_method("request")
    assert request is not None
    assert request.is_static
    assert request.return_type.type_name == "C3Http.Response"

    params = request.parameters
    assert [p.name for p in params] == [
        "url",
        "custom_headers",
        "method",
        "request_data",
        "options",
    ]
    method_param = next(p for p in params if p.name == "method")
    assert method_param.type_name.enum == "HTTPClient.Method"
    assert method_param.default_value == "0"


def test_parse_method_default_return_type_void(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.CancellationToken.xml")

    cancel = class_def.find_method("cancel")
    assert cancel.return_type.type_name == "void"


def test_parse_constants_grouped_into_enums(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.RequestError.xml")

    assert class_def.constants == []
    assert "Kind" in class_def.enums
    kind_enum = class_def.enums["Kind"]
    assert not kind_enum.is_bitfield
    assert list(kind_enum.values.keys()) == [
        "TRANSPORT",
        "HTTP",
        "CLIENT",
        "CANCELLED",
        "TIMEOUT",
        "BODY_SIZE_LIMIT_EXCEEDED",
    ]
    assert kind_enum.values["TRANSPORT"].value == "0"


def test_parse_standalone_constants(fixtures_xml_dir):
    class_def = parse_class_file(fixtures_xml_dir / "C3Http.xml")

    assert class_def.enums == {}
    assert len(class_def.constants) == 1
    assert class_def.constants[0].name == "VERSION"


def test_private_class_detection(fixtures_xml_dir):
    impl = parse_class_file(fixtures_xml_dir / "C3Http._Impl.xml")
    assert impl.is_private

    nested_private = parse_class_file(fixtures_xml_dir / "C3Http._Impl._ParsedURL.xml")
    assert nested_private.is_private

    session_pool_entry = parse_class_file(
        fixtures_xml_dir / "C3Http.Session._PoolEntry.xml"
    )
    assert session_pool_entry.is_private

    session = parse_class_file(fixtures_xml_dir / "C3Http.Session.xml")
    assert not session.is_private


def test_parse_registry_builds_name_to_classdef_map(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)

    assert set(registry) == {
        "C3Http",
        "C3Http.CancellationToken",
        "C3Http.Mock",
        "C3Http.Options",
        "C3Http.RequestError",
        "C3Http.Response",
        "C3Http.Session",
        "C3Http.Session._PoolEntry",
        "C3Http._Impl",
        "C3Http._Impl._ParsedURL",
        "C3Http._Stub",
    }
    assert registry["C3Http.Session"].name == "C3Http.Session"
