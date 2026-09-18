import pytest
from click.testing import CliRunner

from bible_translations.cli import cli
from bible_translations.translations import TRANSLATIONS, get_translation
from bible_translations.translations.bible_gateway import BibleGatewayTranslation


def test_registry_keys_match_class_abbreviations():
    for abbreviation, translation_class in TRANSLATIONS.items():
        assert abbreviation == translation_class.abbreviation
        assert abbreviation == abbreviation.upper()


@pytest.mark.parametrize("abbreviation", sorted(TRANSLATIONS))
def test_registered_translation_has_complete_public_domain_metadata(abbreviation):
    translation = get_translation(abbreviation)
    assert isinstance(translation, BibleGatewayTranslation)
    assert translation.name
    assert translation.copyright == "Public Domain"
    assert translation.url == "https://www.biblegateway.com"
    assert translation.language == "English"
    assert translation._get_container_selector() == f"div.version-{abbreviation}.result-text-style-normal.text-html"


def test_get_translation_is_case_insensitive():
    assert get_translation("web").abbreviation == "WEB"
    assert get_translation("Darby").abbreviation == "DARBY"


def test_get_translation_unknown_lists_available():
    with pytest.raises(ValueError, match="Available translations: " + ", ".join(TRANSLATIONS)):
        get_translation("NOPE")


def test_cli_offers_every_registered_translation():
    result = CliRunner().invoke(cli, ["verse", "--help"])  # type: ignore
    assert result.exit_code == 0
    # Click renders case-insensitive Choice values in lowercase.
    for abbreviation in TRANSLATIONS:
        assert abbreviation.lower() in result.output.lower()
