#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-8-8

import pymongo
from config import *
from log_format import logger


class Pipeline(object):

    def __init__(self):
        self.host = host
        self.port = port
        self.database = database_name
        if connect:
            self._connect()

    def _connect(self):

        self.client = pymongo.MongoClient(self.host,self.port)
        self.db = self.client[self.database]

    def process_item(self, item, collection_name, use_id=True):
        collection = self.db[collection_name]
        # msg = 'insert data into collection: [%s]' %collection_name
        # logger.info(msg)
        if use_id:
            collection.update({'_id':item['_id']}, dict(item), True)
        else:
            collection.insert(dict(item))

        # self.client.close()

pipeline = Pipeline()