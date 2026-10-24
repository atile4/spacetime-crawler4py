from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import requests

class Worker(Thread):
    def __init__(self, worker_id, config, frontier, report):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.report = report
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def _download_with_retry(self, url):
        while True:
            try:
                return download(url, self.config, self.logger)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                self.logger.error(f"Cache server unreachable ({type(e).__name__}) for {url}. Retrying in 5s.")
                time.sleep(5)
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed for {url}: {e}")
                return None
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
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            # robots.txt check
            if not self.report.isAllowedByRobots(tbd_url, fetch=self._download_with_retry):
                self.frontier.mark_url_complete(tbd_url)
                continue

            # download the page through the cache server
            resp = self._download_with_retry(tbd_url)
            if resp is None:
                self.frontier.mark_url_complete(tbd_url)
                continue

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            # scrape, enqueue new links, mark done
            for scraped_url in scraper.scraper(tbd_url, self.report, resp):
                self.frontier.add_url(scraped_url)

            self.report.save_report() # saving report of urls stats
            with self.report._save_lock:
                with open("report_files/report.txt", "w", encoding="utf-8") as file:
                    file.write(self.report._print_report())
    
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)