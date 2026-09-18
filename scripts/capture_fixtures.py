"""One-off script to (re)capture real BibleGateway HTML for offline unit tests.

Run manually whenever BibleGateway's markup changes and fixtures need refreshing:
    python scripts/capture_fixtures.py
"""

import asyncio
from pathlib import Path

from bible_translations.utils.fetch.bible_gateway import BibleGatewayClient

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "bible_gateway"

QUERIES = {
    "kjv_john_3.html": "John+3&version=KJV",
    "kjv_john_3_16.html": "John+3:16&version=KJV",
}


async def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    async with BibleGatewayClient() as client:
        for filename, query in QUERIES.items():
            soup = await client.fetch(query)
            (FIXTURES_DIR / filename).write_text(str(soup), encoding="utf-8")
            print(f"Wrote {filename}")


if __name__ == "__main__":
    asyncio.run(main())
