import os
import logging
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet.task import deferLater
from mercariscanner.mercari_spider import MercariSpider
from mercariscanner.alerters.alerter import Alerter

log = logging.getLogger('mercari_scanner')


class MercariScanner:
    def __init__(
            self,
            keyword,
            min_price,
            max_price,
            delay,
            out,
            alerters,
            tiers
    ):
        self.delay = delay
        self.out = out
        self.process = CrawlerProcess(settings={
            "FEEDS": {
                out: {"format": "json"},
            },
            'mercari.keyword': keyword,
            'mercari.min_price': min_price,
            'mercari.max_price': max_price
        })
        self.alerter = Alerter(alerters, out, delay / 3, tiers)

    def start(self):
        self._crawl(None)
        self.alerter.start()
        self.process.start()

    def _sleep(self, *args, seconds):
        """Non blocking sleep callback"""
        return deferLater(reactor, seconds, lambda: None)

    def _crawl(self, result):
        deferred = self.process.crawl(MercariSpider)
        deferred.addCallback(lambda results: log.info(f"waiting {self.delay} seconds before next scan..."))
        deferred.addCallback(self._sleep, seconds=self.delay)
        deferred.addCallback(lambda results: os.remove(self.out))
        deferred.addCallback(self._crawl)
        return deferred
