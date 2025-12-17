from datetime import datetime, timedelta
import re

def parse_date(text):
    if not text:
        return None
    now = datetime.now()
    text = text.lower()

    m = re.search(r"(\d+)\s*(minute|hour|day|week)s?\s*ago", text)
    if m:
        v, u = int(m.group(1)), m.group(2)
        dt = now - {
            "minute": timedelta(minutes=v),
            "hour": timedelta(hours=v),
            "day": timedelta(days=v),
            "week": timedelta(weeks=v),
        }[u]
        return dt.strftime("%m-%d-%Y")

    m_vi = re.search(r"(\d+)\s*(phút|giờ|ngày|tuần)\s*trước", text)
    if m_vi:
        v, u = int(m_vi.group(1)), m_vi.group(2)
        dt = now - {
            "phút": timedelta(minutes=v),
            "giờ": timedelta(hours=v),
            "ngày": timedelta(days=v),
            "tuần": timedelta(weeks=v),
        }[u]
        return dt.strftime("%m-%d-%Y")

    m_date = re.search(r"(\d{2}-\d{2}-\d{4})", text)
    if m_date:
        d, m, y = m_date.group(1).split("-")
        return f"{m}-{d}-{y}"
    return None

def is_empty(val):
    return val is None or (isinstance(val, str) and not val.strip())

def safe_text(locator):
    return locator.first.inner_text().strip() if locator.count() > 0 else None