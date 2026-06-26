APP_TITLE = "Uchaguzi wa Maoni ya Umma"
SUBTITLE = "Mfumo wa Usimamizi wa Wakala wa Forodha Tanzania"
POLL_QUESTION = "Je, unaunga mkono mfumo wa TCAMS?"

LABEL_NAME = "Jina"
LABEL_GENDER = "Jinsia"
LABEL_REGION = "Mkoa"
LABEL_STATION = "Kituo cha Forodha"
LABEL_REASON = "Sababu (kwa nini unasaidia au hupingi mfumo?)"
PLACEHOLDER_NAME = "Andika jina lako kamili"
PLACEHOLDER_REGION = "Andika ili kutafuta mkoa..."
PLACEHOLDER_STATION = "Andika ili kutafuta kituo cha forodha..."
PLACEHOLDER_REASON = "Eleza sababu yako hapa..."

GENDER_MALE = "Mwanaume"
GENDER_FEMALE = "Mwanamke"
GENDER_OPTIONS = [
    {"label": GENDER_MALE, "value": "Male"},
    {"label": GENDER_FEMALE, "value": "Female"},
]

BTN_YES = "Piga Kura NDIYO"
BTN_NO = "Piga Kura HAPANA"
BTN_NOT_SURE = "Piga Kura SIJUI"

TIMER_LABEL = "Muda uliobaki"
TOTAL_VOTES = "Jumla ya Kura"
TALLY_YES = "NDIYO"
TALLY_NO = "HAPANA"
TALLY_NOT_SURE = "SIJUI"

ANALYTICS_TITLE = "Takwimu za Uchaguzi"
TOTAL_VOTERS = "Jumla ya Wapiga Kura"
GENDER_DIST = "Usambazaji wa Jinsia"
TOP_REGION = "Mkoa Ulioongoza"
TOP_STATION = "Kituo cha Forodha Kilichoongoza"
GENDER_YES_NO = "Asilimia ya Jinsia: Ndiyo vs Hapana"
SENTIMENT = "Hali ya Maoni kwa Sasa"

SENTIMENT_NO_VOTES = "Hakuna kura bado."
SENTIMENT_YES_LEADS = "Ndiyo ni mingi — wengi wanaunga mkono TCAMS ({pct}% Ndiyo)."
SENTIMENT_NO_LEADS = "Hapana ni mingi — wengi hawapingi mfumo wa TCAMS ({pct}% Hapana)."
SENTIMENT_UNSURE_LEADS = "Sijui ni mingi — wengi hawajaamua bado ({pct}% Sijui)."
SENTIMENT_THREE_WAY_TIE = (
    "Maoni yanasawana kabisa — Ndiyo, Hapana na Sijui zina kura sawa ({pct}% kila moja)."
)
SENTIMENT_TWO_WAY_TIE = "Maoni yanasawana kati ya {a} na {b} ({pct}% kila moja)."

POLL_PENDING = "Uchaguzi haujaanza bado."
POLL_CLOSED = "Uchaguzi umefungwa. Asante kwa kushiriki!"
VOTE_SUCCESS = "Asante! Kura yako imehesabiwa."


def vote_success_message(voter_name: str) -> str:
    name = voter_name.strip()
    if not name:
        return VOTE_SUCCESS
    return f"Asante {name}! Kura yako imehesabiwa."
VOTE_ERROR = "Imeshindikana kupokea kura. Jaribu tena."
VALIDATION_ERROR = "Tafadhali jaza sehemu zote zinazohitajika."

MALE_LABEL = "Wanaume"
FEMALE_LABEL = "Wanawake"
