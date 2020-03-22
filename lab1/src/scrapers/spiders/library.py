# -*- coding: utf-8 -*-
from scrapy.http.response import Response
import scrapy


class LibrarySpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['uartlib.org']
    start_urls = ['http://uartlib.org/']

    def parse(self, response: Response):
        all_images = response.xpath("//img/@src[starts-with(., 'http')]")
        all_text = response.xpath("//a[@class='_blank cvplbd']/text()")
        yield {
            'url': response.url,
            'payload': [{'type': 'text', 'data': text.get().strip()} for text in all_text] +
                       [{'type': 'image', 'data': image.get()} for image in all_images]
        }
        if response.url == self.start_urls[0]:
            all_links = response.xpath(
                "//a/@href[starts-with(., 'http://uartlib.org/')]")
            selected_links = [link.get() for link in all_links][:19]
            for link in selected_links:
                yield scrapy.Request(link, self.parse)
