import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from text_processing import computeWordFrequencies, tokenize
from page_filters import is_trap, low_value_reason

from urllib.robotparser import RobotFileParser



class Report:
    def __init__(self):
        self.visited_urls = set()
        self.longest_webpage = ('', -1)
        self.token_frequency_table = dict()
        self.url_subdomain_count = dict()
        self._robot_rules = dict()


    def visitSite(self, url, soup):
        # use isValid before calling this method;
        # robots helper no longer does that check
        if url in self.visited_urls: return None
        parts = urlparse(url)
        base_url = f"{parts.scheme}://{parts.netloc}"
        if not self._urlAllowedByRobotTxt(url, base_url): return None

        self.visited_urls.add(url)


        tokens = tokenize(soup.get_text(" ", strip=True))
        num_tokens = len(tokens)
        token_freq = computeWordFrequencies(tokens=tokens)

        self._updateWordFrequencies(token_freq)
        self._incrementSubdomainCount(base_url)
        self._checkIfLongestPage(url, num_tokens)

    def getNumVisitedURLs(self) -> int:
        return len(self.visited_urls)
    
    def getLongestWebpage(self):
        return self.longest_webpage

    def getMostCommonWords(self, count = 50) -> list[tuple[str, int]]:
        # returns most common words as a sorted list of tuples
        return sorted(self.token_frequency_table.items(),
            key=lambda item: (-item[1], item[0]))[:count]

    def getURLSubdomainCount(self) -> list[tuple[str, int]]:
        # returns subdomains as a sorted list of tuples
        return sorted(self.url_subdomain_count.items(),
            key=lambda item: (-item[1], item[0]))

    def _updateWordFrequencies(self, map: dict[str, int]) -> None:
        for token, freq in map.items():
            self.token_frequency_table[token] = self.token_frequency_table.get(token, 0) + freq
    
    def _incrementSubdomainCount(self, base_url: str):
        if base_url in self.url_subdomain_count:
            self.url_subdomain_count[base_url] += 1
        else:
            self.url_subdomain_count[base_url] = 1    
        
    def _checkIfLongestPage(self, url: str, tokens_count: int):
        if self.longest_webpage[1] < tokens_count:
            self.longest_webpage = (url, tokens_count)

    def _urlAllowedByRobotTxt(self, url : str, base_url: str, user_agent = '*') -> bool:
        """
        Returns if string is valid and is not disallowed in the base_url's robots.txt
        """
        robot_url = f'{base_url}/robots.txt'
        # Read and parse robots.txt
        if robot_url in self._robot_rules:
            return self._robot_rules[robot_url].can_fetch(user_agent, url)

        rp = RobotFileParser(robot_url)
        try:
            rp.read()
        except Exception as e:
            # return True on error; no robots.txt to deny entry
            print(f'Returned True after exception encountered accessing robots.txt of {base_url}:', e)
            return True

        # @TODO potential optimization:
        # store disallowed urls in a dictionary that maps str base urls to a set of their disallowed urls

        # check if url is allowed
        self._robot_rules[robot_url] = rp
        return rp.can_fetch(user_agent, url) 

def scraper(url, report : Report, resp) -> list[str]: 
    # check whether response is sucessful or if there is no content -> if not return
    if resp.status != 200 or resp.raw_response is None:
        return []
    if not is_valid(url): return []

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    reason = low_value_reason(resp, soup.get_text(" ", strip=True))
    if reason:
        print(f"Skipped {url}: {reason}")
        return []

    links = extract_next_links(url, resp, soup)

    report.visitSite(url, soup)

    return [link for link in links if is_valid(link)]

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

        try: 
            temp = urljoin(resp.url, temp).split("#")[0] #removing the url fragment
            hyper_links.append(temp)
        except ValueError:
            print(f"Skipping malformed URL: {temp}")
            continue

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