# -*- coding: utf-8 -*-
import sys

from datetime import date, datetime, timedelta
import dateutil2 # own
import dbman # own
import tdal # own

def get_today_KDJ933(stock, current_price, today_high, today_low, log):
    if not stock.has_key('KDJ'):
        raise Exception('no KDJ' + stock['code'])
    real = dateutil2.is_today_trade_date()
    return compute_KDJ933(stock, date.today(), current_price, today_high, today_low, real, log)

def compute_KDJ933(stock, theDate, close, high, low, real, log):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if dateutil2.parse_date(baseKDJDateStr) == theDate:
        #print 'hit'
        return (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    (k_1, d_1, j_1) = get_previous_KDJ933(stock, dateutil2.previous_date(theDate), log)
    if not real:
        return (k_1, d_1, j_1)
    #print 'compute' + stock['code'] + ' ' + theDate.strftime('%Y-%m-%d') + ' ' + str(k_1) + ' ' + str(d_1) + " " + str(j_1)
    h9 = high
    l9 = low
    count = 1
    while count < 9:
        theDate = dateutil2.previous_date(theDate)
        datestr = dateutil2.format_date(theDate)
        dh = tdal.previous_data_with_date(stock['code'], datestr, log)
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

def get_previous_KDJ933(stock, theDate, log):
    theOriginDate = theDate
    datestr = dateutil2.format_date(theDate)
    dh = tdal.previous_data_with_date(stock['code'], datestr, log)
    if dh is None:
        print "dh is None. Shouldn't happen."
        return (0, 0, 0)
    if dh.has_key('theK') and (not dbman.reset_KDJ):
        return (dh['theK'], dh['theD'], dh['theJ'])
    (k, d, j) = compute_KDJ933(stock, theOriginDate, dh['close'], dh['high'], dh['low'], dh['real'], log)
    dbman.c_dayK.update({"code": stock['code'], "date": datestr}, {"$set": {"theK": k, "theD": d, "theJ": j}})
    return (k, d, j)

# no-test
def print_KDJ(stock, theDate):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if datetime.strptime(baseKDJDateStr, '%Y-%m-%d').date() == theDate:
        print baseKDJDateStr + " KDJ %6.2f %6.2f %6.2f" % (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    else:
        (k, d, j) = get_previous_KDJ933(stock, theDate)
        theDateStr = theDate.strftime('%Y-%m-%d')
        print theDateStr + " KDJ %6.2f %6.2f %6.2f" % (k, d, j)
        print_KDJ(stock, theDate - timedelta(days=1))

# no-test
def print_KDJs(code):
    theDate = date.today()
    for stock in all_stocks:
        if stock['code'] == code:
            print_KDJ(stock, theDate - timedelta(days=1))

if __name__=='__main__':
    print_KDJs('601766')
