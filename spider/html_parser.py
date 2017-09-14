#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-8-8

import re
import json
import lxml.html as H
from log_format import logger
import inspect
from tools import format_error_msg


class HtmlParser(object):
    """
    解析: re 或 xpath 或 json
    在这里只提供接口

    """

    def __init__(self, ):
        self.logger = logger

    # xpath
    def get_data_by_xpath(self, html_page_source, urls_xpath):
        try:
            self.doc = H.document_fromstring(html_page_source)
        except Exception, e:
            msg = 'Error msg: %s in [get_data_by_xpath]' % e
            self.logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))
        else:
            data = self.doc.xpath(urls_xpath)
            return data

    # re
    def get_data_by_re(self, html_page_source, pattern, flags=re.DOTALL):
        try:
            data = re.findall(pattern, html_page_source, flags=flags)
        except Exception, e:
            msg = 'Error msg: %s in [get_data_by_re]' % e
            self.logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))

        else:
            return data

    # json
    def get_data_by_json(self, html_page_source):
        try:
            data = json.loads(html_page_source)
        except Exception, e:
            msg = 'Error msg: %s in [get_data_by_json]' % e
            self.logger.error(format_error_msg(inspect.stack()[1][1], inspect.stack()[1][3], msg))

        else:
            return data


parser = HtmlParser()
