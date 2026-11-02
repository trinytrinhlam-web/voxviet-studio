"""Đọc số cho văn bản tiếng Anh (không cần thư viện ngoài).

Cần thiết vì bộ chuẩn hoá của lõi giọng đọc mọi chữ số theo tiếng Việt; với module
tiếng Anh, ta đổi số sang chữ tiếng Anh TRƯỚC khi đưa vào mô hình.
"""

from __future__ import annotations

import re

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
_SCALES = [(10**12, "trillion"), (10**9, "billion"), (10**6, "million"), (1000, "thousand")]
_ORD_IRREGULAR = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth",
                  "nine": "ninth", "twelve": "twelfth"}
_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December"]


def _under_1000(n: int) -> str:
    parts = []
    if n >= 100:
        parts.append(f"{_ONES[n // 100]} hundred")
        n %= 100
    if n >= 20:
        parts.append(_TENS[n // 10] + (f"-{_ONES[n % 10]}" if n % 10 else ""))
    elif n > 0 or not parts:
        parts.append(_ONES[n])
    return " ".join(parts)


def cardinal(n: int) -> str:
    if n < 0:
        return "minus " + cardinal(-n)
    if n < 1000:
        return _under_1000(n)
    parts = []
    for value, name in _SCALES:
        if n >= value:
            parts.append(f"{cardinal(n // value)} {name}")
            n %= value
    if n:
        parts.append(_under_1000(n))
    return " ".join(parts)


def ordinal(n: int) -> str:
    words = cardinal(n)
    head, sep, last = words.rpartition(" ")
    if "-" in last:
        h2, _, l2 = last.rpartition("-")
        return f"{head}{sep}{h2}-{_ordinal_word(l2)}"
    return f"{head}{sep}{_ordinal_word(last)}"


def _ordinal_word(w: str) -> str:
    if w in _ORD_IRREGULAR:
        return _ORD_IRREGULAR[w]
    if w.endswith("y"):
        return w[:-1] + "ieth"
    return w + "th"


def year(n: int) -> str:
    if 2000 <= n <= 2009:
        return cardinal(n)
    hi, lo = divmod(n, 100)
    if lo == 0:
        return f"{cardinal(hi)} hundred"
    if lo < 10:
        return f"{cardinal(hi)} oh {cardinal(lo)}"
    return f"{cardinal(hi)} {cardinal(lo)}"


def _digits(s: str) -> str:
    return " ".join(_ONES[int(c)] for c in s)


def _decimal(int_part: str, frac: str) -> str:
    return f"{cardinal(int(int_part))} point {_digits(frac)}"


_RE_CURRENCY = re.compile(r"([$€£])\s?(\d[\d,]*)(?:\.(\d{1,2}))?(\s?(?:k|K|million|billion|m|bn)\b)?")
_RE_PERCENT = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?%")
_RE_TIME = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\s?(am|pm|AM|PM|a\.m\.|p\.m\.)?")
_RE_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_RE_ORD = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.IGNORECASE)
_RE_DEC = re.compile(r"\b(\d+)\.(\d+)\b")
_RE_INT = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d+\b")
_CURRENCY = {"$": ("dollar", "cent"), "€": ("euro", "cent"), "£": ("pound", "penny")}


def _plural(word: str, n: int) -> str:
    if n == 1:
        return word
    return "pence" if word == "penny" else word + "s"


def _currency(m: re.Match) -> str:
    sym, whole, cents, scale = m.group(1), int(m.group(2).replace(",", "")), m.group(3), m.group(4)
    major, minor = _CURRENCY[sym]
    if scale:
        s = scale.strip().lower()
        scale_word = {"k": "thousand", "m": "million", "bn": "billion"}.get(s, s)
        amount = _decimal(str(whole), cents) if cents else cardinal(whole)
        return f"{amount} {scale_word} {major}s"
    out = f"{cardinal(whole)} {_plural(major, whole)}"
    if cents and int(cents):
        c = int(cents.ljust(2, "0"))
        out += f" and {cardinal(c)} {_plural(minor, c)}"
    return out


def _time(m: re.Match) -> str:
    h, mi, suf = int(m.group(1)), int(m.group(2)), m.group(3)
    words = cardinal(h)
    if mi == 0:
        words += "" if suf else " o'clock"
    elif mi < 10:
        words += f" oh {cardinal(mi)}"
    else:
        words += f" {cardinal(mi)}"
    if suf:
        words += " " + ("a m" if suf.lower().startswith("a") else "p m")
    return words


def _date(m: re.Match) -> str:
    mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return m.group(0)
    return f"{_MONTHS[mo - 1]} {ordinal(d)}, {year(y)}"


def _int(m: re.Match) -> str:
    s = m.group(0)
    n = int(s.replace(",", ""))
    if "," not in s and len(s) == 4 and 1100 <= n <= 2099:
        return year(n)
    if len(s) > 1 and s.startswith("0"):
        return _digits(s)  # mã số, số điện thoại...
    return cardinal(n)


def expand_numbers(text: str) -> str:
    text = _RE_CURRENCY.sub(_currency, text)
    text = _RE_PERCENT.sub(lambda m: (_decimal(*m.group(1).replace(",", "").split(".")) if "." in m.group(1)
                                      else cardinal(int(m.group(1).replace(",", "")))) + " percent", text)
    text = _RE_TIME.sub(_time, text)
    text = _RE_DATE.sub(_date, text)
    text = _RE_ORD.sub(lambda m: ordinal(int(m.group(1))), text)
    text = _RE_DEC.sub(lambda m: _decimal(m.group(1), m.group(2)), text)
    text = _RE_INT.sub(_int, text)
    return text
