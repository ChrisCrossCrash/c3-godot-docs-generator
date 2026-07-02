from c3_godot_docs_gen.model import ClassDef


def _class_def(name: str) -> ClassDef:
    return ClassDef(
        name=name,
        inherits=None,
        brief_description="",
        description="",
    )


def test_underscore_prefixed_class_is_private():
    assert _class_def("_Impl").is_private
    assert _class_def("C3Http._Impl").is_private


def test_normal_class_name_is_public():
    assert not _class_def("C3Http.Session").is_private


def test_quoted_resource_path_class_is_private():
    # Godot's doctool falls back to the script's quoted resource path as the
    # "class name" for scripts with no `class_name` declaration (common in GUT).
    assert _class_def('"addons/gut/GutScene.gd"').is_private


def test_quoted_resource_path_nested_class_is_private():
    assert _class_def('"addons/gut/awaiter.gd".AwaitLogger').is_private
