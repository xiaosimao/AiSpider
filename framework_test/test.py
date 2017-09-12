#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-9-12
import sys
sys.path.append('/home/shimeng/code/spider_framework_github_responsity')
from spider.data_save import pipeline
from spider.html_parser import parser
from spider.page_downloader import aispider
from spider.threads import start, work_queue, format_put_data
from spider.log_format import logger


root_url_format = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_album.fcg?g_tk=676629472&loginUin=549411552&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&singermid={singermid}&order=time&begin={begin}&num={num}&exstatus=1'

class SpiderMain(object):
    def __init__(self):
        self.logger = logger
        self.downloader = aispider
        self.parser = parser
        self.pipeline = pipeline

    def craw(self, singer_mids, begin=0, num=1):
        for singer_mid in singer_mids:
            url = root_url_format.format(singermid=singer_mid, begin=begin, num=num)
            put_data = format_put_data(args={"url": url}, work_func=self.downloader.request, follow_func=self.get_total_num,
                                        )
            work_queue.put(put_data)
            # self.get_total_num()

    def get_total_num(self, response):
        html_content = response.get('content')

        datas = parser.get_data_by_json(html_content)
        total_num = datas.get('data').get('total','')

        if total_num:
            singer_mid = datas.get('data').get('singer_mid')
            url = root_url_format.format(singermid=singer_mid, begin=0, num=total_num)
            put_data = format_put_data(args={"url": url}, work_func=self.downloader.request, tag='to_get_data',
                                       need_save=True, save_func=self.save)
            work_queue.put(put_data)

    def save(self, response):

        collection_name = 'qq_music_album_base_info'
        html_content = response.get('content')
        datas = parser.get_data_by_json(html_content)
        data = datas.get('data').get('list')
        if data:
            for da in data:
                insert_data = da
                insert_data['singer_id'] = datas.get('data').get('singer_id')
                insert_data['singer_mid'] = datas.get('data').get('singer_mid')
                insert_data['singer_name'] = datas.get('data').get('singer_name')
                insert_data['total'] = datas.get('data').get('total')

                insert_data['_id'] = da.get('albumID')

                print insert_data

                # self.pipeline.process_item(insert_data, collection_name)


def get_singer_mid():
    import pymongo
    client = pymongo.MongoClient('10.12.8.18', 27017)
    db = client['DUI_JIE_DATA']
    collection = db['qq_music_singer_base_info']
    singer_mids = []
    for u in collection.find():
        singer_mid = u.get('Fsinger_mid')
        singer_mids.append(singer_mid)
    return singer_mids[:20]


def go(singer_mids):
    start()
    obj_spider = SpiderMain()
    obj_spider.craw(singer_mids)
    work_queue.join()

if __name__ == '__main__':
    # singer_mids = get_singer_mid()
    singer_mids = ['0025NhlN2yWrP4']

    go(singer_mids)
