import os
import sys
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


class HelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}" + '\n')
        self.print_help()
        sys.exit(2)


def parse_args():
    parser = HelpParser()
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


def parse_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def build_alerters(config):
    alerters = []
    if config.has_section('slack'):
        token = config['slack']['token']
        channel = config['slack']['channel']
        if token == 'xoxb-blah-blah':
            log.warn('Please provide your own Slack API token')
        else:
            slack = SlackAlerter(token, channel)
            alerters.append(slack)
    else:
        log.info('No Slack configuration detected')

    if not alerters:
        log.warn('No alerters configured')

    return alerters


def alert(alerters, message):
    for alerter in alerters:
        alerter.alert(message)


def remove_file(file_name):
    if file_name and os.path.exists(file_name):
        os.remove(file_name)


def main():
    items_file_name = None
    alerters = []
    try:
        config = parse_config()
        args = parse_args()
        alerters = build_alerters(config)

        min = None
        max = None
        if args.min_price:
            min = int(args.min_price * 100)  # multiplied by 100 because Mercari search uses pennies
        if args.max_price:
            max = int(args.max_price * 100)

        items_file_name = f"{hash(args.keyword)}.json"
        remove_file(items_file_name)
        alert(alerters, f":scan: {args.keyword} scanning started")
        scanner = MercariScanner(args.keyword, min, max, args.delay, items_file_name, alerters)
        scanner.start()
    except Exception as e:
        alert(alerters, f":warning: unhandled exception: {e}")
    finally:
        remove_file(items_file_name)
        if alerters and args:
            alert(alerters, f":octagonal_sign: {args.keyword} scanning stopped")


if __name__ == "__main__":
    main()
