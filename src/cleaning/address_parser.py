import unidecode
import re
from src.utils.contants import SUB_WORDS_ADDRESS

def normalize(s):
    s = unidecode.unidecode(s.strip().lower())
    pattern = r"\b(" + "|".join(SUB_WORDS_ADDRESS) + r")\b"
    s = re.sub(pattern, "", s)
    return s.strip()


def parse_locations(raw, cities_json):
    parts = [p.strip() for p in raw.split(":")]

    city_raw = parts[0]
    city_norm = normalize(city_raw)

    district_raw = parts[1] if len(parts) > 1 else None
    district_norm = normalize(district_raw) if district_raw else None

    matched_city = None
    matched_district = None

    for c in cities_json:
        if city_norm in normalize(c['name']):
            matched_city = c['name']

        if district_norm:
            for d in c["districts"]:

                if district_norm == normalize(d["name"]):
                    if district_norm == normalize(c["name"]):
                        matched_city = d['name']
                        matched_district = None
                    else:
                        matched_district = d["name"]
                    break

    return matched_city, matched_district


