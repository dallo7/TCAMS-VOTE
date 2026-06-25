import random

FIRST_NAMES_MALE = [
    "Ramadhani", "Juma", "Hemedi", "Nestory", "Castory", "Richard", "Lucas", "Fabian",
    "George", "Filbert", "Abdallah", "Issa", "John", "Erick", "Peter", "Ally", "Elia",
    "Emmanuel", "Godfrey", "Renatus", "Gervas", "Mathayo", "Deogratias", "Masunga",
    "Selemani", "Constantine", "Baraka", "Gabriel", "Lameck", "Marko", "Yohana",
]

FIRST_NAMES_FEMALE = [
    "Amina", "Shufaa", "Latifa", "Gloria", "Tatu", "Mwanaidi", "Rukia", "Tunu",
    "Mwanaharusi", "Zawadi", "Editruda", "Esther", "Hadija", "Catherine",
]

LAST_NAMES = [
    "Macha", "Haule", "Tarimo", "Mfaume", "Kibwana", "Minja", "Athumani", "Paul",
    "Kulwa", "Bhoke", "Kihwele", "Lyimo", "Kassim", "Daniel", "Mayala", "Komba",
    "Chacha", "Mwasanguti", "Ngonyani", "Range", "Magige", "Lucas", "Mwinyi",
    "Mmari", "Ndaki", "Mosha", "Rwechungura", "Mlowe", "Rweyemamu", "Chande",
    "Lazaro", "Daniel", "Mohamed", "Mtumwa", "Mgaya", "Nassoro", "Mhagama", "Wambura",
]


def generate_swahili_name() -> tuple[str, str]:
    if random.random() < 0.45:
        first = random.choice(FIRST_NAMES_FEMALE)
        gender = "Female"
    else:
        first = random.choice(FIRST_NAMES_MALE)
        gender = "Male"
    last = random.choice(LAST_NAMES)
    return f"{first} {last}", gender
