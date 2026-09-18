from .asv import ASV
from .darby import DARBY
from .dra import DRA
from .kjv import KJV
from .web import WEB
from .ylt import YLT

TRANSLATIONS = {
    "KJV": KJV,
    "ASV": ASV,
    "WEB": WEB,
    "YLT": YLT,
    "DARBY": DARBY,
    "DRA": DRA,
}


def get_translation(abbreviation: str):
    """
    Get a translation class by its abbreviation.

    :param abbreviation: The translation abbreviation (e.g., "KJV").
    :return: The translation class.
    :raises ValueError: If the translation is not found.
    """
    translation_class = TRANSLATIONS.get(abbreviation.upper())
    if not translation_class:
        raise ValueError(
            f"Translation not found: {abbreviation}. Available translations: {', '.join(TRANSLATIONS.keys())}"
        )
    return translation_class()
