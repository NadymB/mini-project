import unidecode
from src.utils.contants import JOB_TITLE_MAP

# alias list
aliases = []
alias_to_group = {}
for grp, arr in JOB_TITLE_MAP.items():
    for a in arr:
        aliases.append(a)
        alias_to_group[a] = grp

def standardize_title_job(raw):
    if raw is None:
        return None
    s = unidecode.unidecode(raw.lower())
    # direct substring match
    for alias, grp in alias_to_group.items():
        if alias in s:
            return grp
    return "Other"