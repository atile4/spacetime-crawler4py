
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

print("Requested URL:", url)
print("Response URL:", resp.url)
print("Status:", resp.status)

if resp.raw_response is not None:
    response = resp.raw_response
    raw = response.content

    print("Final URL:", response.url)
    print("Redirect history:", response.history)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("File size:", len(raw), "bytes")
    print("First 80 bytes:", repr(raw[:80]))

    # Test different character encodings
    for encoding in ["utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"]:
        print(f"\n--- {encoding.upper()} TEST ---")

        try:
            html = raw.decode(encoding)
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)

            print("Decoded characters:", repr(html[:150]))
            print("HTML tag found:", soup.find("html") is not None)
            print("Body tag found:", soup.find("body") is not None)
            print("Extracted text:", repr(text[:300]))
            print("Word count:", len(text.split()))

        except UnicodeError as e:
            print("Decoding failed:", e)

    # Compare with original parsing
    print("\n--- ORIGINAL BEAUTIFULSOUP PARSING ---")

    soup = BeautifulSoup(raw, "html.parser")
    text = soup.get_text(" ", strip=True)

    print("Detected encoding:", soup.original_encoding)
    print("HTML tag found:", soup.find("html") is not None)
    print("Extracted text:", repr(text[:300]))
    print("Word count:", len(text.split()))

else:
    print("No raw response!")
