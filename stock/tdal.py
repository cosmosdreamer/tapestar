# -*- coding: utf-8 -*-
import sys

from datetime import date, datetime, timedelta
import dateutil2 # own
import dbman # own
import tushare as ts
import util # own

def get_realtime_quotes(stocks, log):
    total = len(stocks)
    codes = map(util.get_stock_code, stocks)
    realtime_quotes = None
    batches = total / 15 + (1 if total % 15 != 0 else 0)
    for ind in range(batches):
        start = ind * 15
        end = ind * 15 + 15
        end = end if end < total else total
        log('(%d/%d) Getting realtime quotes' % (ind + 1, batches))
        df = ts.get_realtime_quotes(codes[start : end])
        log('(%d/%d) Done realtime quotes' % (ind + 1, batches))
        if realtime_quotes is None:
            realtime_quotes = df
        else:
            realtime_quotes = realtime_quotes.append(df, True)
    return realtime_quotes

###
# tushare supported code:
# realtime
# 12XXXX 可转债
# 13XXXX 国债逆回购，可交换债
# 15XXXX ETF基金，分级基金（开放分级？深市？）
# 16XXXX 定增基金? 行业基金
# 50XXXX 分级基金（沪市？）
# 51XXXX ETF基金
###

###
# Not supported code:
# 01XXXX 国债
# 11XXXX 可转债？
###

history_cache = {}
dayK_cache = {}

# trade data abstraction layer

# 上一交易日的数据
def previous_data(code, log):
    d = date.today()
    tdatestr = dateutil2.format_date(d)
    # mem cache
    codedate = code + '__' + tdatestr
    if history_cache.has_key(codedate):
        return history_cache[codedate]

    # db
    dh = dbman.query_history(code, tdatestr)
    
    if len(dh) == 0 or (len(dh) != 0 and not dh[0].has_key('high')):
        df = None
        while df is None or df.empty:
            d = dateutil2.previous_date(d)
            datestr = dateutil2.format_date(d)
            #print datestr
            log('Getting hist data for %s at %s' % (code, datestr))
            df = ts.get_hist_data(code, start=datestr, end=datestr)
            #print 'x'
            log('Done hist data for %s at %s' % (code, datestr))
            #print df
            if df is None or df.empty:
                pdh = dbman.query_history(code, datestr)
                if len(pdh) != 0:
                    # update db
                    if len(dh) == 0:
                        dbman.insert_history(code, tdatestr, pdh[0]['open'], pdh[0]['close'], pdh[0]['high'])
                    else:
                        dbman.update_history(code, tdatestr, pdh[0]['high'])
                    dh = dbman.query_history(code, tdatestr)
                    history_cache[codedate] = dh[0]
                    return dh[0]
        # update db
        if len(dh) == 0:
            dbman.insert_history(code, tdatestr, df['open'][0], df['close'][0], df['high'][0])
        else:
            dbman.update_history(code, tdatestr, df['high'][0])
        dh = dbman.query_history(code, tdatestr)
        #print len(dh)

    history_cache[codedate] = dh[0]
    return dh[0]

def previous_data_with_date(code, datestr, log, recursive = True):

    # mem cache
    codedate = code + '__' + datestr
    if dayK_cache.has_key(codedate):
        return dayK_cache[codedate]

    originDateStr = datestr
    dh = dbman.query_dayK(code, datestr)
    
    if len(dh) == 0:
        log('Getting hist data for %s at %s' % (code, datestr))
        df = ts.get_hist_data(code, start=datestr, end=datestr)
        #print 'x'
        log('Done hist data for %s at %s' % (code, datestr))
        d = dateutil2.parse_date(datestr)
        if df is None or df.empty:
            if not recursive:
                return None
            d = dateutil2.previous_date(d)
            datestr = dateutil2.format_date(d)
            #df = ts.get_hist_data(code, start=datestr, end=datestr)
            dh = previous_data_with_date(code, datestr, log)
            dbman.insert_dayK(code, False, originDateStr, dh['open'], dh['close'], dh['high'], dh['low'])
        else:
            dbman.insert_dayK(code, True, originDateStr, df['open'][0], df['close'][0], df['high'][0], df['low'][0])
        dh = dbman.query_dayK(code, originDateStr)

    dayK_cache[codedate] = dh[0]
    return dh[0]

def log_none(str):
    print str
    #pass

if __name__=='__main__':
    print previous_data('601788', log_none)
    #print previous_data_with_date('601211', '2018-2-17', log_none, False)
