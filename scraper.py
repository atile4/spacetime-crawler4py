import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from text_processing import computeWordFrequencies, tokenize
from page_filters import is_trap

class Report:
    def __init__(self):
        self.visited_urls = set()
        self.url_subdomain_count = dict()
        self.token_frequency_table = dict()
        self.longest_webpage = ('', -1)

    def visitedSite(self):
        self

    def getNumVisitedURLs(self) -> int:
        return len(self.visited_urls)
    
    def getMostCommonWords(self, count = 50) -> dict[str, int]:
        return dict(list(self.token_frequency_table.items())[:50])

    def updateWordFrequencies(self, map: dict[str, int]) -> None:
        for token, freq in map.items():
            self.token_frequency_table[token] = self.token_frequency_table.get(token, 0) + freq
    
    def _incrementSubdomainCount(self, url: str):
        base_url = ...
        try:
            self.token_frequency_table[base_url] += 1
        except KeyError:
            self.token_frequency_table[base_url] = 1
        ...

    def checkIfLongestPage(self, url: str, tokens_count: int):
        if self.longest_webpage[1] < tokens_count:
            self.longest_webpage = (url, tokens_count)

def scraper(url, report : Report, resp) -> list[str]: 
    # check whether response is sucessful or if there is no content -> if not return
    if resp.status != 200 or resp.raw_response is None:
        return []

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    links = extract_next_links(url, resp, soup)

    # @TODO logic for adding unique pages, longest page, most common words, and subdomains
    parse_text_and_update_report(url, soup, report)

    return [link for link in links if is_valid(link)]

def parse_text_and_update_report(url : str, soup : BeautifulSoup, report : Report):
    # update visited URL set
    report.visited_urls.add(url)
    tokens = tokenize(soup.get_text(" ", strip=True))

    # update if longest page
    report.checkIfLongestPage(url, len(tokens))

    # compute and update word frequencies
    map = computeWordFrequencies(tokens=tokens)
    report.updateWordFrequencies(map)


def extract_next_links(url, resp, soup):
    """
    extracts all the links found in the webpage to be returned 
    Inputs:
        url(string) - url used to get the page
        resp(response object) - the downloaded response object of the url
    Outputs:
        hyper_links(list) - list of links found in webpage
    """
    # goal: return a list with ALL hyperlinks -> valid or not
    # create a list
    hyper_links = []

    # parse the content -> accquire the links
    for link in soup.find_all('a', href=True):
        temp = link.get('href')
        # if empty skip to the next link
        if not temp.strip(): 
            continue
        # appending links to list, joining links so relative becomes absolute
        temp = urljoin(resp.url, temp).split("#")[0] #removing the url fragment
        hyper_links.append(temp)

    return hyper_links

def is_valid(url : str) -> bool:
    '''
    Decide whether to crawl this url or not. 

    If decide to crawl, return True; otherwise False

    Input:
        url(string): the potential URL to crawl
    Returns:
        boolean: True to crawl, False to not crawl
    '''
    # Valid Links: *.ics.uci.edu/*, *.cs.uci.edu/*, *.informatics.uci.edu/*, *.stat.uci.edu/*
    # using regex
    VALID_URL_RE = re.compile(r"^(?:[a-z0-9-]+\.)*(?:ics|cs|informatics|stat)\.uci\.edu$")

    try:
        parsed = urlparse(url)
        # check if URL is http or https / check if it's a link we want
        if parsed.scheme not in set(["http", "https"]) or not VALID_URL_RE.match(parsed.netloc): 
            return False

        # check if path is file extension
        if re.match( 
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        
        return not is_trap(url)

    except TypeError:
        print ("TypeError for ", parsed)
        raise