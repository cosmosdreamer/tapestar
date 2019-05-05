# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import dateutil2 # own
import stockdata # own
import sys
import tushare as ts

def profit():
    overall_history_amount = 0.0
    overall_history_profit = 0.0
    overall_current_amount = 0.0
    overall_current_profit = 0.0
    for stock in stockdata.all_stocks_1:
        if stock.has_key('trades'):
            code = stock['code']
            #print 'Getting realtime quotes...'
            df = ts.get_realtime_quotes(code)
            today_price = float(df['price'][0])
            print code + ' ' + df['name'][0]

            history_amount = 0.0
            history_profit = 0.0
            current_amount = 0.0
            current_profit = 0.0
            for trade in stock['trades']:
                theDate = dateutil2.parse_date(trade[0])
                direction = trade[1]
                volume = trade[2]
                price = trade[3]
                if direction == 2 or len(trade) > 4:
                    theSellDate = dateutil2.parse_date(trade[4])
                    sellPrice = trade[5]
                    history_amount += price * volume
                    history_profit += (sellPrice - price) * volume
                if direction == 1:
                    current_amount += price * volume
                    current_profit += (today_price - price) * volume

            if history_amount != 0.0:
                print '历史: %s/%s \t%5.2f%%' % (str(history_amount), str(history_profit), history_profit / history_amount * 100)
            if current_amount != 0.0:
                print '持仓: %s/%s \t%5.2f%%' % (str(current_amount), str(current_profit), current_profit / current_amount * 100)

            overall_history_amount += history_amount
            overall_history_profit += history_profit
            overall_current_amount += current_amount
            overall_current_profit += current_profit
            
            print ''

    print '\n\n'
    if overall_history_amount != 0.0:
        print '历史: %s/%s \t%5.2f%%' % (str(overall_history_amount), str(overall_history_profit), overall_history_profit / overall_history_amount * 100)
    if overall_current_amount != 0.0:
        print '持仓: %s/%s \t%5.2f%%' % (str(overall_current_amount), str(overall_current_profit), overall_current_profit / overall_current_amount * 100)



if __name__=='__main__':
    #print arguments[0]
    profit()
    print




