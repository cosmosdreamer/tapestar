
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, '../stock/')
#print sys.path

import stockdata
from datetime import date, datetime, timedelta
import tushare as ts

# print stockdata.all_stocks

def parse_args():
    global g_arg_simplified
    if len(sys.argv) >= 2 and sys.argv[1] == '-s':
        g_arg_simplified = True


