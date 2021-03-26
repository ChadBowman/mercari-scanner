import os
from scrapy.crawler import CrawlerProcess
from mercari_spider import MercariSpider
from twisted.internet import reactor
from twisted.internet.task import deferLater


class MercariScanner:
    def __init__(self, keyword, min_price, max_price, retry=60, out='items.json'):
        self.retry = retry
        self.out = out
        self.process = CrawlerProcess(settings = {
            "FEEDS": {
                out: {"format": "json"},
            },
            'mercari.keyword': keyword,
            'mercari.min_price': min_price,
            'mercari.max_price': max_price
        })

    def sleep(self, *args, seconds):
        """Non blocking sleep callback"""
        return deferLater(reactor, seconds, lambda: None)

    def crawl(self, result):
        deferred = self.process.crawl(MercariSpider)
        deferred.addCallback(lambda results: print(f"waiting {self.retry} seconds before restart..."))
        deferred.addCallback(self.sleep, seconds=self.retry)
        deferred.addCallback(lambda _: os.remove(self.out))
        deferred.addCallback(self.crawl)
        return deferred

    def start(self):
        self.crawl(None)
        self.process.start()


if __name__ == "__main__":
    scanner = MercariScanner('5700xt', '10000', '100000', retry=10)
    scanner.start()
