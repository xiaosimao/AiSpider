#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-8-8
import urlparse
import requests
import time
import random
from log_format import logger
from UAS import *
from config import *
import hashlib
from pybloom import ScalableBloomFilter
import os

request_session = requests.Session()

sbf = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH, error_rate=0.000001)


class AiSpider(object):
    def __init__(self):
        self.log = logger
        self.status_code = status_code
        self.has_requested = set()
        self.sleep_time = sleep_time
        self.time_out = time_out
        self.use_proxy = use_proxy
        self.ua_type = ua_type
        self.diy_header = diy_header
        self.retry_times = retry_times
        self.ip = ip
        self.method = 'get'
        self.submit_data = None

    def md5_url(self, url):

        # 摘要算法
        md5 = hashlib.md5()
        md5.update(url)
        return md5.hexdigest()

    def check(self, url):
        url = self.md5_url(url)
        if url not in sbf:
            return True
        else:
            return False

    def request(self, _args, dont_filter):
        url = _args.get('url')
        sleep_time = _args.get('sleep_time') if _args.get('sleep_time') else self.sleep_time
        time_out = _args.get('time_out') if _args.get('time_out') else self.time_out
        retry_times = _args.get('retry_times') if _args.get('retry_times') else self.retry_times
        use_proxy = _args.get('use_proxy') if _args.get('use_proxy') else self.use_proxy
        _ip = _args.get('ip') if _args.get('ip') else self.ip
        ua_type = _args.get('ua_type') if _args.get('ua_type') else self.ua_type
        diy_header = _args.get('diy_header') if _args.get('diy_header') else self.diy_header
        method = _args.get('method') if _args.get('method') else self.method
        post_data = _args.get('submit_data') if _args.get('submit_data') else self.submit_data

        if not dont_filter:
            check_result = self.check(url)
            if not check_result:
                return 'HAS CRAWLED', url
            else:
                msg = 'new url'
                logger.info(msg)

        if not url.startswith('http'):
            raise ValueError('url has to be started with http or https')
        if diy_header:
            header = diy_header
        else:
            host = urlparse.urlparse(url).netloc
            header = {
                'User-Agent': random.choice(PC_USER_AGENTS),
                'Host': host,
            }

            if ua_type == 'mobile':
                header = {
                    'User-Agent': random.choice(MOBILE_USER_AGENTS),
                    'Host': host
                }

        times = 0
        con = None
        while retry_times > 0:
            times += 1
            self.log.info('request %s, times: %d' % (url, times))
            try:
                if use_proxy:
                    ip = _ip
                    if ip:
                        proxy = {
                            'http': 'http://%s' % ip,
                            'https': 'http://%s' % ip
                        }
                        if method == 'get':
                            con = request_session.get(url, headers=header, proxies=proxy, timeout=time_out, params=post_data, verify=False)
                        elif method == 'post':
                            if post_data and isinstance(post_data, dict):
                                con = request_session.post(url, headers=header, proxies=proxy, timeout=time_out, data=post_data, verify=False)
                            else:
                                self.log.error('while method is post, post_data must be defined and defined as dict')

                        if con.status_code not in self.status_code:
                            self.log.error('status code is %s' % con.status_code)
                            raise ValueError('status code not in the code in config.py, check your log')
                        time.sleep(sleep_time)
                    else:
                        msg = 'ip can not be none while use_proxy is True'
                        self.log.error(msg)
                        os._exit(0)

                else:
                    if method == 'get':
                        con = request_session.get(url, headers=header, timeout=time_out, params=post_data, verify=False)
                    elif method == 'post':
                        if post_data and isinstance(post_data, dict):
                            con = request_session.post(url, headers=header, timeout=time_out, data=post_data, verify=False)
                        else:
                            self.log.error('while method is post, post_data must be defined and defined as dict')
                            os._exit(0)

                    if con.status_code not in self.status_code:
                        self.log.error('status code is %s' % con.status_code)
                        raise ValueError('status code not in the code in config.py, check your log')
                    time.sleep(sleep_time)

            except Exception, e:
                self.log.error(e)
                retry_times -= 1
                self.log.warning('retrying request: [%s], times: %s' % (url, times))
                if times == 10:
                    self.log.error('give up retrying request: [%s], times: %s is bigger than setting' % (url, times))
                    return None, None
            else:
                self.log.info('[%s] has requested successfully' % url)

                if con:
                    if not dont_filter:
                        url = self.md5_url(url)
                        sbf.add(url)

                    return con.content, con.url
                else:
                    self.log.error('content is None, url is %s' % url)
                    return None, None


aispider = AiSpider()
