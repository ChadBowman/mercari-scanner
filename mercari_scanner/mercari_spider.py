import logging
import scrapy
import re
from twisted.internet import reactor

log = logging.getLogger(__name__)


class MercariSpider(scrapy.Spider):
    name = 'mercarispider'
    base_url = 'https://www.mercari.com'

    def __init__(self, *args, **kwargs):
        self.timeout = int(kwargs.pop('timeout', '60'))
        super(MercariSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        reactor.callLater(self.timeout, self.stop)
        urls = [self._build_url()]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def stop(self):
        """ Gracefully stops the crawler and returns a deferred tath is fired
        whe the crawler is stopped
        """
        if self.crawling:
            self.crawling = False
            yield reactor.maybeDeferred(self.engine.stop)

    def parse(self, response):
        # each item on page contains "Grid2__Col" in its div class
        # TODO use selector to avoid future breakage
        items = response.css('div.Grid2__Col-mpt2p4-0')
        if not items:
            log.warn('No items found! It is highly possible that we need to use a selector to source '
                     'items. If this happens for each search, please report this as a bug')

        for item in items:
            # TODO use selector to avoid future breakage
            url = item.css('div.Flex__Box-ych44r-1 a::attr(href)').get()
            item_id = self._parse_id(url)
            # TODO use selector to avoid future breakage
            name = item.css('div.Flex__Box-ych44r-1 a::attr(alt)').get()
            price = self._parse_price(item)

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
        keyword = f"keyword={self.settings.get('mercari.keyword')}"
        min_price = None
        max_price = None
        if self.settings.get('mercari.min_price'):
            min_price = f"minPrice={self.settings.get('mercari.min_price')}"
        if self.settings.get('mercari.max_price'):
            max_price = f"maxPrice={self.settings.get('mercari.max_price')}"
        sort = 'sortBy=2'  # newest
        for_sale = 'itemStatuses=1'  # for sale
        params = filter(None, [keyword, min_price, max_price, sort, for_sale])
        return f"{self.base_url}/search?{'&'.join(params)}"

    def _parse_price(self, item):
        discount_selector = './/span[contains(@class, "withMetaInfo__DiscountPrice")]/text()'
        discounted_price = item.xpath(discount_selector).getall()

        price_selection = './/span[contains(@class, "withMetaInfo__Price")]/text()'
        price = item.xpath(price_selection).getall()
        best_price = None

        # if the price is discounted, the normal price will not be present
        if discounted_price:
            # discounted_price has two elements. One for '$' and another for the price
            best_price = discounted_price[1].replace(',', '')
        elif price:
            best_price = price[1].replace(',', '')
        return best_price

    def _parse_id(self, url):
        item_id = re.search(r'item/(.\d+)/', str(url))
        if item_id:
            item_id = item_id.group(1)
        return item_id
