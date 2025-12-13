import re
from src.utils.logger import get_logger
import unidecode

logger = get_logger(__name__)

def _detect_unit(text):
    t = text.lower()

    if 'usd' in t or '$' in t:
        return 'USD'
    return 'VND'

def _parse_number(s_num, s_raw = None):
    # normalize decimal common/dot to find amount in salary
    s_cleaned = unidecode.unidecode(s_raw.strip() if s_raw is not None else s_num)
    s_num = unidecode.unidecode(s_num.replace(',', '').replace('.', ''))
    m = re.search(r"(\d+(?:\.\d+)?)", s_num)

    if not m:
        return None
    salary = float(m.group(1))

    if 'ty' in s_cleaned:
        return salary * 1000000000
    if 'trieu' in s_cleaned:
        return salary * 1000000
    if 'nghin' in s_cleaned or 'ngan' in s_cleaned:
        return salary * 1000
    if 'tram' in s_cleaned:
        return salary * 100
    print(f"salary: {salary}")

    return salary

def clean_salary(raw):
    if raw == '':
        return None, None, None
    text = unidecode.unidecode(raw.strip().lower())
    if text == '' or any(k in text for k in ['thoa', 'thoa thuan', 'thoathuan', 'thuong luong', 'thuongluong']):
        return None, None, None
    unit = _detect_unit(text)

    t = re.sub(r"[---]", "-", text)
    m = re.search(r"\$?([\d,.]+)\s*-\s*\$?([\d,.]+)", t)
    print(f"t: {t}")

    if m:
        a = _parse_number(m.group(1), t)
        b = _parse_number(m.group(2), t)
        return a, b, unit

    if any(k in t for k in ['tren', 'tu', 'from']):
        n = _parse_number(t)
        return (n, None, unit) if n is not None else (None, None, unit)

    if any(k in t for k in ['toi', 'den', 'upto', 'up to']):
        n = _parse_number(t)
        return (0.0, n, unit) if n is not None else (None, None, unit)

    n = _parse_number(t)
    if n is not None:
        return n, n, unit

    return None, None, None

