# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import dateutil2 # own
import keys # own
import math
import posman # own
import tdal # own

def preprocess_all(stocks, sh_index):
    posman.reset()
    for stock in stocks:
        preprocess_stock(stock, sh_index)

def preprocess_stock(stock, sh_index):
    last_buy = 0.0
    last_buy_date = date.min
    far_buy_date = date.max
    last_sell = 0.0
    last_sell_date = date.min
    position = 0
    last_buy_position = 0
    turnover = 0
    if stock.has_key(keys.trades):
        for trade in stock[keys.trades]:
            theDate = dateutil2.parse_date(trade[0])
            direction = trade[1]
            amount = trade[2]
            price = trade[3]
            if direction == 2 or len(trade) > 4:
                theSellDate = dateutil2.parse_date(trade[4])
                sellPrice = trade[5]
                # correct direction in case it has wrong value
                if direction != 2:
                    print 'wrong direction in stock ' + stock['code']
                    direction = 2
                if theSellDate >= last_sell_date:
                    last_sell_date = theSellDate
                    last_sell = sellPrice
                turnover += 1
            if direction == 1 and theDate >= last_buy_date:
                last_buy_date = theDate
                last_buy = price
                last_buy_position = amount
            if direction == 1 and theDate < far_buy_date:
                far_buy_date = theDate
            if direction == 1:
                position += direction * amount
                posman.investments['total'] += direction * amount * price
                if stock['code'] not in posman.whitelist_codes:
                    posman.investments['totalExceptWhitelist'] += direction * amount * price
                if (stock['code'] not in posman.whitelist_codes) and (stock['code'] not in posman.halt_codes):
                    posman.investments['totalExceptWhitelistAndHalt'] += direction * amount * price
                if stock['code'] in posman.vip_codes:
                    posman.investments['totalVip'] += direction * amount * price
                # sh index at trade date
                dh = tdal.previous_data_with_date(sh_index['code'], trade[0])
                shIndex = (dh['high'] + dh['low']) / 2
                posman.investments['indexedTotal'] += shIndex * amount * price
                costIndex = int(math.floor((5000 - shIndex) / 500) + 1)
                costIndex = 0 if (costIndex < 0) else costIndex
                costIndex = 7 if (costIndex > 7) else costIndex
                posman.investments['indexed_cost'][costIndex] += amount * price
                if sh_index['price'] > 0:
                    costIndex = (int(sh_index['price']) / 100) - (int(shIndex) / 100) + 3
                    #display_info("" + costIndex + " " + amount * price, 1, 20)
                    if costIndex >= 0 and costIndex <= 7:
                        posman.investments['fine_indexed_cost'][costIndex] += amount * price
    if not stock.has_key('last_buy_date') and last_buy_date != date.min:
        stock['last_buy_date'] = last_buy_date.strftime('%Y-%m-%d')
    if not stock.has_key('far_buy_date') and far_buy_date != date.max:
        stock['far_buy_date'] = far_buy_date.strftime('%Y-%m-%d')
    if not stock.has_key('last_buy'):
        stock['last_buy'] = last_buy
    if not stock.has_key('last_buy_position'):
        stock['last_buy_position'] = last_buy_position
    if not stock.has_key('last_sell_date') and last_sell_date != date.min:
        stock['last_sell_date'] = last_sell_date.strftime('%Y-%m-%d')
    if not stock.has_key('last_sell'):
        stock['last_sell'] = last_sell
    if not stock.has_key('position'):
        stock['position'] = position
    if stock['position'] > 0:
        posman.investments['positioned_stock_count'] += 1
    stock['turnover'] = turnover




