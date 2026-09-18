from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class DRA(BibleGatewayTranslation):
    """Douay-Rheims 1899 American Edition backed by BibleGateway scraping."""

    name = "Douay-Rheims 1899 American Edition"
    abbreviation = "DRA"
    copyright = "Public Domain"
    url = "https://www.biblegateway.com"
