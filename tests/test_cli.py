from pathlib import Path
from unittest.mock import AsyncMock, patch

from bs4 import BeautifulSoup
from click.testing import CliRunner

from bible_translations.cli import cli
from bible_translations.constants import VERSION

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "bible_gateway"


def test_bt_verse_exports_zip_end_to_end(tmp_path):
    """Run the real verse command with the network mocked; exercises the default Exporter path."""
    html = (FIXTURES_DIR / "kjv_john_3_16.html").read_text(encoding="utf-8")
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with patch(
            "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
            new=AsyncMock(return_value=BeautifulSoup(html, "html.parser")),
        ):
            result = runner.invoke(cli, ["verse", "John 3:16", "--output", "john_3_16", "--flat"])
        assert result.exit_code == 0, result.output
        assert Path("exports/john_3_16.zip").exists()


def test_bt():
    """Test that the CLI runs."""
    runner = CliRunner()
    result = runner.invoke(cli)  # type: ignore
    assert result.exit_code == 0
    assert VERSION in result.output


def test_bt_verse():
    """Test that the CLI verse runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verse", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_chapter():
    """Test that the CLI chapter runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["chapter", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_book():
    """Test that the CLI book runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["book", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_books():
    """Test that the CLI books runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["books", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_selection():
    """Test that the CLI selection runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["selection", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output
