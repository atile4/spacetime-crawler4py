from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
from scraper import Report

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        self.report = Report() # one shared report for all workers
        if not restart: # load saved report
            self.report.load_report()
        else: # restart previous progress
            self.report.save_report() 
            open("report_files/report.txt", "w").close()

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.report)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()

        self.report.save_report()
        with open("report_files/report.txt", "w", encoding="utf-8") as file:
            file.write(self.report._print_report())
        print(self.report._print_report())           # runs once, after every worker is done