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
from datetime import datetime 
from text_processing import tokenize

# trap function variables
MAX_URL_LENGTH = 200
MAX_PATH_DEPTH = 10
MAX_QUERY_PARAMS = 4
MAX_URLS_PER_TEMPLATE = 30
MAX_CALENDAR_URLS = 10 

# page-quality. checker variables
MIN_WORDS = 50
MAX_CONTENT_BYTES = 2 * 1024 * 1024

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

# regex pattern to find dates formatted yyyy-mm or yyyy-mm-dd
DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}(?:-\d{2})?(?!\d)")

def is_calendar_date(url):
    parsed = urlparse(url)

    for match in DATE_RE.finditer(parsed.path):
        date = match.group() # getting just the matched text from obj

        try:
            if len(date) == 10:
                datetime.strptime(date, "%Y-%m-%d") #can raise an exception if it can't b stripped as date fromat
            else:
                datetime.strptime(date, "%Y-%m") #can raise an exception if it can't b stripped as date fromat
            return True
        
        except ValueError:
            continue

    return False

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
    limit = MAX_URLS_PER_TEMPLATE

    if is_calendar_date(url):
        limit = MAX_CALENDAR_URLS

    if url in seen_urls:
        return False

    if template_counts[template] >= limit:
        return True

    seen_urls.add(url)
    template_counts[template] += 1
    return False


def low_value_reason(resp, text):
    raw = resp.raw_response

    if raw is None or not raw.content:
        return "empty page"

    content_type = raw.headers.get("Content-Type", "").lower()
    if content_type and "html" not in content_type:
        return f"not html ({content_type.split(';')[0]})"

    if len(raw.content) > MAX_CONTENT_BYTES:
        return "too large"

    if len(text.split()) < MIN_WORDS:
        return f"too few words ({len(text.split())})"

    return None