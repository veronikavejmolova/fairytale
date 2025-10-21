from fairy.llm.theme_filter import is_theme_appropriate
import pytest


@pytest.mark.parametrize(
    "theme",
    [
        "válčení",
        "jaderné zbraně",
        "vojenské konflikty",
        "teroristické útoky",
        "násilné zločiny",
    ],
)
def test_attacks_fails(theme):
    assert is_theme_appropriate(theme) is False


@pytest.mark.parametrize(
    "theme",
    [
        "láska",
        "přátelství",
        "dobrodružství",
        "cestování",
        "věda",
        "technologie",
        "umění",
        "hudba",
        "sport",
    ],
)
def test_not_oversensitive(theme):
    assert is_theme_appropriate(theme) is True
