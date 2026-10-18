import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    """
    Inputs:
        url(string) - url used to get the page
        resp(response object) - the downloaded response object of the url
    Outputs:
        hyper_links(list) - list of links found in webpage
    """
    # goal: return a list with ALL hyperlinks -> valid or not
    # create a list
    hyper_links = []
    
    # check whether response is sucessful -> if not return
    if resp.status != 200 or resp.raw_response is None:
        return hyper_links

    # parse the content -> accquire the links
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for link in soup.find_all('a', href=True):
        temp = link.get('href')
        # if empty skip to the next link
        if temp == '': 
            continue
        # appending links to list, for realtive -> converting to absolute
        hyper_links.append(urljoin(resp.url, temp))

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
        return not re.match( 
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise