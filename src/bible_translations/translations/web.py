from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class WEB(BibleGatewayTranslation):
    """World English Bible backed by BibleGateway scraping."""

    name = "World English Bible"
    abbreviation = "WEB"
    copyright = "Public Domain"
    url = "https://www.biblegateway.com"
