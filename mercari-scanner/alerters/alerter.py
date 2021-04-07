import threading
import time
import json
import os.path
import logging
import collections

log = logging.getLogger(__name__)


class Alerter:
    def __init__(self, alerters, item_file_name, check_interval, tiers):
        self.alerters = alerters
        self.item_file_name = item_file_name
        self.check_interval = check_interval
        self.tiers = collections.OrderedDict(sorted(tiers.items()))
        self.items = {}
        self.latch = False

    def _check(self):
        if not os.path.exists(self.item_file_name):
            log.warn(f"no file named {self.item_file_name} found")
            return
        if os.stat(self.item_file_name).st_size == 0:
            return

        with open(self.item_file_name, 'r') as f:
            items = json.load(f)
            for item in items:
                if item['id'] not in self.items.keys():
                    msg = self._build_message(item)
                    log.info(f"new item found: {item['name']}, price: {item['price']}")

                    if self.latch:  # don't alert on the first sweep
                        for alerter in self.alerters:
                            alerter.alert(msg)

                    self.items[item['id']] = item
        self.latch = True

    def _build_message(self, item):
        name = item['name']
        price = item['price']
        url = item['url']
        newline = '\n'

        for threshold, template in self.tiers.items():
            if price <= threshold:
                return template.format(**locals())

        return f"New item found! :money_with_wings: ${price} :money_with_wings: {name}{newline}{url}"

    def _keep_checking(self):
        while True:
            self._check()
            time.sleep(self.check_interval)

    def start(self):
        thread = threading.Thread(target=self._keep_checking, daemon=True)
        thread.start()
