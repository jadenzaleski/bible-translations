import bible_translations as bt

EXPECTED_PUBLIC_NAMES = {
    "__version__",
    "Book",
    "BookNotFoundError",
    "Chapter",
    "ChapterNotFoundError",
    "Exporter",
    "FlatVerse",
    "Info",
    "SelectionInvalidError",
    "TRANSLATIONS",
    "Translation",
    "Verse",
    "VerseNotFoundError",
    "flatten_books",
    "get_translation",
}


def test_public_api_exports_expected_names():
    assert EXPECTED_PUBLIC_NAMES.issubset(set(dir(bt)))
    assert set(bt.__all__) == EXPECTED_PUBLIC_NAMES


def test_public_api_get_translation_returns_kjv_instance():
    kjv = bt.get_translation("KJV")
    assert kjv.abbreviation == "KJV"
    assert isinstance(kjv, bt.Translation)


def test_public_api_flatten_books_is_reachable():
    book = bt.Book(name="Genesis", chapters=[bt.Chapter(number=1, verses=[bt.Verse(number=1, text="x")])])
    flat = bt.flatten_books([book])
    assert len(flat) == 1
    assert isinstance(flat[0], bt.FlatVerse)
