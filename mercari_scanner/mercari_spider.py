
import scrapy
import re
from twisted.internet import reactor


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
        for item in response.css('div.Flex__Box-ych44r-1'):
            url = item.css('div.Flex__Box-ych44r-1 a::attr(href)').get()
            item_id = self._parse_id(url)
            name = item.css('div.withMetaInfo__EllipsisText-sc-1j2k5ln-12::text').get()
            price = self._parse_price(item)

            if name and price:
                yield {
                    'id': item_id,
                    'name': name,
                    'url': f"{self.base_url}{url}",
                    'price': price
                }

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
        discounted_price = item.css('span.withMetaInfo__DiscountPrice-sc-1j2k5ln-9::text').re(r'\d+,?\d*')
        price = item.css('span.withMetaInfo__Price-sc-1j2k5ln-3::text').re(r'\d+,?\d*')
        best_price = None
        if discounted_price:
            best_price = discounted_price[0].replace(',', '')
        elif price:
            best_price = price[0].replace(',', '')
        return best_price

    def _parse_id(self, url):
        item_id = re.search(r'item/(.\d+)/', str(url))
        if item_id:
            item_id = item_id.group(1)
        return item_id
