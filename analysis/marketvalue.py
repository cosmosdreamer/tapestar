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

def log_status(message):
    print message

def group_stock(stock):
    if stock['marketvalue'] == 0:
        return 'Unknown'
    elif stock['marketvalue'] < 80:
        return '< 80亿'
    elif stock['marketvalue'] < 160:
        return '< 160亿'
    elif stock['marketvalue'] < 320:
        return '< 320亿'
    elif stock['marketvalue'] < 1000:
        return '< 1000亿'
    else:
        return '>= 1000亿'

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
            print '  %s %s:\t%s%4.1f%%%s\t\t%s\t%s' % (stock['code'], stock['name'], color, ratio, c_reset, str(stock['vest']), str(stock['marketvalue']))

def calc():
    all_vest = 0
    for stock in all_stocks:
        code = stock['code']
        dg = ts.get_realtime_quotes(stock['code'])
        df = None
        d = date.today()
        count = 0
        while (df is None or df.empty) and count < 10:
            count += 1
            d = d - timedelta(days=1)
            datestr = d.strftime('%Y-%m-%d')
            log_status('Getting hist data for %s at %s' % (code, datestr))
            df = ts.get_hist_data(stock['code'], datestr, datestr)
            log_status('Done hist data for %s at %s' % (code, datestr))
        stock['name'] = dg['name'][0]
        if (df is None or df.empty) or df.get('turnover') is None:
            stock['marketvalue'] = 0
        else:
            stock['marketvalue'] = float(df['close'][0]) * float(df['volume'][0]) * 100 / (float(df['turnover'][0] / 100)) / 100000000
        group = stock['group'] = group_stock(stock)
        vest = stock['vest'] = calc_stock(stock)
        if not group_data.has_key(group):
            group_data[group] = vest
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
