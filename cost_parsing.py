"""
Shared cost/price extraction utilities for Halifax event scrapers.

Unifies ticket price extraction from mixed marketing copy, including:
- $ amounts, CAD / dollars text, price ranges, "from $X", cover/door/ticket lines
- Free / PWYC / no cover / French gratuit
- Avoids classifying "sugar-free" style words as "Free admission" where possible
"""

import re
from typing import List, Optional, Tuple

# Non-numeric cost phrases: keep text, do not add $ in format_cost_fields
NON_MONETARY_COST_PHRASES = frozenset(
    {
        "see website",
        "see event website",
        "tba",
        "tbc",
        "tbd",
        "various",
        "call",
        "contact",
        "contact venue",
    }
)

# Min/max for plausible single-ticket amounts (CAD)
_MIN_TICKET = 0.5
_MAX_TICKET = 15000.0


def _is_plausible_price(val: float) -> bool:
    # Reject year-like stand-alone 4-digit amounts (common in event copy)
    if val == int(val) and 2015 <= int(val) <= 2035:
        return False
    return _MIN_TICKET <= val <= _MAX_TICKET


def _norm_price_str(p: str) -> str:
    p = p.strip()
    if not p:
        return p
    if "." in p:
        p = p.rstrip("0").rstrip(".")
    return p


def extract_event_cost(*text_sources: str) -> str:
    """
    Extract event cost from one or more text blobs (title, description, page text, etc.).

    Returns:
        "Free" | "20" | "20.5" | "20 - 35" | "" (unknown)
    """
    combined = " ".join(str(t) for t in text_sources if t)
    if not combined.strip():
        return ""

    low = combined.lower()

    # ---- Free / PWYC (avoid matching "carefree" — no \\bfree\\b inside a word) ----
    free_phrases = [
        r"\bno cover\b",
        r"\bno charge\b",
        r"\bno cost\b",
        r"\bno ticket(?:s)?\s+required\b",
        r"\bfree admission\b",
        r"\bfree entry\b",
        r"\bfree to attend\b",
        r"\bcomplimentary\b",
        r"\bpwyc\b",
        r"\bpay what you can\b",
        r"\bby donation\b",
        r"\bsuggested donation\b",
        r"\bgratuit\b",
        r"\bgratis\b",
        r"\bdoors?\s*open\s+free\b",
    ]
    for pat in free_phrases:
        if re.search(pat, low, re.IGNORECASE):
            return "Free"

    # Standalone "free" (not part of *-free compound)
    for m in re.finditer(r"(?<![-–—])\bfree\b(?![-–—])", low):
        start = m.start()
        if start >= 1 and low[start - 1] == "-":
            continue
        return "Free"

    if re.search(r"\bfree\s*[!.,]?\s*$", low, re.IGNORECASE) and "carefree" not in low:
        return "Free"

    # ---- Price ranges: $20 - $35, $20–$35, 20-35 CAD, 20 to 35 ----
    range_patterns = [
        r"\$\s*(\d+(?:\.\d{1,2})?)\s*[-–—]+\s*\$?\s*(\d+(?:\.\d{1,2})?)\b",
        r"\b(\d+(?:\.\d{1,2})?)\s*[-–—]+\s*(\d+(?:\.\d{1,2})?)\s*(?:CAD|cdn|dollars?)\b",
        r"(?:from|between)\s*\$?\s*(\d+(?:\.\d{1,2})?)\s*[-–—to]+\s*\$?\s*(\d+(?:\.\d{1,2})?)\b",
    ]
    for pat in range_patterns:
        rm = re.search(pat, combined, re.IGNORECASE)
        if not rm:
            continue
        try:
            a, b = float(rm.group(1)), float(rm.group(2))
        except ValueError:
            continue
        if _is_plausible_price(a) and _is_plausible_price(b):
            lo, hi = (a, b) if a <= b else (b, a)
            return f"{_norm_price_str(str(lo))} - {_norm_price_str(str(hi))}"

    # ---- "Tickets: $X", "cover $X", "door: 25", "GA $30" ----
    keyword_price = re.search(
        r"(?:tickets?|admission|cover|door|ga\b|general admission|price|cost|"
        r"entry|pre-?sale|presale|box office|at the door|(?:^|\s)fee)[:\s]+"
        r"\$?\s*(\d+(?:\.\d{1,2})?)(?:\s*(?:\+|plus)\s*tax)?",
        combined,
        re.IGNORECASE,
    )
    if keyword_price:
        try:
            v = float(keyword_price.group(1))
        except ValueError:
            v = 0.0
        if _is_plausible_price(v):
            return _norm_price_str(keyword_price.group(1))

    # ---- "from $X", "starting at $X", "as low as" ----
    from_m = re.search(
        r"(?:from|starting at|starts at|as low as|only|just)\s+\$?\s*(\d+(?:\.\d{1,2})?)\b",
        low,
        re.IGNORECASE,
    )
    if from_m:
        try:
            v = float(from_m.group(1))
        except ValueError:
            v = 0.0
        if _is_plausible_price(v):
            return _norm_price_str(from_m.group(1))

    # ---- $45 CAD, 45.00 CAD ----
    cad_m = re.search(
        r"\$?\s*(\d+(?:\.\d{1,2})?)\s*(?:CAD|cdn\.?)\b",
        combined,
        re.IGNORECASE,
    )
    if cad_m:
        try:
            v = float(cad_m.group(1))
        except ValueError:
            v = 0.0
        if _is_plausible_price(v):
            return _norm_price_str(cad_m.group(1))

    # ---- 25 dollars (no $) ----
    dol_m = re.search(
        r"\b(\d+(?:\.\d{1,2})?)\s+dollars?\b",
        low,
        re.IGNORECASE,
    )
    if dol_m:
        try:
            v = float(dol_m.group(1))
        except ValueError:
            v = 0.0
        if _is_plausible_price(v):
            return _norm_price_str(dol_m.group(1))

    # ---- $ amounts: collect & prefer first in plausible range (skip years) ----
    candidates: List[Tuple[int, str, float]] = []
    for m in re.finditer(r"\$(\d+(?:\.\d{1,2})?)", combined):
        raw = m.group(1)
        try:
            val = float(raw)
        except ValueError:
            continue
        if not _is_plausible_price(val):
            continue
        candidates.append((m.start(), raw, val))

    if candidates:
        def score(pos: int, value: float) -> float:
            s = 0.0
            start = max(0, pos - 45)
            ctx = combined[start : pos + 15].lower()
            for kw in ("ticket", "cover", "admission", "door", "show", "price", "ga ", "cost"):
                if kw in ctx:
                    s += 2.0
            if 20 <= value <= 300:
                s += 0.5
            return s

        scored: List[Tuple[float, int, str]] = []
        for pos, raw, val in candidates:
            sc = score(pos, val)
            scored.append((sc, -pos, raw))
        scored.sort(reverse=True)
        return _norm_price_str(scored[0][2])

    return ""


def format_cost_fields(cost: str) -> dict:
    """
    Map a cost string to TEC cost-related field dict.
    Phrases like "See website" stay as text without a currency symbol.
    """
    c = (cost or "").strip()
    if not c:
        return {
            "EVENT COST": "",
            "EVENT CURRENCY SYMBOL": "",
            "EVENT CURRENCY POSITION": "",
            "EVENT ISO CURRENCY CODE": "",
        }

    if c.lower() == "free":
        return {
            "EVENT COST": "Free",
            "EVENT CURRENCY SYMBOL": "",
            "EVENT CURRENCY POSITION": "",
            "EVENT ISO CURRENCY CODE": "",
        }

    if c.lower() in NON_MONETARY_COST_PHRASES or (
        "see" in c.lower() and "website" in c.lower() and not re.search(r"\d", c)
    ):
        return {
            "EVENT COST": c,
            "EVENT CURRENCY SYMBOL": "",
            "EVENT CURRENCY POSITION": "",
            "EVENT ISO CURRENCY CODE": "",
        }

    return {
        "EVENT COST": c,
        "EVENT CURRENCY SYMBOL": "$",
        "EVENT CURRENCY POSITION": "prefix",
        "EVENT ISO CURRENCY CODE": "CAD",
    }


def apply_tec_cost_fields(cost: str) -> dict:
    """Alias for :func:`format_cost_fields` (clearer name for scraper code)."""
    return format_cost_fields(cost)
