from pipeline.models.comedian import APPEARANCE_ATTRIBUTES


KNOWN_GOLDEN_TICKET_SLUGS = frozenset(
    {
        "steve-lee",
        "enrique-chacon",
        "john-callaghan",
        "caroline-smith",
        "tristan-bowling",
        "todd-royce",
        "aloe-mean",
        "ryan-middendorf",
        "colt",
        "martin-malloy",
        "nicole-tran",
        "liam-o-brian",
        "martin-phillips",
        "jared-nathan",
        "aya-amarir",
        "gary-falcon",
        "ahren-belisle",
        "ric-diez",
        "heath-cordes",
        "carlos-lopez",
        "drew-nickens",
        "fiona-cauley",
        "jack-shaw",
        "jeremy",
        "collin-sledge",
        "kansei-yasuda",
        "charlie-mac",
        "timmy-no-brakes",
        "chris-silio",
        "jj-alexander",
        "mason-bird",
        "yaqiao-yang",
        "tony-scar",
        "angel-diaz",
        "orhun-timur",
        "randolph-davies",
        "pat-o-neill",
    }
)


KNOWN_REGULAR_SLUGS = frozenset(
    {
        "ari-matti",
        "casey-rocket",
        "david-lucas",
        "dedrick-flynn",
        "hans-kim",
        "kam-patterson",
        "kimberly-congdon",
        "sara-weinshenk",
        "vanessa-johnston",
        "william-montgomery",
        "malcolm-hatchett",
        "michael-lehrer",
    }
)


KNOWN_SPECIAL_SLUGS = frozenset(
    {
        "ron-white",
        "uncle-lazer",
        "ari-shaffir",
        "iron-patriot",
        "karen-feehan",
        "joe-derosa", 
        "james-mccann",
        "rob-schneider",
        "brian-holtzman",
        "ehsan-ahmad",
        "luis-j-gomez",
    }
)


KNOWN_COMEDIAN_OVERLAP = (
    (KNOWN_GOLDEN_TICKET_SLUGS & KNOWN_REGULAR_SLUGS)
    | (KNOWN_GOLDEN_TICKET_SLUGS & KNOWN_SPECIAL_SLUGS)
    | (KNOWN_REGULAR_SLUGS & KNOWN_SPECIAL_SLUGS)
)
if KNOWN_COMEDIAN_OVERLAP:
    names = ", ".join(sorted(KNOWN_COMEDIAN_OVERLAP))
    raise ValueError(f"Known comedian slugs cannot have multiple appearance types: {names}")


def normalize_known_appearance_attributes(slug: str, attributes: list[str] | None) -> list[str]:
    """Make appearance type authoritative from known slug lists."""
    values = attributes or []
    had_appearance_attribute = any(value in APPEARANCE_ATTRIBUTES for value in values)

    non_appearance_attributes = []
    seen = set()
    for value in values:
        if not value or value in APPEARANCE_ATTRIBUTES or value in seen:
            continue
        non_appearance_attributes.append(value)
        seen.add(value)

    if slug in KNOWN_REGULAR_SLUGS:
        appearance_attribute = "regular"
    elif slug in KNOWN_GOLDEN_TICKET_SLUGS:
        appearance_attribute = "golden_ticket"
    elif slug in KNOWN_SPECIAL_SLUGS:
        appearance_attribute = "special"
    elif had_appearance_attribute:
        appearance_attribute = "bucket_pull"
    else:
        appearance_attribute = None

    if appearance_attribute is None:
        return non_appearance_attributes
    return [appearance_attribute, *non_appearance_attributes]
