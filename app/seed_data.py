"""Master catalog of Lost Ark classes/subclasses known to the app.

Used both to seed an empty database on first run and as the source list
for the "Add Class" picker (only classes not already present are offered,
so there's never a duplicate). This list is intentionally NOT editable
from the UI: when a new class is released in-game, the app itself needs
to be updated (add the name here) and re-released.
"""

ALL_CLASSES = [
    # Warrior
    "Berserker", "Gunlancer", "Paladin", "Slayer", "Destroyer", "Breaker",
    # Martial Artist
    "Wardancer", "Scrapper", "Soulfist", "Glaivier", "Striker",
    # Gunner
    "Gunslinger", "Sharpshooter", "Deadeye", "Artillerist", "Machinist",
    # Assassin
    "Shadowhunter", "Deathblade", "Souleater",
    # Specialist / Mage
    "Bard", "Sorceress", "Artist", "Aeromancer",
    # Added, detected from lostark.bible (archetype not verified)
    "Valkyrie", "Wildsoul", "Guardianknight", "Reaper", "Arcanist", "Summoner",
]
