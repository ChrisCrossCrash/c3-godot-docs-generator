from c3_godot_docs_gen.cli import generate, main


def test_generate_writes_one_file_per_public_class(fixtures_xml_dir, tmp_path):
    generated = generate(fixtures_xml_dir, tmp_path)

    written = {p.name for p in tmp_path.glob("*.md")}
    assert "C3Http.Session.md" in written
    assert "C3Http.Options.md" in written
    assert "index.md" in written
    assert "C3Http.Session.md" in generated
    assert "index.md" in generated


def test_generate_excludes_private_classes(fixtures_xml_dir, tmp_path):
    generate(fixtures_xml_dir, tmp_path)

    written = {p.name for p in tmp_path.glob("*.md")}
    assert "C3Http._Impl.md" not in written
    assert "C3Http._Stub.md" not in written
    assert "C3Http.Session._PoolEntry.md" not in written
    assert "C3Http._Impl._ParsedURL.md" not in written


def test_index_lists_public_classes_only(fixtures_xml_dir, tmp_path):
    generate(fixtures_xml_dir, tmp_path)

    index_text = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "C3Http.Session" in index_text
    assert "C3Http.Options" in index_text
    assert "_Impl" not in index_text
    assert "_Stub" not in index_text


def test_dry_run_does_not_write_files(fixtures_xml_dir, tmp_path):
    generated = generate(fixtures_xml_dir, tmp_path, dry_run=True)

    assert list(tmp_path.glob("*.md")) == []
    assert "C3Http.Session.md" in generated


def test_main_returns_zero_and_writes_output(fixtures_xml_dir, tmp_path):
    exit_code = main([str(fixtures_xml_dir), "-o", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "C3Http.Session.md").exists()
