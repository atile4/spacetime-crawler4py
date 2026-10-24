from configparser import ConfigParser
from bs4 import BeautifulSoup

from utils.config import Config
from utils.download import download
from utils import get_logger
from utils.server_registration import get_cache_server

url = "http://www.ics.uci.edu/~dsm/dyn/release/files/zImage_paapi"

parser = ConfigParser()
parser.read("config.ini")

config = Config(parser)
config.cache_server = get_cache_server(config, False)

resp = download(url, config, get_logger("CRAWLER"))
print("Requested URL:", url) # to test for redirects
print("Response URL:", resp.url) # to test for redirects

if resp.raw_response is not None:
    print("Final URL:", resp.raw_response.url) # to test for redirects
    print("Status:", resp.status)
    print("Redirect history:", resp.raw_response.history)
    print("Status:", resp.status)
    print("Content-Type:", resp.raw_response.headers.get("Content-Type"))
    print("File size:", len(resp.raw_response.content), "bytes")
    print("First 200 bytes:", resp.raw_response.content[:200])

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    text = soup.get_text(" ", strip=True)

    print("Extracted text:", repr(text))
    print("Word count:", len(text.split()))
else:
    print("No raw response!")