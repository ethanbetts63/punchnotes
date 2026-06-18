from pipeline.utils.generate.ep_meta import parse_guests_from_title


def test_parse_guests_from_dash_title_with_commas_and_ampersand():
    assert parse_guests_from_title(
        "Kill Tony #190 - Doug Benson, Big Jay Oakerson & Dom Irrera"
    ) == ["Doug Benson", "Big Jay Oakerson", "Dom Irrera"]


def test_parse_guests_from_parenthetical_early_title():
    assert parse_guests_from_title(
        "Kill Tony #17 (Jamar Neighbors, Mat Edgar)"
    ) == ["Jamar Neighbors", "Mat Edgar"]


def test_parse_guests_ignores_location_parenthetical_before_dash():
    assert parse_guests_from_title(
        "KT #761 (HOUSTON) - ADAM RAY + KIM CONGDON"
    ) == ["Adam Ray", "Kim Congdon"]
