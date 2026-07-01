from c3_godot_docs_gen.bbcode import bbcode_to_markdown
from c3_godot_docs_gen.parse import parse_registry


def md(text, current_class="C3Http.Session", registry=None):
    return bbcode_to_markdown(text, current_class, registry or {})


def test_bold_and_italic():
    assert md("[b]bold[/b]") == "**bold**"
    assert md("[i]italic[/i]") == "*italic*"


def test_underline_uses_html_tag():
    assert md("[u]word[/u]") == "<u>word</u>"


def test_inline_code():
    assert md("[code]x == y[/code]") == "`x == y`"


def test_codeblock_becomes_fenced_gdscript_block():
    text = "[codeblock]\nvar x := 1\nprint(x)\n[/codeblock]"
    result = md(text)
    assert "```gdscript" in result
    assert "var x := 1" in result
    assert "print(x)" in result
    assert result.strip().endswith("```")


def test_codeblock_dedents_relative_to_tag():
    text = "[codeblock]\n\tvar x := 1\n\tif x:\n\t\tprint(x)\n[/codeblock]"
    result = md(text)
    lines = result.splitlines()
    code_lines = [line for line in lines if line and not line.startswith("```")]
    assert "var x := 1" in code_lines
    assert "    print(x)" in code_lines


def test_br_creates_paragraph_break():
    assert md("a[br]b") == "a\n\nb"


def test_single_newline_becomes_paragraph_break():
    assert md("a\nb") == "a\n\nb"


def test_url_with_title():
    assert (
        md("[url=https://example.com]click here[/url]")
        == "[click here](https://example.com)"
    )


def test_bare_url():
    assert (
        md("[url]https://example.com[/url]")
        == "[https://example.com](https://example.com)"
    )


def test_lb_rb_literal_brackets():
    assert md("[lb]code[rb]") == "[code]"


def test_kbd_inline_code():
    assert md("[kbd]Ctrl+C[/kbd]") == "`Ctrl+C`"


def test_param_inline_code():
    assert md("[param url]") == "`url`"


def test_bare_class_ref_links_to_known_class(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    result = md(
        "Create a [C3Http.Options]", current_class="C3Http.Session", registry=registry
    )
    assert result == "Create a [`C3Http.Options`](C3Http.Options.md)"


def test_bare_class_ref_to_current_class_is_bold(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    result = md(
        "This is a [C3Http.Session]", current_class="C3Http.Session", registry=registry
    )
    assert result == "This is a **C3Http.Session**"


def test_member_ref(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    result = md(
        "See [member C3Http.Options.session]",
        current_class="C3Http.Session",
        registry=registry,
    )
    assert result == "See [`session`](C3Http.Options.md#property-session)"


def test_method_ref(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    result = md(
        "Call [method C3Http.request]",
        current_class="C3Http.Session",
        registry=registry,
    )
    assert result == "Call [`request()`](C3Http.md#method-request)"


def test_enum_ref(fixtures_xml_dir):
    registry = parse_registry(fixtures_xml_dir)
    result = md(
        "a [enum C3Http.RequestError.Kind] value",
        current_class="C3Http.Response",
        registry=registry,
    )
    assert result == "a [`Kind`](C3Http.RequestError.md#enum-Kind) value"


def test_signal_ref(fixtures_xml_dir):
    registry = {}
    result = md("[signal foo]", current_class="C3Http", registry=registry)
    assert result == "`foo`"
