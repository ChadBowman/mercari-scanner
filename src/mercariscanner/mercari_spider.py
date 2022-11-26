import logging
import scrapy
import json
from twisted.internet import reactor
from urllib import parse

log = logging.getLogger(__name__)


class MercariSpider(scrapy.Spider):
    name = 'mercarispider'
    base_url = 'https://www.mercari.com'
    custom_settings = {
        "COOKIES_ENABLED": False
    }

    def __init__(self, *args, **kwargs):
        self.timeout = int(kwargs.pop('timeout', '60'))
        super(MercariSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        headers = {
            "authority": "www.mercari.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,de;q=0.8,ko;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache",
            "sec-ch-ua": "\"Google Chrome\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mac OS X/10.6.8 (10K549); ExchangeWebServices/1.3 (61); Mail/4.6 (1085)",
        }
        reactor.callLater(self.timeout, self.stop)
        urls = [self._build_url()]
        for url in urls:
            yield scrapy.Request(url=url, method='GET', dont_filter=True, headers=headers)

    def stop(self):
        """ Gracefully stops the crawler and returns a deferred tath is fired
        whe the crawler is stopped
        """
        if self.crawling:
            self.crawling = False
            yield reactor.maybeDeferred(self.engine.stop)

    def parse(self, response):
        items = json.loads(response.text).get("data", None).get("search", None).get("itemsList", None)
        if not items:
            log.warn('No items found!')

        for item in items:
            item_id = item["id"]
            url = f"/us/item/{item_id}"
            name = item["name"]
            price = item["price"]

            if url and item_id and name and price:
                yield {
                    'id': item_id,
                    'name': name,
                    'url': f"{self.base_url}{url}",
                    'price': price
                }
            else:
                log.error(f'Unable to parse fields, id: {id} name: {name} url: {url} price: {price}')

    def _build_url(self):
        keyword = parse.quote(self.settings.get('mercari.keyword'))
        min_price = ""
        max_price = ""
        if self.settings.get('mercari.min_price'):
            min_price = f"%2C%22minPrice%22%3A{self.settings.get('mercari.min_price')}"
        if self.settings.get('mercari.max_price'):
            max_price = f"%2C%22maxPrice%22%3A{self.settings.get('mercari.max_price')}"
        sort = '2'  # newest
        item_status = '1'  # for sale
        return f"{self.base_url}/v1/api?operationName=searchFacetQuery&variables=%7B%22criteria%22%3A%7B%22offset%22%3A0%2C%22soldItemsOffset%22%3A0%2C%22promotedItemsOffset%22%3A0%2C%22sortBy%22%3A{sort}%2C%22length%22%3A30%2C%22query%22%3A%22{keyword}%22%2C%22itemConditions%22%3A%5B%5D%2C%22shippingPayerIds%22%3A%5B%5D%2C%22sizeGroupIds%22%3A%5B%5D%2C%22sizeIds%22%3A%5B%5D%2C%22itemStatuses%22%3A%5B{item_status}%5D%2C%22customFacets%22%3A%5B%5D%2C%22facets%22%3A%5B1%2C2%2C3%2C5%2C7%2C8%2C9%2C10%2C11%2C13%5D%2C%22authenticities%22%3A%5B%5D%2C%22deliveryType%22%3A%22all%22%2C%22state%22%3Anull%2C%22locale%22%3Anull%2C%22shopPageUri%22%3Anull%2C%22withCouponOnly%22%3Anull{min_price}{max_price}%7D%2C%22categoryId%22%3A0%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22a234c160e270e63c7689739e191d207884eea0c46f344b66a17a59bcc7f725fa%22%7D%7D"
