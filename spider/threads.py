#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-8-11

import threading
import Queue
import time
import os
from config import *
from log_format import logger
import inspect
import tools

# work_threading count
work_threading_list = []
save_threading_list = []

# 两种队列  先进先出
fifo = FIFO

if fifo:
    work_queue = Queue.Queue()
    save_queue = Queue.Queue()
    url_content_queue = Queue.Queue()
else:
    work_queue = Queue.LifoQueue()
    save_queue = Queue.LifoQueue()
    url_content_queue = Queue.LifoQueue()


def get_work_queue():
    """
    工作队列
    """
    while 1:
        if not work_queue.empty():
            _dict = work_queue.get()

            if not isinstance(_dict, dict):
                msg = 'put queue data is not dict,please check'
                raise ValueError(msg)
            # 参数
            _args = _dict.get('args')
            # 工作函数即请求函数
            work_func = _dict.get('work_func')

            # 是否过滤
            dont_filter = _dict.get('dont_filter')

            content, url = work_func(_args, dont_filter)

            if content is not None:
                if content == 'HAS CRAWLED':
                    logger.warning('%s has crawled' % url)
                else:
                    _dict['content'] = content
                    _dict['url'] = url

                    follow_func = _dict.get('follow_func')
                    save_func = _dict.get('save_func')

                    if follow_func:
                        handle_thread_exception(follow_func, _dict)

                    if save_func:
                        save_queue.put(_dict)

            work_queue.task_done()


def get_save_queue():
    """
    保存队列
    """
    while 1:
        if not save_queue.empty():
            _dict = save_queue.get()
            save_func = _dict.get('save_func')
            handle_thread_exception(save_func, _dict)
            save_queue.task_done()


def start(thread_num=thread_num):
    for i in range(thread_num):
        get_work_thread = threading.Thread(target=get_work_queue)
        work_threading_list.append(get_work_thread)
        get_work_thread.setDaemon(True)
        get_work_thread.start()

    for i in range(thread_num * 2):
        get_save_thread = threading.Thread(target=get_save_queue)
        save_threading_list.append(get_save_thread)
        get_save_thread.setDaemon(True)
        get_save_thread.start()

    show_size_thread = threading.Thread(target=show_size)
    show_size_thread.setDaemon(True)
    show_size_thread.start()


def handle_thread_exception(func, _dict):
    try:
        func(_dict)
    except Exception, e:
        msg = 'ERROR INFO in {func}: {e}'.format(func=func, e=e)
        logger.error(tools.format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))


def show_size():
    while 1:
        if not work_queue.empty() or not save_queue.empty():
            msg = 'AT %s ,work queue size is [%d]' % (time.strftime('%Y-%m-%d %H:%M:%S'), work_queue.qsize())
            logger.info(msg)

            msg = 'AT %s ,save queue size is [%d]' % (time.strftime('%Y-%m-%d %H:%M:%S'), save_queue.qsize())
            logger.info(msg)

            msg = 'work threading total count is [%d], active count is [%d]' % (
                len(work_threading_list), tools.isThreadAlive(work_threading_list))
            logger.info(msg)

            msg = 'save threading total count is [%d], active count is [%d]' % (
                len(save_threading_list), tools.isThreadAlive(save_threading_list))
            logger.info(msg)

            time.sleep(2)
