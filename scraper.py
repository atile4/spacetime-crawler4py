import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup

'''
Report Content:
1. How many unique pages did you find? 
    ONLY consider URL, discarding the fragment part: http://www.ics.uci.edu#aaa == http://www.ics.uci.edu#bbb == 1 unique page
2. What is the longest page in terms of the number of words? 
    (HTML markup doesn’t count as words)
3. What are the 50 most common words in the entire set of pages crawled under these domains ? 
    (Ignore English stop words: https://www.ranks.nl/stopwords)
    Submit list of common words ordered by frequency.
4. How many subdomains did you find in the ics.uci.edu domain? 
    Submit list of subdomains ordered alphabetically AND the number of unique pages detected in each subdomain. 
    Format should be lines containing <URL>, <number>   For example:  http://vision.ics.uci.edu, 10


In this project, we are looking for TEXT on Web pages so that we can search for it later on. 
    The following is a list of what a "correct crawl" entails in this context:
        * Honor the politeness delay for each site
        * Crawl all pages with high textual information content
        * Detect and avoid infinite traps
        * Detect and avoid sets of similar pages with no information
        * Detect redirects and if the page redirects your crawler, index the redirected content
        * Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes mean)
        * Detect and avoid crawling very large files, especially if they have low information value

    Notes & Tips:
        Note 1: Please remember to transform relative to absolute URLs (you will get very wrong statistics if you do not remember to do so, and your grade will suffer).
        Note 2: Also, please, add comments throughout your code. We shouldn’t need to ask you to do this at this point in your career, but we keep this note as a reminder.
        Note 3: Before launching your crawler, ensure that you send the server a request with an ASCII URL, but neither the entire HTML content of the webpage that you are crawling nor garbage/Unicode strings.
        Note 4: You should write simple automatic trap detection systems based on repeated URL patterns and/or (ideally) webpage content similarity repetition over a certain amount of chained pages (the threshold definition is up to you!).
        Note 5: Use openlab and tmux to operate your crawler. This will certainly make your life easier.
'''


def _url_allowed_by_robot_txt(url : str, user_agent = '*') -> bool:
    """
    Returns if string is valid and is not disallowed in the base_url's robots.txt
    """

    # make sure we even care about accessing this url
    # also checks validity
    if not is_valid(url): return False

    # get base url
    parts = urlparse(url)
    base_url = f"{parts.scheme}://{parts.netloc}"

    # Read and parse robots.txt
    rp = RobotFileParser(f"{base_url}/robots.txt")
    try:
        rp.read()
    except Exception as e:
        # return True on error; no robots.txt to deny entry
        print(f'Returned True after exception encountered accessing robots.txt of {base_url}:', e)
        return True

    # check if url is allowed
    return rp.can_fetch(user_agent, url) 



def scraper(url, resp) -> list[str]:
    """
    handles logic for web scraping returns valid links found in the webpage
    Inputs:
        url(string) - url used to get the page
        resp(response object) - the downloaded response object of the url
    Returns:
        return_links(list[str]) - list of valid links found in webpage
    """
    # NOTES: 
    # look into using socket.setdefaulttimeout to prevent program from hanging or crashing on unresponsive servers
    # when we run this program, make sure that the existing base code implements a delay for politeness, else use time.sleep(POLITENESS) or smth like that


    # initialize return list
    return_links = []

    # check validity of the link we were passed
    if not (_url_allowed_by_robot_txt(url)): return return_links


    # add logic for traps & stuff here, before page is parsed for links



    # extract_next_links handles any http errors from resp
    links = extract_next_links(url, resp)

    # tokenize page and 

    # iterate through all links; check if they can be crawled
    for link in links:
        if not (_url_allowed_by_robot_txt(url)): continue
        return_links.append(url)
        
    return return_links

    # return [link for link in links if is_valid(link)] # old return value







def extract_next_links(url, resp):
    """
    extracts all the links found in the webpage to be returned 
    Inputs:
        url(string) - url used to get the page
        resp(response object) - the downloaded response object of the url
    Returns:
        hyper_links(list[str]) - list of links found in webpage
    """
    # goal: return a list with ALL hyperlinks -> valid or not
    # create a list
    hyper_links = []

    # check whether response is sucessful or if there is no content -> if not return
    if resp.status != 200 or resp.raw_response is None:
        return hyper_links

    # parse the content -> accquire the links
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
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