import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from goldmansachs.items import Article


class GoldmansachsSpider(scrapy.Spider):
    name = 'goldmansachs'
    start_urls = ['https://www.goldmansachs.com/insights/series/briefly/index.html']

    def parse(self, response):
        links = response.xpath('//a[@class="title-link-hover"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="article-content-page__date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="article-content-page__content"]//text()').getall()
        content = [text for text in content if text.strip() and "BRIEFINGS" not in text
                   and "The article below" not in text and "newsletter of" not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
