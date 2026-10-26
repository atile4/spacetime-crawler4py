
from configparser import ConfigParser
from bs4 import BeautifulSoup, UnicodeDammit
from text_processing import tokenize

from utils.config import Config
from utils.download import download
from utils import get_logger
from utils.server_registration import get_cache_server

url = "https://cml.ics.uci.edu/category/aiml/"

parser = ConfigParser()
parser.read("config.ini")

config = Config(parser)
config.cache_server = get_cache_server(config, False)

resp = download(url, config, get_logger("CRAWLER"))

response = resp.raw_response

print("Status:", response.status_code)
print("Final URL:", response.url)
print("Content-Type:", response.headers.get("Content-Type"))
print("Size:", len(response.content))

soup = BeautifulSoup(response.content, "html.parser")

print("Page title:", soup.title.get_text(" ", strip=True) if soup.title else None)
print("Encoding:", soup.original_encoding)
print("Token count:", len(tokenize(soup.get_text(" ", strip=True))))
print("Text preview:", repr(soup.get_text(" ", strip=True)))
