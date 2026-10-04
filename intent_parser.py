"""
Rule-based intent detection + extraction for short shop commands.
Works offline, no LLM, no API. Handles English, Banglish and Bangla.

Examples:
    sales rahim to 500tk          -> sales, rahim, 500
    rahim ke 5 hajar becha        -> sales, rahim, 5000
    রহিম কে ৫০০ টাকা বিক্রি        -> sales, রহিম, 500
    kena karim theke 2.5k         -> purchase, karim, 2500
    ferot 2 pcs rahim             -> return, rahim, qty 2
    stock koto ache               -> inventory
"""
import re

# ---------------------------------------------------------------- keywords
# English/Banglish words are matched as whole words.
# Bangla words are matched as substrings (suffixes like -কে, -র attach to words).
INTENT_KEYWORDS = {
    "sales": [
        "sales", "sale", "sell", "sold", "becha", "bechi", "bechlam", "bikri",
        "bikroy", "বিক্রি", "বিক্রয়", "বেচা", "বেচলাম", "বেচি",
    ],
    "purchase": [
        "purchase", "buy", "bought", "kena", "kinlam", "kinsi", "kinechi",
        "kroy", "ক্রয়", "কেনা", "কিনলাম", "কিনেছি", "কিনি",
    ],
    "inventory": [
        "stock", "inventory", "mojud", "mojut", "koto ache", "koto achhe",
        "মজুদ", "স্টক", "কত আছে",
    ],
    "return": [
        "return", "ferot", "ferat", "ফেরত", "ফেরৎ",
    ],
}

NEGATIONS = {"na", "nai", "noy", "not", "no", "না", "নাই", "নয়"}

STOPWORDS = {
    "to", "from", "ke", "theke", "er", "for", "of", "the", "a", "dilam", "dilo",
    "nilam", "nilo", "korlam", "koro", "kor", "diyechi", "dise",
    "কে", "থেকে", "এর", "দিলাম", "দিলো", "নিলাম", "করলাম", "করো", "দিয়েছি",
    "তে", "জন্য",
}

# ---------------------------------------------------------------- numbers
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

MULT = {
    "hajar": 1_000, "hazar": 1_000, "হাজার": 1_000, "k": 1_000,
    "lakh": 100_000, "lac": 100_000, "লাখ": 100_000, "লক্ষ": 100_000,
}
CURRENCY = {"tk", "taka", "টাকা", "টাকার", "৳", "/-", "bdt"}
QTY_UNITS = {
    "pcs", "pc", "piece", "pieces", "pis", "kg", "kgs", "gram", "gm",
    "dozen", "dz", "liter", "litre", "ltr", "packet", "pack", "bag",
    "পিস", "কেজি", "গ্রাম", "ডজন", "লিটার", "প্যাকেট", "বস্তা",
}

_mult_alt = "|".join(sorted(map(re.escape, MULT), key=len, reverse=True))
_cur_alt = "|".join(sorted(map(re.escape, CURRENCY), key=len, reverse=True))
_unit_alt = "|".join(sorted(map(re.escape, QTY_UNITS), key=len, reverse=True))

# number + (multiplier and/or currency). e.g. 500tk, 5 hajar, 2.5k, 3 lakh taka
AMOUNT_RE = re.compile(
    rf"(?P<num>\d+(?:\.\d+)?)\s*"
    rf"(?:(?P<mult>{_mult_alt})(?![a-z]))?\s*"
    rf"(?:(?P<cur>{_cur_alt})(?![a-z]))?",
    re.I,
)
# currency before number. e.g. tk 500, ৳500
AMOUNT_PREFIX_RE = re.compile(rf"(?:{_cur_alt})\.?\s*(?P<num>\d+(?:\.\d+)?)", re.I)
QTY_RE = re.compile(rf"(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>{_unit_alt})(?![a-z])", re.I)
BARE_NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def normalize(text: str) -> str:
    text = text.translate(BN_DIGITS)
    text = re.sub(r"(?<=\d),(?=\d)", "", text)  # 1,500 -> 1500
    return text.strip()


# ---------------------------------------------------------------- intent
def _find_hits(text_lower: str, words: list[str]) -> list[tuple[int, int]]:
    """Return (start, end) spans of keyword hits, skipping negated ones."""
    hits = []
    for w in words:
        if w.isascii():
            pattern = rf"(?<![a-z]){re.escape(w)}(?![a-z])"
        else:
            pattern = re.escape(w)
        for m in re.finditer(pattern, text_lower):
            after = re.findall(r"[^\s,;:.!?]+", text_lower[m.end():])[:1]
            if after and after[0] in NEGATIONS:  # "return na" -> not a return
                continue
            hits.append((m.start(), m.end()))
    return hits


def detect_intent(text: str) -> dict:
    t = normalize(text).lower()
    scores = {}
    for intent, words in INTENT_KEYWORDS.items():
        n = len(_find_hits(t, words))
        if n:
            scores[intent] = n

    if not scores:
        return {"intent": "other", "confidence": 0.0, "scores": {}, "ambiguous": False}

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best, best_n = ranked[0]
    total = sum(scores.values())
    ambiguous = len(ranked) > 1 and ranked[1][1] == best_n
    return {
        "intent": best,
        "confidence": round(best_n / total, 2),
        "scores": scores,
        "ambiguous": ambiguous,
    }


# ---------------------------------------------------------------- extraction
def extract_amount(text: str):
    t = normalize(text).lower()

    # 1) number with currency or multiplier (strongest signal)
    for m in AMOUNT_RE.finditer(t):
        if m.group("mult") or m.group("cur"):
            val = float(m.group("num"))
            if m.group("mult"):
                val *= MULT[m.group("mult")]
            return int(val) if val == int(val) else val
    # 2) currency first
    m = AMOUNT_PREFIX_RE.search(t)
    if m:
        val = float(m.group("num"))
        return int(val) if val == int(val) else val
    # 3) fallback: a bare number that is not a quantity
    qty_spans = [m.span("num") for m in QTY_RE.finditer(t)]
    for m in BARE_NUM_RE.finditer(t):
        if not any(s <= m.start() < e for s, e in qty_spans):
            val = float(m.group())
            return int(val) if val == int(val) else val
    return None


def extract_quantity(text: str):
    t = normalize(text).lower()
    m = QTY_RE.search(t)
    if not m:
        return None
    val = float(m.group("num"))
    return {"value": int(val) if val == int(val) else val, "unit": m.group("unit")}


def extract_name(text: str):
    t = normalize(text)
    all_kw = {w for ws in INTENT_KEYWORDS.values() for w in ws}
    kw_parts = {p for w in all_kw for p in w.split()}
    for token in re.findall(r"[^\s,;:()]+", t):
        low = token.lower()
        if (
            low in STOPWORDS
            or low in NEGATIONS
            or low in all_kw
            or low in kw_parts
            or low in CURRENCY
            or low in QTY_UNITS
            or low in MULT
            or any(k in low for k in all_kw if not k.isascii())
            or re.fullmatch(r"[\d.]+", low)
            or AMOUNT_RE.fullmatch(low) and re.search(r"\d", low)
            or QTY_RE.fullmatch(low)
        ):
            continue
        # strip attached Bangla suffix: রহিমকে -> রহিম
        if token.endswith("কে") and len(token) > 3:
            token = token[:-2]
        return token
    return None


# ---------------------------------------------------------------- main API
def parse(text: str) -> dict:
    result = detect_intent(text)
    result["name"] = None if result["intent"] == "other" else extract_name(text)
    result["amount"] = extract_amount(text)
    result["quantity"] = extract_quantity(text)
    # Suggested action for your app
    if result["intent"] == "other":
        result["action"] = "ask_again"
    elif result["ambiguous"]:
        result["action"] = "confirm_with_user"
    else:
        result["action"] = "save"
    return result


if __name__ == "__main__":
    tests = [
        "sales rahim to 500tk",
        "rahim ke 5 hajar becha",
        "রহিম কে ৫০০ টাকা বিক্রি",
        "রহিমকে ১,২০০ টাকার বিক্রি",
        "kena karim theke 2.5k",
        "purchase from abul 1 lakh",
        "ferot 2 pcs rahim",
        "ফেরত করিম ৩ কেজি",
        "stock koto ache",
        "মজুদ কত আছে",
        "return na, sales rahim 300 tk",
        "hello kemon acho",
        "sales return rahim 200",
    ]
    for s in tests:
        r = parse(s)
        print(f"{s!r}\n  -> {r['intent']} (conf {r['confidence']}) | "
              f"name={r['name']} | amount={r['amount']} | qty={r['quantity']} | {r['action']}")

    print("\nType a command (empty line to quit):")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            break
        print(parse(line))
