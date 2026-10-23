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
from collections import defaultdict
from urllib.parse import urlparse, parse_qsl

MAX_URL_LENGTH = 200
MAX_PATH_DEPTH = 10
MAX_QUERY_PARAMS = 4
MAX_URLS_PER_TEMPLATE = 300

JUNK_PARAMS = {
    "sid", "sessionid", "session_id", "phpsessid", "jsessionid",
    "do", "action", "oldid", "diff", "rev",
    "ical", "outlook-ical", "tribe-bar-date",
    "share", "replytocom",
}

# same chunk of path 3+ times in a row, e.g. /a/b/a/b/a/b
REPEATING_PATH_RE = re.compile(r"(/.+?)\1{2,}")

seen_urls = set()
template_counts = defaultdict(int)


def template_of(parsed, params):
    # /events/2026-10-04?view=day -> (host, "/events/#-#-#", ("view",))
    shape = re.sub(r"\d+", "#", parsed.path)
    names = tuple(sorted(key for key, _ in params))
    return (parsed.netloc, shape, names)


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
    if any(key.lower() in JUNK_PARAMS for key, _ in params):
        return True

    template = template_of(parsed, params)
    if url not in seen_urls:
        seen_urls.add(url)
        template_counts[template] += 1
    if template_counts[template] > MAX_URLS_PER_TEMPLATE:
        return True

    return False