#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-9-12
# 导入模块
import sys

# 这里写你自己的地址
sys.path.append('/home/shimeng/code/spider_framework_github_responsity')

from spider.tools import format_put_data
from spider.data_save import pipeline
from spider.html_parser import parser
from spider.page_downloader import aispider
from spider.threads import start, work_queue, save_queue
from spider.log_format import logger

root_url_format = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_album.fcg?g_tk=676629472&loginUin=549411552&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&singermid={singermid}&order=time&begin={begin}&num={num}&exstatus=1'


# 定义主程序
class SpiderMain(object):
    def __init__(self):
        self.logger = logger
        self.downloader = aispider
        self.parser = parser
        self.pipeline = pipeline

    def craw(self, singer_mids, begin=0, num=1):
        for singer_mid in singer_mids:
            url = root_url_format.format(singermid=singer_mid, begin=begin, num=num)
            # 调用format_put_data 构造放入队列中的数据 
            put_data = format_put_data(args={"url": url, 'method': 'get', 'submit_data': None},
                                       work_func=self.downloader.request,
                                       follow_func=self.get_total_num)
            # 放入队列
            work_queue.put(put_data)

    # 这个函数就是上一步中定义的follow_func
    def get_total_num(self, response):
        #  获取请求的内容
        html_content = response.get('content')
        # 调用解析方法
        datas = parser.get_data_by_json(html_content)
        total_num = datas.get('data').get('total', '')

        if total_num:
            singer_mid = datas.get('data').get('singer_mid')
            url = root_url_format.format(singermid=singer_mid, begin=0, num=total_num)
            # 再次调用format_put_data方法构造将要放入工作队列中的数据
            put_data = format_put_data(args={"url": url}, work_func=self.downloader.request, need_save=True,
                                       save_func=self.save)
            work_queue.put(put_data)

    # 上一步中定义的保存函数
    def save(self, response):
        # ｍｏｎｇｏｄｂ集合名称
        collection_name = 'qq_music_album_base_info'
        html_content = response.get('content')
        datas = parser.get_data_by_json(html_content)
        data = datas.get('data').get('list')
        if data:
            for da in data:
                print da
                insert_data = da
                insert_data['singer_id'] = datas.get('data').get('singer_id')
                insert_data['singer_mid'] = datas.get('data').get('singer_mid')
                insert_data['singer_name'] = datas.get('data').get('singer_name')
                insert_data['total'] = datas.get('data').get('total')
                insert_data['_id'] = da.get('albumID')

                # 　保存数入库　
                # self.pipeline.process_item(insert_data, collection_name)


def go(singer_mids):
    start()
    obj_spider = SpiderMain()
    obj_spider.craw(singer_mids)


if __name__ == '__main__':
    singer_mids = ['0025NhlN2yWrP4']
    go(singer_mids)

    # blocking, 这里必须这么写
    work_queue.join()
    save_queue.join()
    print 'done'
