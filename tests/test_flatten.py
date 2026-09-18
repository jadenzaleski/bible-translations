from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.models.verse import Verse
from bible_translations.utils.flatten import FlatVerse, flatten_books


def _make_book() -> Book:
    info = Info(translation="King James Version", abbreviation="KJV", language="English", copyright="Public Domain")
    verses_ch1 = [Verse(number=1, text="In the beginning..."), Verse(number=2, text="And the earth was...")]
    verses_ch2 = [Verse(number=1, text="Thus the heavens...")]
    return Book(
        name="Genesis",
        chapters=[Chapter(number=1, verses=verses_ch1), Chapter(number=2, verses=verses_ch2)],
        info=info,
    )


def test_flatten_books_produces_one_record_per_verse():
    flat = flatten_books([_make_book()])
    assert len(flat) == 3
    assert all(isinstance(r, FlatVerse) for r in flat)


def test_flatten_books_preserves_reference_and_text():
    flat = flatten_books([_make_book()])
    first = flat[0]
    assert first.translation == "King James Version"
    assert first.abbreviation == "KJV"
    assert first.book == "Genesis"
    assert first.chapter == 1
    assert first.verse == 1
    assert first.text == "In the beginning..."


def test_flatten_books_handles_missing_info():
    book = Book(name="Genesis", chapters=[Chapter(number=1, verses=[Verse(number=1, text="x")])], info=None)
    flat = flatten_books([book])
    assert flat[0].translation == ""
    assert flat[0].abbreviation == ""
