"""bible_translations: fetch and export Bible translations on demand.

This package does not bundle any Bible text. Translations are scraped from
BibleGateway at request time, via either the `bt` / `bible-translations` CLI
or this Python API.
"""

from bible_translations.constants import VERSION as __version__
from bible_translations.exceptions import (
    BookNotFoundError,
    ChapterNotFoundError,
    SelectionInvalidError,
    VerseNotFoundError,
)
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.models.verse import Verse
from bible_translations.translations import TRANSLATIONS, get_translation
from bible_translations.translations.base import Translation
from bible_translations.utils.exporter import Exporter
from bible_translations.utils.flatten import FlatVerse, flatten_books

__all__ = [
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
]
