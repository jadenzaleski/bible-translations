# bible-translations

A Python package and CLI for fetching Bible translations on demand.

`bible-translations` does not ship any pre-downloaded Bible text. It scrapes
publicly available, public-domain translations from
[BibleGateway](https://www.biblegateway.com) at request time, and gives you
the result as Python objects (via the API) or as exported JSON files (via
the CLI).

## Install

```bash
pip install bible-translations
```

## Quickstart

### CLI

```bash
bt verse "John 3:16"
```

### API

```python
from bible_translations import get_translation

kjv = get_translation("KJV")
verse = kjv.get_verse("John", 3, 16)
print(verse.text)
```

See the [CLI Reference](cli.md) and [API Reference](api.md) for full details.
