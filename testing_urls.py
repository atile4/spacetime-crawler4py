from configparser import ConfigParser
from bs4 import BeautifulSoup

from utils.config import Config
from utils.download import download
from utils import get_logger
from utils.server_registration import get_cache_server

url = "https://wiki.ics.uci.edu/doku.php/projects:maint-fall-2019"

parser = ConfigParser()
parser.read("config.ini")

config = Config(parser)
config.cache_server = get_cache_server(config, False)

resp = download(url, config, get_logger("CRAWLER"))
print("Requested URL:", url) # to test for redirects
print("Response URL:", resp.url) # to test for redirects

if resp.raw_response is not None:
    print("Final URL:", resp.raw_response.url) # to test for redirects
    print("Redirect history:", resp.raw_response.history)
    print("Status:", resp.status)
    print("Content-Type:", resp.raw_response.headers.get("Content-Type"))
    print("File size:", len(resp.raw_response.content), "bytes")
    print("First 200 bytes:", resp.raw_response.content[:200])

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    text = soup.get_text(" ", strip=True)
    body = soup.body.get_text(" ", strip=True) if soup.body else ""
    main = soup.main.get_text(" ", strip=True) if soup.main else ""
    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

    print("Extracted text:", repr(text))
    print("Word count:", len(text.split()))
    print("BODY:", repr(body))
    print("Word count:", len(body.split()))
    print("MAIN:", repr(main))
    print("Word count:", len(main.split()))
    print("P TEXT:", repr(text))
    print("Word count:", len(text.split()))
    
    print("ARTICLE:", soup.article.get_text(" ", strip=True)[:500] if soup.article else None)
else:
    print("No raw response!")