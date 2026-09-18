from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class YLT(BibleGatewayTranslation):
    """Young's Literal Translation (1898) backed by BibleGateway scraping."""

    name = "Young's Literal Translation"
    abbreviation = "YLT"
    copyright = "Public Domain"
    url = "https://www.biblegateway.com"
