"""Live smoke tests run against every registered translation.

Deliberately light (one verse + one chapter each) to keep BibleGateway load per CI run low;
deeper per-translation coverage lives in the fixture-based unit tests and in test_kjv.py.
"""

import pytest

from bible_translations.translations import TRANSLATIONS, get_translation
from bible_translations.utils.fetch.bible_gateway import BibleGatewayClient


@pytest.mark.live
@pytest.mark.asyncio
@pytest.mark.parametrize("abbreviation", sorted(TRANSLATIONS))
async def test_verse_and_chapter_round_trip(abbreviation):
    translation = get_translation(abbreviation)
    async with BibleGatewayClient() as client:
        raw = await client.fetch(f"John+3&version={abbreviation}")
        verse = await translation.aget_verse("John", 3, 16, client=client)
        chapter = await translation.aget_chapter("John", 3, client=client)

    # Footnote ("[a]") and cross-reference ("(A)") markers present in the raw markup must not survive.
    container = raw.select_one(translation._get_container_selector())
    markers = {sup.get_text(strip=True) for sup in container.select("sup.footnote, sup.crossreference")}

    assert verse.number == 16
    assert verse.text and verse.text == verse.text.strip()

    assert chapter.number == 3
    assert [v.number for v in chapter.verses] == list(range(1, 37))
    assert chapter.verses[15].text.split()[:3] == verse.text.split()[:3]
    for v in chapter.verses:
        assert v.text
        leaked = [m for m in markers if m in v.text]
        assert not leaked, f"markers {leaked} leaked into {abbreviation} John 3:{v.number}: {v.text!r}"
