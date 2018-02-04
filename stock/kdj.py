# -*- coding: utf-8 -*-
import sys

import dateutil # own
import dbman # own

def get_today_KDJ933(stock, current_price, today_high, today_low):
    if not stock.has_key('KDJ'):
        raise Exception('no KDJ' + stock['code'])
    real = dateutil.is_today_trade_date)
    return compute_KDJ933(stock, date.today(), current_price, today_high, today_low, real)

def compute_KDJ933(stock, theDate, close, high, low, real):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if dateutil.parse_date(baseKDJDateStr) == theDate:
        #print 'hit'
        return (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    (k_1, d_1, j_1) = get_previous_KDJ933(stock, dateutil.previous_date(theDate))
    if not real:
        return (k_1, d_1, j_1)
    #print 'compute' + stock['code'] + ' ' + theDate.strftime('%Y-%m-%d') + ' ' + str(k_1) + ' ' + str(d_1) + " " + str(j_1)
    h9 = high
    l9 = low
    count = 1
    while count < 9:
        theDate = dateutil.previous_date(theDate)
        datestr = dateutil.format_date(theDate)
        dh = previous_data_with_date(stock['code'], datestr)
        if dh['real']:
            count += 1
            if l9 > dh['low']:
                l9 = dh['low']
            if h9 < dh['high']:
                h9 = dh['high']
    rsv = (close - l9) / (h9 - l9) * 100
    #print "rsv " + str(rsv) + " l9 " + " " + str(l9) + " h9 " + str(h9)
    k = rsv / 3 + 2 * k_1 / 3
    d = k / 3 + 2 * d_1 / 3
    j = 3 * k - 2 * d
    return (k, d, j)

def get_previous_KDJ933(stock, theDate):
    theOriginDate = theDate
    datestr = dateutil.format_date(theDate)
    dh = previous_data_with_date(stock['code'], datestr)
    if dh is None:
        print "dh is None. Shouldn't happen."
        return (0, 0, 0)
    if dh.has_key('theK') and (not dbman.reset_KDJ):
        return (dh['theK'], dh['theD'], dh['theJ'])
    (k, d, j) = compute_KDJ933(stock, theOriginDate, dh['close'], dh['high'], dh['low'], dh['real'])
    dbman.c_dayK.update({"code": stock['code'], "date": datestr}, {"$set": {"theK": k, "theD": d, "theJ": j}})
    return (k, d, j)

def previous_data(code):
    d = date.today()
    tdatestr = d.strftime('%Y-%m-%d')
    dh = dbman.c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
    dh = list(dh)
    
    if len(dh) == 0 or (len(dh) != 0 and not dh[0].has_key('high')):
        df = None
        while df is None or df.empty:
            d = d - timedelta(days=1)
            datestr = d.strftime('%Y-%m-%d')
            #print datestr
            log_status('Getting hist data for %s at %s' % (code, datestr))
            df = ts.get_hist_data(code, start=datestr, end=datestr)
            log_status('Done hist data for %s at %s' % (code, datestr))
            #print df
            if df is None or df.empty:
                pdh = dbman.c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
                pdh = list(pdh)
                if len(pdh) != 0:
                    if len(dh) == 0:
                        dbman.c.insert({"code": code, "date": tdatestr, "close": pdh[0]['close'], "open": pdh[0]['open'], "high": pdh[0]['high']})
                    else:
                        dbman.c.update({"code": code, "date": tdatestr}, {"$set": {"high": pdh[0]['high']}})
                    dh = dbman.c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
                    dh = list(dh)
                    return dh[0]
        if len(dh) == 0:
            dbman.c.insert({"code": code, "date": tdatestr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0]})
        else:
            dbman.c.update({"code": code, "date": tdatestr}, {"$set": {"high": df['high'][0]}})
        dh = dbman.c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
        dh = list(dh)
        #print len(dh)

    return dh[0]


