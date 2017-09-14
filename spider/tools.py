#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-9-14

def isThreadAlive(threads):
    count = 0
    for t in threads:
        if t.isAlive():
            count += 1
    return count
