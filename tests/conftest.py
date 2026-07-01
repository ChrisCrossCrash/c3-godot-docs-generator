from pathlib import Path

import pytest

FIXTURES_XML_DIR = Path(__file__).parent / "fixtures" / "xml"


@pytest.fixture
def fixtures_xml_dir() -> Path:
    return FIXTURES_XML_DIR
