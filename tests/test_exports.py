import json
import logging
import zipfile

import pytest

from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.models.verse import Verse
from bible_translations.translations.kjv import KJV
from bible_translations.utils.exporter import Exporter


def test_exporter_accepts_string_output_dir(tmp_path):
    # The CLI relies on the default (string) output_dir, which must be coerced to a Path.
    exporter = Exporter(output_dir=str(tmp_path / "out"))
    assert exporter.output_dir == tmp_path / "out"
    assert exporter.output_dir.is_dir()


def test_export_flat_json(tmp_path):
    info = Info(translation="King James Version", abbreviation="KJV", language="English", copyright="Public Domain")
    book = Book(
        name="John",
        chapters=[Chapter(number=3, verses=[Verse(number=16, text="For God so loved...")])],
        info=info,
    )
    exporter = Exporter(output_dir=tmp_path)

    zip_path = exporter.export([book], flat=True)

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        assert "kjv_flat.json" in names
        assert "kjv_info.json" in names
        with z.open("kjv_flat.json") as f:
            data = json.load(f)
        assert data == [
            {
                "translation": "King James Version",
                "abbreviation": "KJV",
                "book": "John",
                "chapter": 3,
                "verse": 16,
                "text": "For God so loved...",
                "heading": None,
                "superscription": None,
                "footnotes": None,
            }
        ]


@pytest.mark.live
@pytest.mark.asyncio
async def test_export_single_verse(tmp_path):
    kjv = KJV()
    verse = await kjv.aget_verse("John", 3, 16)
    chapter = Chapter(3, [verse])
    book = Book("John", [chapter], kjv.getInfo())
    exporter = Exporter(output_dir=tmp_path)

    zip_path = exporter.export([book])

    assert zip_path.exists()
    assert zip_path.suffix == ".zip"

    with zipfile.ZipFile(zip_path) as z:
        logging.basicConfig(level=logging.DEBUG, force=True)
        names = z.namelist()
        print(names)

        assert "books/john.json" in names
        assert "kjv_info.json" in names
        assert "kjv.json" in names
