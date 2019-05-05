# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import dateutil2 # own
import stockdata # own
import sys
import tushare as ts

def get_high(code, last_buy_date):
    print 'Getting hist data...'
    df = ts.get_hist_data(code, start=dateutil2.format_date(last_buy_date), end=dateutil2.format_date(date.today()))
    high = 0.0
    for i in range(0, len(df)):
        theHigh = float(df['high'][i])
        print df.index[i] + ' ' + str(theHigh)
        if high < theHigh:
            high = theHigh
    return high

def last_trade(code):
    print 'Getting realtime quotes...'
    df = ts.get_realtime_quotes(code)
    today_price = float(df['price'][0])
    print code + ' ' + df['name'][0]
    for stock in stockdata.all_stocks_1:
        if stock['code'] == code and stock.has_key('trades'):
            last_buy_date = date.min
            last_buy = 0.0
            last_buy_position = 0
            for trade in stock['trades']:
                theDate = dateutil2.parse_date(trade[0])
                direction = trade[1]
                volume = trade[2]
                price = trade[3]
                if direction == 1 and theDate >= last_buy_date:
                    last_buy_date = theDate
                    last_buy = price
                    last_buy_position = volume
            if last_buy != 0.0:
                print 'Last trade: ' + str(last_buy_date) + ' ' + str(last_buy) + ' ' + str(last_buy_position)
                print '当前价: ' + str(today_price)
                print '盈利: ' + '%3.2f%%' % ((today_price - last_buy) / last_buy * 100)
                high = get_high(code, last_buy_date)
                print ''
                print '最高价: ' + str(high)
                print '回撤: ' + '%2.0f%%' % ((high - today_price)/(high - last_buy) * 100)



if __name__=='__main__':
    last_trade(sys.argv[1])
