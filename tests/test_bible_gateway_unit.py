from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from bs4 import BeautifulSoup

from bible_translations.translations.kjv import KJV

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "bible_gateway"


def _load_fixture(name: str) -> BeautifulSoup:
    html = (FIXTURES_DIR / name).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


@pytest.mark.asyncio
async def test_aget_chapter_parses_fixture_without_network():
    kjv = KJV()
    fixture_soup = _load_fixture("kjv_john_3.html")
    with patch(
        "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
        new=AsyncMock(return_value=fixture_soup),
    ):
        chapter = await kjv.aget_chapter("John", 3)
    assert chapter.number == 3
    assert len(chapter.verses) == 36
    assert chapter.verses[15].number == 16
    assert chapter.verses[15].text.startswith("For God so loved the world")


@pytest.mark.asyncio
async def test_aget_verse_parses_fixture_without_network():
    kjv = KJV()
    fixture_soup = _load_fixture("kjv_john_3_16.html")
    with patch(
        "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
        new=AsyncMock(return_value=fixture_soup),
    ):
        verse = await kjv.aget_verse("John", 3, 16)
    assert verse.number == 16
    assert verse.text == (
        "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not"
        " perish, but have everlasting life."
    )
