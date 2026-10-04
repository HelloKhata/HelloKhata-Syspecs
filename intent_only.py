"""
Sentence in -> intent out. No LLM, no API, works offline.

    from intent_only import detect_intent
    detect_intent("sales rahim to 500tk")   # 'sales'

Possible results:
    sales, purchase, inventory, sales return, purchase return, other
"""
import re

# Words for each base intent.
# English/Banglish words match as whole words; Bangla words match as substrings.
KEYWORDS = {
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

# Hints that tell which side a "return" belongs to.
CUSTOMER_HINTS = ["customer", "grahok", "গ্রাহক", "কাস্টমার"]
SUPPLIER_HINTS = ["supplier", "vendor", "mohajon", "company", "সাপ্লায়ার", "মহাজন", "সরবরাহকারী", "কোম্পানি"]

# If a sentence says only "return" with no other clue, which one is it?
DEFAULT_RETURN = "sales return"

NEGATIONS = {"na", "nai", "noy", "not", "no", "না", "নাই", "নয়"}
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def _count(text: str, words: list[str]) -> int:
    """Count keyword hits, ignoring ones followed by a negation ('return na')."""
    n = 0
    for w in words:
        pattern = rf"(?<![a-z]){re.escape(w)}(?![a-z])" if w.isascii() else re.escape(w)
        for m in re.finditer(pattern, text):
            nxt = re.findall(r"[^\s,;:.!?]+", text[m.end():])[:1]
            if nxt and nxt[0] in NEGATIONS:
                continue
            n += 1
    return n


def detect_intent(sentence: str) -> str:
    t = sentence.translate(BN_DIGITS).lower()

    sales = _count(t, KEYWORDS["sales"]) + _count(t, CUSTOMER_HINTS)
    purchase = _count(t, KEYWORDS["purchase"]) + _count(t, SUPPLIER_HINTS)
    inventory = _count(t, KEYWORDS["inventory"])
    ret = _count(t, KEYWORDS["return"])

    # Return: decide which side it belongs to
    if ret:
        if sales > purchase:
            return "sales return"
        if purchase > sales:
            return "purchase return"
        return DEFAULT_RETURN

    # Normal intents
    scores = {"sales": sales, "purchase": purchase, "inventory": inventory}
    best = max(scores.values())
    if best == 0:
        return "other"
    winners = [k for k, v in scores.items() if v == best]
    return winners[0] if len(winners) == 1 else "other"  # tie = unclear


if __name__ == "__main__":
    tests = [
        "sales rahim to 500tk",
        "rahim ke 5 hajar becha",
        "রহিম কে ৫০০ টাকা বিক্রি",
        "kena karim theke 2.5k",
        "purchase from abul 1 lakh",
        "stock koto ache",
        "মজুদ কত আছে",
        "customer rahim ferot dilo 2 pcs",
        "sales return rahim 200",
        "গ্রাহক ফেরত দিলো",
        "supplier abul ke ferot dilam",
        "purchase return abul 300",
        "মহাজনকে মাল ফেরত",
        "ferot 2 pcs",
        "return na, sales rahim 300 tk",
        "hello kemon acho",
    ]
    for s in tests:
        print(f"{s!r:45} -> {detect_intent(s)}")

    print("\nType a sentence (empty line to quit):")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            break
        print(detect_intent(line))
