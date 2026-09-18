from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class ASV(BibleGatewayTranslation):
    """
    American Standard Version (1901) backed by BibleGateway scraping.

    Inherits all retrieval methods from BibleGatewayTranslation so that the
    scraping logic is shared across translations.
    """

    name = "American Standard Version"
    abbreviation = "ASV"
    copyright = "Public Domain"
    url = "https://www.biblegateway.com"
