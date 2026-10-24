import requests
from bs4 import BeautifulSoup
from utils.download import download
from utils import get_logger

url = "http://www.ics.uci.edu/~dsm/dyn/release/files/zImage_paapi"
resp = download(url, "config.ini", get_logger("CRAWLER"))

print("Status:", resp.status)

if resp.raw_response is None:
    print("No raw response!")
else:
    print("Content-Type:", resp.raw_response.headers.get("Content-Type"))
    print("Size:", len(resp.raw_response.content), "bytes")
    print("First 200 bytes:", resp.raw_response.content[:200])

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    text = soup.get_text(" ", strip=True)

    print("Extracted text:", repr(text[:500]))
    print("Extracted characters:", len(text))
