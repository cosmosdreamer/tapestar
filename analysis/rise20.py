# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, '../stock/')
#print sys.path

#import advise
#import stockdata
from datetime import date, datetime, timedelta
import tushare as ts

c_highlight_blue = '\033[1;34;40m'
c_highlight_red = '\033[1;31;40m'
c_highlight_green = '\033[1;32;40m'
c_default_white = '\033[0;37;40m'
c_reset = '\033[0m'

result_data = {}

#           print '  %s %s:\t%s%4.1f%%%s\t\t%s' % (stock['code'], stock['name'], color, ratio, c_reset, str(stock['vest']))

def get_recent_low_from_date(code, datestr):
    #theBeginDate = datetime.strptime(datestr, '%Y-%m-%d').date()
    theBeginDate = (date.today() - timedelta(days=90)).strftime('%Y-%m-%d')
    theEndDate = date.today().strftime('%Y-%m-%d')
    recent_low = 10000.0
    df = ts.get_hist_data(code, start=theBeginDate, end=theEndDate)
    if df is not None:
        for index in range(len(df['low'])):
            if df['low'][index] < recent_low:
                recent_low = df['low'][index]
    else:
        recent_low = 0.0
    return recent_low

def is_halt(dg):
    return float(dg['price'][0]) == 0 or float(dg['open'][0]) == 0

def get_recent_rise(code):
    dg = ts.get_realtime_quotes(code)
    if dg is None or is_halt(dg):
        return 0.0
    #print float(dg['open'][0]) == 0
    theDate = date.today() - timedelta(days=90)
    low = get_recent_low_from_date(code, theDate.strftime('%Y-%m-%d'))
    result_data[code]['name'] = dg['name'][0]
    price = float(dg['price'][0])
    #print low
    return (price - low) / low if low != 0 else 0.0

def calc():
    #for icode in range(0, 4000):
    #    code = str(600000 + icode)
    for icode in range(0, 2950):
        code = str(2000000 + icode)[1:]
    #for icode in range(0, 750):
    #    code = str(300000 + icode)
        result_data[code] = {}
        result_data[code]['name'] = ''
        rise = get_recent_rise(code)
        on_focus = rise >= 0.2 and rise <= 0.25
        color = c_default_white if not on_focus else c_highlight_red
        if on_focus:
            print code + ' ' + result_data[code]['name'] + '    ' + color + str(rise) + c_reset
    #print 'all: ' + str(all_vest)

if __name__ == '__main__':
    calc()
#
