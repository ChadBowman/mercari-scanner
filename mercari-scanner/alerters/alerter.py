import threading
import time
import json
import os.path
import logging

log = logging.getLogger(__name__)


class Alerter:
    def __init__(self, alerters, item_file_name, check_interval):
        self.alerters = alerters
        self.item_file_name = item_file_name
        self.check_interval = check_interval
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
                    log.info(f"new item found: {item['name']}, price: {item['price']}")
                    if self.latch:  # dont alert on the first sweep
                        for alerter in self.alerters:
                            s = '\n'.join([f"New item found! :money_with_wings: ${item['price']} :money_with_wings: {item['name']}",
                                           f"{item['url']}"])
                            alerter.alert(s)
                    self.items[item['id']] = item
        self.latch = True

    def _keep_checking(self):
        while True:
            self._check()
            time.sleep(self.check_interval)

    def start(self):
        thread = threading.Thread(target=self._keep_checking, daemon=True)
        thread.start()


if __name__ == "__main__":
    class B:
        def alert(self):
            pass

    a = Alerter([B()])
    a.start()
