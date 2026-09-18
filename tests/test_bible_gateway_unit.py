from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from bs4 import BeautifulSoup

from bible_translations.translations.asv import ASV
from bible_translations.translations.kjv import KJV
from bible_translations.translations.web import WEB

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "bible_gateway"


def _load_fixture(name: str) -> BeautifulSoup:
    html = (FIXTURES_DIR / name).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


def _marker_strings(soup: BeautifulSoup) -> set[str]:
    """The literal "[a]" / "(A)" strings BibleGateway renders for footnotes and cross-references."""
    return {sup.get_text(strip=True) for sup in soup.select("sup.footnote, sup.crossreference")}


def _patched_fetch(soup: BeautifulSoup):
    return patch(
        "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
        new=AsyncMock(return_value=soup),
    )


@pytest.mark.asyncio
async def test_aget_chapter_strips_footnote_markers():
    fixture_soup = _load_fixture("asv_john_3.html")
    markers = _marker_strings(fixture_soup)
    assert fixture_soup.select("sup.footnote"), "fixture must contain footnote markers for this test to mean anything"
    with _patched_fetch(fixture_soup):
        chapter = await ASV().aget_chapter("John", 3)
    for verse in chapter.verses:
        leaked = [m for m in markers if m in verse.text]
        assert not leaked, f"John 3:{verse.number}: {leaked} in {verse.text!r}"


@pytest.mark.asyncio
async def test_aget_chapter_strips_cross_reference_markers():
    fixture_soup = _load_fixture("web_romans_3.html")
    markers = _marker_strings(fixture_soup)
    assert fixture_soup.select("sup.crossreference"), "fixture must contain cross-reference markers"
    with _patched_fetch(fixture_soup):
        chapter = await WEB().aget_chapter("Romans", 3)
    assert [v.number for v in chapter.verses] == list(range(1, 32))
    for verse in chapter.verses:
        leaked = [m for m in markers if m in verse.text]
        assert not leaked, f"Romans 3:{verse.number}: {leaked} in {verse.text!r}"


@pytest.mark.asyncio
async def test_aget_verse_strips_markers_and_keeps_scripture():
    html = (
        '<div class="version-KJV result-text-style-normal text-html"><p>'
        '<span class="text John-3-16" id="en-KJV-26137">'
        '<sup class="versenum">16 </sup>For God so loved'
        "<sup class='footnote' data-fn='#fen-a'>[<a href='#fen-a'>a</a>]</sup> the world"
        "<sup class='crossreference' data-cr='#cen-A'>(<a href='#cen-A'>A</a>)</sup>, "
        'that he gave his <span class="small-caps">only</span> begotten Son. '
        "</span></p></div>"
    )
    with _patched_fetch(BeautifulSoup(html, "html.parser")):
        verse = await KJV().aget_verse("John", 3, 16)
    assert verse.number == 16
    assert verse.text == "For God so loved the world, that he gave his only begotten Son."


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
async def test_aget_chapter_parses_paragraph_style_markup_without_network():
    # ASV renders several verses per <p>, unlike KJV's one <p> per verse.
    asv = ASV()
    fixture_soup = _load_fixture("asv_john_3.html")
    with patch(
        "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
        new=AsyncMock(return_value=fixture_soup),
    ):
        chapter = await asv.aget_chapter("John", 3)
    assert [v.number for v in chapter.verses] == list(range(1, 37))
    assert chapter.verses[0].text.startswith("Now there was a man of the Pharisees")
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
