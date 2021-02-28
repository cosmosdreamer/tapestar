# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import dateutil2 # own
import stockdata # own
import sys
import tushare as ts

reload(sys)
sys.setdefaultencoding('utf-8')

def get_hist(code, hist_date):
    #print 'Getting hist data...'
    df = ts.get_hist_data(code, start=dateutil2.format_date(hist_date), end=dateutil2.format_date(date.today()), ktype='W')
    #high = 0.0
    #for i in range(0, len(df)):
        #return float(df['close'][i])
        #theHigh = float(df['high'][i])
        #print df.index[i] + ' ' + str(theHigh)
        #if high < theHigh:
        #    high = theHigh
    #return high
    if df is None:
        return 0.0
    elif len(df['close']) == 0:
        return 0.0
    else:
        return float(df['close'][0])

def compOffset(stock1, stock2):
    return int(stock1['offset'] - stock2['offset'])

def profit():
    # 半年时间
    hist_date = date.today() - timedelta(days=180)

    df = ts.get_realtime_quotes('sh')
    index_today_price = float(df['price'][0])
    index_hist_price = get_hist('sh', hist_date)
    
    print '上证指数: %s/%s' % (str(index_hist_price), str(index_today_price))
    print '上证涨幅: %4.2f%%' % ((index_today_price - index_hist_price) / index_hist_price * 100)
    print

    profitArray = []
    for stock in stockdata.all_stocks_1:
        code = stock['code']
        #print 'Getting realtime quotes...'
        df = ts.get_realtime_quotes(code)
        today_price = float(df['price'][0])
        hist_price = get_hist(code, hist_date)
        
        #print code + ' ' + df['name'][0]
        #print '股价: %s/%s' % (str(hist_price), str(today_price))
        info = code + ' ' + df['name'][0]
        info += '\n股价: %s/%s' % (str(hist_price), str(today_price))
        if hist_price != 0.0:
            #print '涨幅: %4.2f%%' % ((today_price - hist_price) / hist_price * 100)
            #print '背离: %4.2f%%' % ((today_price - hist_price) / hist_price * 100 - (index_today_price - index_hist_price) / index_hist_price * 100)
            info += '\n涨幅: %4.2f%%' % ((today_price - hist_price) / hist_price * 100)
            offset_rate = (today_price - hist_price) / hist_price * 100 - (index_today_price - index_hist_price) / index_hist_price * 100
            info += '\n背离: %4.2f%%\n' % (offset_rate)
        profitArray.append({'offset': offset_rate, 'info': info})
        print '.'

    profitArray.sort(compOffset)

    for stock in profitArray:
        print stock['info']


if __name__=='__main__':
    print
    profit()
    print




