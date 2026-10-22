from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time



class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    """    
    @TODO 
        - detect duplicate pages
        - avoiding infinite traps
        - Report class: implement visitedSite
        - implement subdomain updating
        - avoiding dead URLs that return a 200
        - verify that transforms relative to URL
        - verify detects redirects and if the page redirects your crawler, index the redirected content
        - use tmux to operate crawler
        - add more if necessary
    """
    def run(self):
        report = scraper.Report()
        # i = 0
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, report, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
            # i += 1
        print("============REPORT============")
        print("unique pages:", len(report.visited_urls))
        print("longest page:", report.longest_webpage)
        print("top 50 words:", report.getMostCommonWords())