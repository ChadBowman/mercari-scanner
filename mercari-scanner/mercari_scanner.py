import os
import argparse
import logging
import configparser
from scrapy.crawler import CrawlerProcess
from mercari_spider import MercariSpider
from twisted.internet import reactor
from twisted.internet.task import deferLater
from alerters.alerter import Alerter
from alerters.slack import SlackAlerter

log = logging.getLogger('mercari_scanner')


class MercariScanner:
    def __init__(
            self,
            keyword,
            min_price,
            max_price,
            delay,
            out,
            alerters=[]
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
        self.alerter = Alerter(alerters, out, delay / 3)

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('keyword', help='Mercari search keyword')
    parser.add_argument('--min-price',
                        help='Amount in dollars to filter out items less than min-price',
                        type=float)
    parser.add_argument('--max-price',
                        help='Amount in dollars to filter out items more than max-price',
                        type=float)
    parser.add_argument('--delay',
                        help='Time in seconds to wait before the next scan. Default: 60s',
                        type=int,
                        default=60)
    return parser.parse_args()


def parse_configs():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def main():
    config = parse_configs()
    args = parse_args()

    alerters = []
    if config.has_section('slack'):
        slack = SlackAlerter(config['slack']['token'], config['slack']['channel'])
        alerters.append(slack)
    else:
        log.info('No Slack configuration detected')

    min = None
    max = None
    if args.min_price:
        min = int(args.min_price * 100)
    if args.max_price:
        max = int(args.max_price * 100)

    items_file_name = 'items.json'
    if os.path.exists(items_file_name):
        os.remove(items_file_name)

    scanner = MercariScanner(args.keyword, min, max, args.delay, items_file_name, alerters)
    scanner.start()


if __name__ == "__main__":
    main()
