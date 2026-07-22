"""Disney IP and sub-franchise title matching for catalog grouping."""

from __future__ import annotations

# (franchise label, title/collection keywords) — checked after major brand keywords.
# Within each group, longer keywords should appear first for greedy matching.
IP_FRANCHISE_GROUPS: list[tuple[str, tuple[str, ...]]] = [
    (
        "Pirates of the Caribbean",
        (
            "pirates of the caribbean",
            "dead men tell no tales",
            "on stranger tides",
            "at world's end",
            "dead man's chest",
            "curse of the black pearl",
        ),
    ),
    (
        "Indiana Jones",
        (
            "indiana jones",
            "raiders of the lost ark",
            "temple of doom",
            "last crusade",
            "kingdom of the crystal skull",
            "dial of destiny",
        ),
    ),
    (
        "National Treasure",
        ("national treasure", "book of secrets"),
    ),
    (
        "The Chronicles of Narnia",
        ("chronicles of narnia", "narnia"),
    ),
    (
        "Winnie the Pooh",
        ("winnie the pooh", "pooh's", "pooh and", "the tigger movie", "piglet's"),
    ),
    (
        "Muppets",
        ("muppets", "muppet"),
    ),
    (
        "101 Dalmatians",
        ("101 dalmatian", "102 dalmatians", "dalmatian street"),
    ),
    (
        "Lilo & Stitch",
        ("lilo & stitch", "lilo and stitch", "stitch! the", "stitch the"),
    ),
    (
        "Alice in Wonderland",
        ("alice in wonderland", "alice through the looking", "alice's wonderland"),
    ),
    (
        "The Jungle Book",
        ("jungle book", "jungle cruise", "jungle 2 jungle"),
    ),
    (
        "Princess Stories",
        (
            "snow white",
            "cinderella",
            "sleeping beauty",
            "little mermaid",
            "beauty and the beast",
            "princess diaries",
            "princess and the frog",
            "tangled",
            "princess protection program",
        ),
    ),
    (
        "Mickey & Friends",
        (
            "mickey mouse",
            "mickey's",
            "mickey and",
            "donald duck",
            "goofy",
            "goof troop",
            "a goofy movie",
            "an extremely goofy",
            "minnie",
            "pluto's",
        ),
    ),
    (
        "Chip 'n Dale",
        ("chip 'n' dale", "chip n dale", "chip and dale", "chip 'n dale"),
    ),
    (
        "DuckTales",
        ("ducktales", "duck tales", "darkwing duck", "tailspin", "tale spin"),
    ),
    (
        "Phineas and Ferb",
        ("phineas and ferb", "milos from mars"),
    ),
    (
        "Gravity Falls",
        ("gravity falls",),
    ),
    (
        "Kim Possible",
        ("kim possible",),
    ),
    (
        "High School Musical",
        ("high school musical",),
    ),
    (
        "Descendants",
        ("descendants",),
    ),
    (
        "Percy Jackson",
        ("percy jackson",),
    ),
    (
        "Hannah Montana",
        ("hannah montana",),
    ),
    (
        "The Suite Life",
        ("suite life",),
    ),
    (
        "Wizards of Waverly Place",
        ("waverly place", "wizards of waverly"),
    ),
    (
        "Camp Rock",
        ("camp rock",),
    ),
    (
        "The Cheetah Girls",
        ("cheetah girls",),
    ),
    (
        "Air Bud",
        ("air bud",),
    ),
    (
        "Homeward Bound",
        ("homeward bound",),
    ),
    (
        "The Parent Trap",
        ("parent trap",),
    ),
    (
        "Freaky Friday",
        ("freaky friday",),
    ),
    (
        "Tarzan",
        ("tarzan",),
    ),
    (
        "Hercules",
        ("hercules",),
    ),
    (
        "Atlantis",
        ("atlantis",),
    ),
    (
        "Treasure Planet",
        ("treasure planet",),
    ),
    (
        "Brother Bear",
        ("brother bear",),
    ),
    (
        "Classic Disney Animation",
        (
            "bambi",
            "dumbo",
            "pinocchio",
            "peter pan",
            "lady and the tramp",
            "fox and the hound",
            "aristocats",
            "robin hood",
            "meet the robinsons",
            "home on the range",
            "chicken little",
            "the rescuers",
            "oliver & company",
            "oliver and company",
            "the great mouse detective",
            "the black cauldron",
            "the sword in the stone",
            "fun and fancy free",
            "make mine music",
            "melody time",
            "saludos amigos",
            "the three caballeros",
            "who framed roger rabbit",
            "the nightmare before christmas",
            "frankenweenie",
            "the brave little toaster",
        ),
    ),
    (
        "Doc McStuffins",
        ("doc mcstuffins",),
    ),
    (
        "Sofia the First",
        ("sofia the first",),
    ),
    (
        "Elena of Avalor",
        ("elena of avalor",),
    ),
    (
        "Vampirina",
        ("vampirina",),
    ),
    (
        "The Lion Guard",
        ("lion guard",),
    ),
    (
        "Amphibia",
        ("amphibia",),
    ),
    (
        "The Owl House",
        ("owl house",),
    ),
    (
        "20th Century Studios",
        (
            "avatar",
            "alien",
            "predator",
            "die hard",
            "home alone",
            "ice age",
            "rio ",
            "ferdinand",
            "boss baby",
            "night at the museum",
            "diary of a wimpy kid",
            "the simpsons",
            "family guy",
            "futurama",
            "bobs burgers",
            "american dad",
            "king of the hill",
            "9-1-1",
            "grey's anatomy",
            "greys anatomy",
            "modern family",
            "black-ish",
            "blackish",
            "american horror story",
            "alias",
            "lost",
            "desperate housewives",
            "scrubs",
            "how i met your mother",
            "fresh off the boat",
            "once upon a time",
            "criminal minds",
            "bones",
            "castle",
            "naruto",
            "full house",
            "home improvement",
            "boy meets world",
            "power rangers",
            "anastasia",
            "the book of life",
            "spies in disguise",
        ),
    ),
    (
        "Disney Channel",
        (
            "disney channel",
            "ant farm",
            "a.n.t. farm",
            "alex & co",
            "bunk'd",
            "bunkd",
            "jessie",
            "good luck charlie",
            "liv and maddie",
            "shake it up",
            "kc undercover",
            "stuck in the middle",
            "bizaardvark",
            "andi mack",
            "raven's home",
            "sydney to the max",
            "big city greens",
            "miraculous",
            "ladybug",
        ),
    ),
    (
        "Bluey",
        ("bluey",),
    ),
]


def match_ip_franchise(haystack: str) -> str | None:
    """Return the first matching IP franchise label, or None."""
    text = haystack.lower()
    for name, keywords in IP_FRANCHISE_GROUPS:
        for keyword in sorted(keywords, key=len, reverse=True):
            if keyword in text:
                return name
    return None
