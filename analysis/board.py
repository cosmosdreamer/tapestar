# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, '../stock/')
#print sys.path

import stockdata
from datetime import date, datetime, timedelta
import tushare as ts

c_highlight_blue = '\033[1;34;40m'
c_highlight_red = '\033[1;31;40m'
c_highlight_green = '\033[1;32;40m'
c_default_white = '\033[0;37;40m'
c_reset = '\033[0m'

group_data = {}
all_stocks = stockdata.all_stocks_1

def group_stock(stock):
    if stock['code'].startswith('30'):
        return '深市创业板'
    elif stock['code'].startswith('000'):
        return '深市主板'
    elif stock['code'].startswith('002'):
        return '深市中小板'
    elif stock['code'].startswith('60'):
        return '沪市    '
    elif stock['code'].startswith('510'):
        return 'ETF     '
    elif stock['code'].startswith('150') or stock['code'].startswith('502'):
        return '分级基金'
    else:
        raise Exception('这是啥？ ' + stock['code'])

def calc_stock(stock):
    vest = 0
    if stock.has_key('trades'):
        for trade in stock['trades']:
            if trade[1] == 1:
                vest += trade[2] * trade[3]
    return vest

def display_stock_group(group, all_vest):
    for stock in all_stocks:
        if stock['group'] == group:
            ratio = stock['vest'] * 100 / all_vest
            color = c_default_white
            if ratio == 0:
                color = c_highlight_red
            elif ratio < 3:
                color = c_highlight_blue
            elif ratio > 8:
                color = c_highlight_green
            print '  %s %s:\t%s%4.1f%%%s\t\t%s' % (stock['code'], stock['name'], color, ratio, c_reset, str(stock['vest']))

def calc():
    all_vest = 0
    for stock in all_stocks:
        dg = ts.get_realtime_quotes(stock['code'])
        stock['name'] = dg['name'][0]
        group = stock['group'] = group_stock(stock)
        vest = stock['vest'] = calc_stock(stock)
        if not group_data.has_key(group):
            group_data[group] = 0
        else:
            group_data[group] += vest
        all_vest += vest
    for data in group_data.keys():
        print '%s:\t\t%4.1f%%\t\t%s' % (data,  group_data[data] * 100 / all_vest, str(group_data[data]))
        display_stock_group(data, all_vest)
    print 'all: ' + str(all_vest)

if __name__ == '__main__':
    calc()
#
