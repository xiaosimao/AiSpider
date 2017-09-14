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

# work_threading count
work_threading_count = []
save_threading_count = []

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
            # 工作函数
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
        work_threading_count.append(get_work_thread)
        get_work_thread.setDaemon(True)
        get_work_thread.start()

    for i in range(thread_num * 2):
        get_save_thread = threading.Thread(target=get_save_queue)
        save_threading_count.append(get_save_thread)

        get_save_thread.setDaemon(True)
        get_save_thread.start()

    show_size_thread = threading.Thread(target=show_size)
    show_size_thread.setDaemon(True)
    show_size_thread.start()

    save_queue.join()


def handle_thread_exception(func, _dict):
    try:
        func(_dict)
    except Exception, e:
        msg = 'ERROR INFO in {func}: {e}'.format(func=func, e=e)
        logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))


def show_size():
    while 1:
        if not work_queue.empty() or not save_queue.empty():
            msg = 'AT %s ,work queue size is [%d]' % (time.strftime('%Y-%m-%d %H:%M:%S'), work_queue.qsize())
            logger.info(msg)

            msg = 'AT %s ,save queue size is [%d]' % (time.strftime('%Y-%m-%d %H:%M:%S'), save_queue.qsize())
            logger.info(msg)

            msg = 'work active threading count is [%d]' % (len(work_threading_count))
            logger.info(msg)

            msg = 'save active threading count is [%d]' % (len(save_threading_count))
            logger.info(msg)

            time.sleep(5)


def format_error_msg(file_name, func_name, error_msg):
    error_info = '''
    detail_error_info
    ##################
    file_name: {},
    func_name: {},
    error_msg: {}
    ##################
    '''.format(file_name, func_name, error_msg)
    return error_info


def format_put_data(args, work_func, dont_filter=False, follow_func=None, tag=None, need_save=True, save_func=None,
                    meta=None):
    put_data = {'args': args,
                'work_func': work_func,
                'follow_func': follow_func,
                'dont_filter': dont_filter,
                'tag': tag,
                'need_save': need_save,
                'save_func': save_func,
                'meta': meta
                }

    # args
    if not isinstance(args, dict) or not args:
        msg = 'IN [put_data], args has to be dict and can not be empty, please check, exiting......'

        logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))

        os._exit(0)
    elif 'url' not in args.keys():
        msg = 'IN [put_data], url has to be a key in args and can not be modified ,please check, exiting......'
        logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))
        os._exit(0)

    # work_func
    if work_func is None or not callable(work_func):
        msg = 'IN [put_data], work_func has to be defined and must be callable ,please check, exiting......'
        logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))
        os._exit(0)

    # meta
    if meta and not isinstance(meta, dict):
        msg = 'meta has to be dict while you defined it ,please check, exiting......'
        logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))
        os._exit(0)

    # save_func
    if save_func and not callable(save_func):
        msg = 'IN [put_data], save has to be callable while you define it ,please check, exiting......'
        logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))
        os._exit(0)

    return put_data
