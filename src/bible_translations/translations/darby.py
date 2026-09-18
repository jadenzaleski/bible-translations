from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class DARBY(BibleGatewayTranslation):
    """Darby Translation (1890) backed by BibleGateway scraping."""

    name = "Darby Translation"
    abbreviation = "DARBY"
    copyright = "Public Domain"
    url = "https://www.biblegateway.com"
