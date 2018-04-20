# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, '../stock/')
#print sys.path

import stockdata
from datetime import date, datetime, timedelta
import tushare as ts

all_stocks = stockdata.all_stocks_1

# print stockdata.all_stocks

def compPChange(stockX, stockY):
    return -1 * int(100 * (stockX['pChangeTotal'] - stockY['pChangeTotal']))

def compCloseChange(stockX, stockY):
    return -1 * int(100 * (stockX['closeChangeTotal'] - stockY['closeChangeTotal']))

def calc():
    changes = []
    count = 0
    for stock in all_stocks:
        count += 1
        #if count > 5:
        #    break
        code = stock['code']
        #df = get_dataOfYear(code, 2016)
        df = get_dataOfMonths(code, 4)
        dg = ts.get_realtime_quotes(code)
        print 'Got data of code %s' % (code)
        change = { 'code': code, 'name': dg['name'][0], 'pChangeTotal': 0, 'closeChangeTotal': 0 }
        pre_close = 0
        if df is not None:
            for i in range(0, len(df)):
                pChange = (df['high'][i] - df['low'][i]) / df['close'][i]
                change['pChangeTotal'] += pChange
                if pChange > 0.2:
                    print pChange
                if pre_close > 0:
                    closeChange = abs(df['close'][i] - pre_close) / pre_close
                    if closeChange <= 0.12:
                        change['closeChangeTotal'] += closeChange
                #if closeChange > 0.12:
                    #print '%7.2f %s %s\t%s' % (closeChange, change['code'], change['name'], df.iloc[i])
                pre_close = df['close'][i]
            changes.append(change)
    changes.sort(compPChange)
    print '\n pChange:'
    for change in changes:
        print '%s %s\t %7.2f' % (change['code'], change['name'], change['pChangeTotal'])
    changes.sort(compCloseChange)
    print '\n closeChange:'
    for change in changes:
        print '%s %s\t %7.2f' % (change['code'], change['name'], change['closeChangeTotal'])
    print '\n\nEnjoy.\n'

def get_dataOfYear(code, year):
    start = '%d-08-01' % (year)
    end = '%d-12-31' % (year)
    theTime = datetime.now()
    if year == theTime.year:
        end = theTime.strftime('%Y-%m-%d')
    df = ts.get_hist_data(code, start=start, end=end)
    # print df
    return df

def get_dataOfMonths(code, months):
    theTime = datetime.now()
    end = theTime.strftime('%Y-%m-%d')
    start = (theTime - timedelta(days=months * 30)).strftime('%Y-%m-%d') 
    df = ts.get_hist_data(code, start=start, end=end)
    # print df
    return df

if __name__ == '__main__':
    calc()
#calc()
