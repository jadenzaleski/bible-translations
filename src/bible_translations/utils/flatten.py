from dataclasses import dataclass

from bible_translations.models.book import Book


@dataclass
class FlatVerse:
    """A single verse flattened out of the nested Book/Chapter/Verse structure."""

    translation: str
    abbreviation: str
    book: str
    chapter: int
    verse: int
    text: str
    heading: str | None = None
    superscription: str | None = None
    footnotes: list[str] | None = None


def flatten_books(books: list[Book]) -> list[FlatVerse]:
    """
    Flatten a list of Book objects into a flat list of per-verse records.

    :param books: List of Book objects to flatten.
    :returns: list[FlatVerse]: One record per verse, in book/chapter/verse order.
    """
    flat: list[FlatVerse] = []
    for book in books:
        info = book.info
        translation = info.translation if info else ""
        abbreviation = info.abbreviation if info else ""
        for chapter in book.chapters:
            for verse in chapter.verses:
                flat.append(
                    FlatVerse(
                        translation=translation,
                        abbreviation=abbreviation,
                        book=book.name,
                        chapter=chapter.number,
                        verse=verse.number,
                        text=verse.text,
                        heading=verse.heading,
                        superscription=verse.superscription,
                        footnotes=verse.footnotes,
                    )
                )
    return flat
