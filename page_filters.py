"""
Trap detection plan:

Way to look for traps:
 - URLs are very similar (i.e. /10-21-2023 then /10-22-2023)
    - maybe if only one haracter was changed per URL? 
- crawl depth limit?
- URLs that keep generating new parameters
- 

- Unbounded date / numeric sequences (increasing date, number, ID, time stamp?)
ex. /events/{date} -> /events/2026-10-21
- Same path accumulating new parameter values or combinations
- Excessive path depth or repeating segments
Ex. /page/..., /calendar/...
- Cap depth
- 

"""

import re
from urllib.parse import urlparse, parse_qsl

MAX_URL_LENGTH = 200 
MAX_PATH_DEPTH = 10
MAX_QUERY_PARAMS = 4

# same chunk of path 3+ times in a row, e.g. /a/b/a/b/a/b
REPEATING_PATH_RE = re.compile(r"(/.+?)\1{2,}")


def is_trap(url):
    try:
        parsed = urlparse(url)
        params = parse_qsl(parsed.query, keep_blank_values=True)
    except ValueError:
        return True

    if len(url) > MAX_URL_LENGTH:
        return True

    segments = [s for s in parsed.path.split("/") if s]
    if len(segments) > MAX_PATH_DEPTH:
        return True

    if REPEATING_PATH_RE.search(parsed.path):
        return True

    if len(params) > MAX_QUERY_PARAMS:
        return True

    return False