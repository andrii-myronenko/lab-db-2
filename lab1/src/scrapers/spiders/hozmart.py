# -*- coding: utf-8 -*-
from scrapy.http.response import Response
import scrapy


class HozmartSpider(scrapy.Spider):
    name = 'hozmart'
    allowed_domains = ['www.hozmart.ua']
    start_urls = ['https://www.hozmart.com.ua/uk/953-zapchastini-do-elektropil-stihl']

    def parse(self, response: Response):
        products = response.xpath("//div[contains(@class, 'cell item')]")[:20]
        for product in products:
            yield {
                'description': product.xpath("./h3/a[@class='b1c-name-uk']/text()").get(),
                'price': product.xpath("substring-before(./p[contains(@class, 'b1c-withoutprice')]/text(),' грн.')").get(),
                'img': product.xpath("./div/a/img[@id='product']/@src[starts-with(., 'https')]").get()
            }
