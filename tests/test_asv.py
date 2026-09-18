import pytest

from bible_translations.translations.asv import ASV


@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_verse_john_3_16():
    asv = ASV()
    verse = await asv.aget_verse(book_name="John", chapter_number=3, verse_number=16)
    # https://www.biblegateway.com/passage/?search=John%203%3A16&version=ASV
    assert verse.number == 16
    assert "For God so loved the world" in verse.text


@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_chapter_john_3():
    asv = ASV()
    chapter = await asv.aget_chapter(book_name="John", chapter_number=3)
    assert chapter.number == 3
    assert chapter.verses[15].number == 16


@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_book_john():
    asv = ASV()
    book = await asv.aget_book(name="John")
    assert len(book.chapters) == 21
    assert book.chapters[0].verses[0].number == 1
