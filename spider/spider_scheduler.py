#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-8-8

from page_downloader import aispider
from html_parser import parser
from data_save import pipeline

from threads_use_tag import start, work_queue, format_put_data, url_content_queue
from log_format import logger


class SpiderMain(object):
    def __init__(self):
        self.logger = logger
        self.downloader = aispider
        self.parser = parser
        self.pipeline = pipeline

    def craw(self, root_url):
        put_data = format_put_data(args={"url": root_url}, work_func=self.downloader.request, tag='to_get_url')
        work_queue.put(put_data)

        html_cont = url_content_queue.get()
        news_links_pattern = '(http://[a-z]+.163.com/\d+/\d+/\d+/.*?.html)'
        news_links = self.parser.get_data_by_re(html_cont, news_links_pattern)
        self.get_detail_url(news_links)

    def get_detail_url(self, urls):
        for url in urls:
            put_data = format_put_data(args={"url": url}, work_func=self.downloader.request, tag='to_get_data',
                                       need_save=True, save_func=self.save)
            work_queue.put(put_data)

    def save(self, content, url):
        collection_name = 'for_save_test'
        save_data_dict = {}
        news_title_xpath = '//div[@id="epContentLeft"]/h1/text()'
        news_title = self.parser.get_data_by_xpath(content.decode('gbk', 'ignore'), news_title_xpath)

        save_data_dict['_id'] = url
        save_data_dict['title'] = news_title[0] if news_title else ''

        self.pipeline.process_item(save_data_dict, collection_name)


def go():
    start()
    root_url = 'http://www.163.com/'
    obj_spider = SpiderMain()
    obj_spider.craw(root_url)


if __name__ == '__main__':

    go()

