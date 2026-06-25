"""Build live sentiment summary from vote tallies."""

from tcams.dash_app import i18n_sw as sw

_CHOICES = (
    ("yes", "Ndiyo"),
    ("no", "Hapana"),
    ("not_sure", "Sijui"),
)


def build_sentiment_message(counts: dict[str, int], percentages: dict[str, float]) -> str:
    total = counts["yes"] + counts["no"] + counts["not_sure"]
    if total == 0:
        return sw.SENTIMENT_NO_VOTES

    ranked = [(key, counts[key], percentages[key], label) for key, label in _CHOICES]
    peak = max(count for _, count, _, _ in ranked)
    leaders = [item for item in ranked if item[1] == peak]

    if len(leaders) == 3:
        pct = percentages["yes"]
        return sw.SENTIMENT_THREE_WAY_TIE.format(pct=pct)

    if len(leaders) == 2:
        a, b = leaders[0][3], leaders[1][3]
        pct = leaders[0][2]
        return sw.SENTIMENT_TWO_WAY_TIE.format(a=a, b=b, pct=pct)

    _, _, pct, label = leaders[0]
    key = leaders[0][0]
    if key == "yes":
        return sw.SENTIMENT_YES_LEADS.format(pct=pct)
    if key == "no":
        return sw.SENTIMENT_NO_LEADS.format(pct=pct)
    return sw.SENTIMENT_UNSURE_LEADS.format(pct=pct)
