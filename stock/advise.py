# -*- coding: utf-8 -*-
import curses  
from dateutil import rrule
from datetime import date, datetime, timedelta
import httplib
import json
import legalholidays # own
import locale
from lxml import etree
import lxml.html.soupparser as soupparser
import math
import pymongo
from pymongo import MongoClient
import stockdata # own
import strutil # own
import sys  
import time
import tushare as ts

reload(sys)  
sys.setdefaultencoding('utf8')  

locale.setlocale(locale.LC_ALL, '')
system_code = locale.getpreferredencoding()

stdscr = None

#stock_codes = ['002450', '601766', '601288', '000488', '002008', '600522', '002164', '600008']
#eyeon_stock_codes = ['002290', '600029', '002570', '000898']

client = MongoClient()
db = client.stock
# history schema: {"code": code, "date": tdatestr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0]}
c = db.history
# trade schema: {"code": code, "recent_high": dh['high']}
#db.trade.drop()
#c_trade = db.trade
#db.dayK.drop()
reset_KDJ = False
c_dayK = db.dayK

sh_index = {
    'code': 'sh',
    'KDJ': { '2016-10-31': [67.27, 77.84, 46.12]},
    'price': 0,
}

precious_metals = [
    {
        'code': 1,
        'name': '白银',
        'trades': [
            ['2015-12-14', 1, 3000, 2.87],
        ],
    }
]

whitelist_codes = ['601288', '000725'] # 农业银行
halt_codes = [] # real-time retrieve
vip_codes = ['002008', '002290', '002450'] # 大禾康

positioned_stock_count = 0

const_totalBase = 200000

investments = {
    'totalBase': const_totalBase,
    'total': 0,
    'totalExceptWhitelist': 0,
    'totalExceptWhitelistAndHalt': 0,
    'totalVip': 0,
    'indexed_cost': [],
    'fine_indexed_cost': [],
    'indexedTotal': 0,
}

def preprocess_all():
    global positioned_stock_count
    investments['total'] = 0
    investments['totalExceptWhitelist'] = 0
    investments['totalExceptWhitelistAndHalt'] = 0
    investments['totalVip'] = 0
    investments['indexed_cost'] = [0, 0, 0, 0, 0, 0, 0, 0]
    investments['fine_indexed_cost'] = [0, 0, 0, 0, 0, 0, 0, 0]
    investments['indexedTotal'] = 0
    positioned_stock_count = 0
    for stock in stockdata.all_stocks:
        preprocess_stock(stock)

def preprocess_stock(stock):
    global positioned_stock_count
    last_buy = 0.0
    last_buy_date = date.min
    far_buy_date = date.max
    last_sell = 0.0
    last_sell_date = date.min
    position = 0
    last_buy_position = 0
    turnover = 0
    if stock.has_key('trades'):
        for trade in stock['trades']:
            theDate = datetime.strptime(trade[0], '%Y-%m-%d').date()
            direction = trade[1]
            amount = trade[2]
            price = trade[3]
            if direction == 2 or len(trade) > 4:
                theSellDate = datetime.strptime(trade[4], '%Y-%m-%d').date()
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
                investments['total'] += direction * amount * price
                if stock['code'] not in whitelist_codes:
                    investments['totalExceptWhitelist'] += direction * amount * price
                if (stock['code'] not in whitelist_codes) and (stock['code'] not in halt_codes):
                    investments['totalExceptWhitelistAndHalt'] += direction * amount * price
                if stock['code'] in vip_codes:
                    investments['totalVip'] += direction * amount * price
                # sh index at trade date
                dh = previous_data_with_date(sh_index['code'], trade[0])
                shIndex = (dh['high'] + dh['low']) / 2
                investments['indexedTotal'] += shIndex * amount * price
                costIndex = int(math.floor((5000 - shIndex) / 500) + 1)
                costIndex = 0 if (costIndex < 0) else costIndex
                costIndex = 7 if (costIndex > 7) else costIndex
                investments['indexed_cost'][costIndex] += amount * price
                if sh_index['price'] > 0:
                    costIndex = (int(sh_index['price']) / 100) - (int(shIndex) / 100) + 3
                    #display_info("" + costIndex + " " + amount * price, 1, 20)
                    if costIndex >= 0 and costIndex <= 7:
                        investments['fine_indexed_cost'][costIndex] += amount * price
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
        positioned_stock_count += 1
    stock['turnover'] = turnover

def get_hold_duration(stock):
    far = 0
    last = 0
    if stock.has_key('far_buy_date'):
        theDate = datetime.strptime(stock['far_buy_date'], '%Y-%m-%d').date()
        delta = date.today() - theDate
        far = math.floor(delta.days / 30)
    if stock.has_key('last_buy_date'):
        theDate = datetime.strptime(stock['last_buy_date'], '%Y-%m-%d').date()
        delta = date.today() - theDate
        last = math.floor(delta.days / 30)
    return (last, far)

def compCurrentJ(stockX, stockY):
    if not stockX.has_key('more_info_currentJ') or not stockY.has_key('more_info_currentJ'):
        return 0

    if stockX['more_info_currentJ'] < stockY['more_info_currentJ']:
        return 1
    elif stockX['more_info_currentJ'] > stockY['more_info_currentJ']:
        return -1
    else:
        return 0

stock_index = 0
stock2line = {}

const_baseOffsetPercent = 0.15

def advice_all():
    global positioned_stock_count
    theTime = datetime.now()

    # line 1
    log_status('Getting sh index')
    df = ts.get_realtime_quotes(sh_index['code'])
    log_status('Done sh index')
    sh_index['price'] = float(df['price'][0])
    (k, d, j) = get_today_KDJ933(sh_index, float(df['price'][0]), float(df['high'][0]), float(df['low'][0]))
    now = 'Time: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f  关注: %2d 持仓: %2d 停牌: %2d' \
        % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
        float(df['price'][0]), \
        (float(df['price'][0]) - float(df['pre_close'][0])) / float(df['pre_close'][0]) * 100, j, \
        len(stockdata.all_stocks), positioned_stock_count, len(halt_codes))
    sh_index['price'] = float(df['price'][0])
    if g_arg_simplified:
        now = 'T: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f' \
        % (datetime.now().strftime('%H:%M:%S'), \
        float(df['price'][0]), \
        (float(df['price'][0]) - float(df['pre_close'][0])) / float(df['pre_close'][0]) * 100, j)
    display_info(now, 1, 1)
    #workaround to color index J
    if not g_arg_simplified:
        indexJ = '%6.2f' % j
        indexJ_color = 1
        if j <= 20:
            indexJ_color = 2
        elif j >= 80:
            indexJ_color = 3
        display_info(indexJ, 59, 1, indexJ_color)
    #stockCountInfo = 'Stocks: %d' % (len(stockdata.all_stocks))
    #display_info(stockCountInfo, 80, 1)
    
    # line 2
    indexed_coststr = '[>5000:%6.2f%%|>4500:%6.2f%%|>4000:%6.2f%%|>3500:%6.2f%%|>3000:%6.2f%%|>2500:%6.2f%%|>2000:%6.2f%%|>1500:%6.2f%%] - %7.2f' \
        % (investments['indexed_cost'][0]/investments['total'] * 100, \
        investments['indexed_cost'][1]/investments['total'] * 100, \
        investments['indexed_cost'][2]/investments['total'] * 100, \
        investments['indexed_cost'][3]/investments['total'] * 100, \
        investments['indexed_cost'][4]/investments['total'] * 100, \
        investments['indexed_cost'][5]/investments['total'] * 100, \
        investments['indexed_cost'][6]/investments['total'] * 100, \
        investments['indexed_cost'][7]/investments['total'] * 100, investments['indexedTotal'] / investments['total'])
    if not g_arg_simplified:
        display_info(indexed_coststr, 1, 2)

    # line 3
    current_invest_base = (1 - (float(df['price'][0]) / 500 - 2)*0.1) * investments['totalBase']
    invest_status = '仓/允: %6.0f/%6.0f, 除农: %6.0f, 除农比: %6.2f%%, 除停: %6.0f, 除停比: %6.2f%%, 大禾康占比: %6.2f%%' \
        % (investments['total'], current_invest_base, investments['totalExceptWhitelist'], \
        (investments['totalExceptWhitelist'] - (current_invest_base - investments['totalBase'] * const_baseOffsetPercent)) / (investments['totalBase'] * const_baseOffsetPercent * 2) * 100, \
        investments['totalExceptWhitelistAndHalt'], \
        (investments['totalExceptWhitelistAndHalt'] - (current_invest_base - investments['totalBase'] * const_baseOffsetPercent)) / (investments['totalBase'] * const_baseOffsetPercent * 2) * 100, \
        investments['totalVip'] / investments['total'] * 100)
    if not g_arg_simplified:
        display_info(invest_status, 1, 3)
    
    # line 4
    baseIndex = int(sh_index['price']) / 100 * 100
    indexed_coststr = '[>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%]' \
        % (baseIndex + 300, investments['fine_indexed_cost'][0]/investments['total'] * 100, \
        baseIndex + 200, investments['fine_indexed_cost'][1]/investments['total'] * 100, \
        baseIndex + 100, investments['fine_indexed_cost'][2]/investments['total'] * 100, \
        baseIndex, investments['fine_indexed_cost'][3]/investments['total'] * 100, \
        baseIndex - 100, investments['fine_indexed_cost'][4]/investments['total'] * 100, \
        baseIndex - 200, investments['fine_indexed_cost'][5]/investments['total'] * 100, \
        baseIndex - 300, investments['fine_indexed_cost'][6]/investments['total'] * 100, \
        baseIndex - 400, investments['fine_indexed_cost'][7]/investments['total'] * 100)
    if not g_arg_simplified:
        display_info(indexed_coststr, 1, 4)
    
    line = 5 if not g_arg_simplified else 2
    new_stocks = today_new_stocks()
    if len(new_stocks) > 0:
        line += 1
        display_info('今新: ' + ' '.join(new_stocks), 1, 4)

    for stock in stockdata.all_stocks:
        advise(stock)

    stockdata.all_stocks.sort(compCurrentJ)
    global stock_index
    stock_index = 0
    line = display_stock_group(stockdata.all_stocks, "卖出", line)
    line = display_empty_line(line)
    line = display_stock_group(stockdata.all_stocks, "买入", line)
    line = display_empty_line(line)
    line = display_stock_group(stockdata.all_stocks, "弱买", line)
    line = display_stock_group(stockdata.all_stocks, "追高", line)
    line = display_empty_line(line)
    line = display_stock_group(stockdata.all_stocks, "忖卖", line)
    line = display_stock_group(stockdata.all_stocks, "弱卖", line)
    line = display_stock_group(stockdata.all_stocks, "薄卖", line)
    line = display_stock_group(stockdata.all_stocks, "亏卖", line)
    line = display_empty_line(line)
    line = display_stock_group(stockdata.all_stocks, "持有", line)
    line = display_empty_line(line)
    line = display_stock_group(stockdata.all_stocks, "观望", line)
    line = display_stock_group(stockdata.all_stocks, " -- ", line)
    if g_show_all:
        line = display_stock_group(stockdata.all_stocks, "HIDE", line)
        line = display_stock_group(stockdata.all_stocks, "    ", line)

    line = display_empty_line(line)
    line = display_empty_line(line)
    line = display_empty_line(line)

    elapsed = datetime.now() - theTime
    display_info(' ' + str(elapsed), 0, line + 1)

def advise(stock):
    log_status('Getting realtime quotes for %s' % (stock['code']))
    df = ts.get_realtime_quotes(stock['code'])
    log_status('Done realtime quotes for %s' % (stock['code']))
    dh = previous_data(stock['code'])
    
    # name
    stock['name'] = df['name'][0]
    namelen = strutil.width(stock['name'])
    if namelen < 8:
        for i in range(8 - namelen):
            stock['name'] += ' ' # '_'
    #print len(stock['name'])
    #print namelen

    action = ''
    action_color = 1
    
    code = stock['code']
    current_price = float(df['price'][0])
    today_high = float(df['high'][0])
    today_open = float(df['open'][0])
    position = stock['position']
    last_sell = stock['last_sell']
    last_buy = stock['last_buy']
    previous_close = float(dh['close'])
    previous_open = float(dh['open'])

    last_profit = stock['last_buy_position'] * (current_price - last_buy)
    if not g_show_all and stock.has_key('margin'):
        if len(stock['margin']) > 1 and stock['margin'][0] < current_price and stock['margin'][1] > current_price \
            or len(stock["margin"]) == 1 and stock['margin'][0] < current_price and (position == 0 or current_price < stock["last_buy"] * 1.05):
            stock['action'] = "HIDE"
            return
        elif last_profit > 0 and last_profit < 110.0:
            stock['action'] = "HIDE"
            return
    elif not g_show_all and current_price > stock["last_buy"] * 0.90 and current_price < stock["last_buy"] * 1.05:
        stock['action'] = "HIDE"
        return
    elif not g_show_all and position == 0 and stock["last_sell"] > 0 and current_price * 1.06 > stock["last_sell"]:
        stock['action'] = "HIDE"
        return
    elif not g_show_all and last_profit > 0 and last_profit < 110.0:
        stock['action'] = "HIDE"
        return

    j = 0
    if stock.has_key('KDJ'):
        (k, d, j) = get_today_KDJ933(stock, current_price, float(df['high'][0]), float(df['low'][0]))
    if today_open == 0:
        action = "    "
    elif float(df['price'][0]) - float(df['open'][0]) > 0:
        if float(dh['close']) - float(dh['open']) < 0:
            strong_buy = whether_strong_buy(current_price, last_sell, last_buy)
            strong_buy = False if (j > 80) else strong_buy
            if strong_buy:
                action = "买入"
                action_color = 2
            else:
                action = "弱买"
                action_color = 4
        else:
            if stock['position'] == 0:
                action = "追高"
                action_color = 4
            else:
                action = "持有"
    elif float(df['price'][0]) - float(df['open'][0]) < 0:
        if previous_close - previous_open < 0 or position == 0:
            action = "观望"
        elif current_price < last_buy:
            action = "亏卖"
            action_color = 5
        elif current_price > last_buy + 1.00 and current_price < last_buy * 1.1:
            strong_sell = whether_strong_sell(stock, current_price, last_sell, last_buy, today_high)
            if strong_sell:
                action = "卖出"
                action_color = 3
            else:
                action = "弱卖"
                action_color = 5
        elif current_price < last_buy + 1.00 or current_price < last_buy * 1.1:
            action = "薄卖"
            action_color = 5
        else:
            strong_sell = whether_strong_sell(stock, current_price, last_sell, last_buy, today_high)
            if strong_sell:
                action = "卖出"
                action_color = 3
            else:
                action = "忖卖"
                action_color = 5
    elif current_price == 0:
        action = "    "
    else:
        action = " -- "
    stock['action'] = action
    stock['action_color'] = action_color
 
    profit_percent = 0
    if last_buy > 0 and position > 0:
        profit_percent = math.floor((current_price - last_buy) / last_buy * 100)
    #if profit_percent <= -10:
    #    profit_percent = 0
 
    if profit_percent == 0:
        profit_percentstr = '    '
    else:
        profit_percentstr = '%3d%%' % profit_percent
    
    regress_rate = 0
    if profit_percent <= 0:
        regress_ratestr = '   '
    else:
        recent_high = get_recent_high(stock, float(df['high'][0]))
        regress_rate = math.ceil((recent_high - current_price) / (recent_high - last_buy) * 100)
        #if code == '000531':
        #    print str(recent_high) + ' ' + str(current_price) + ' ' + str(last_buy)
        regress_ratestr = '%2d%%' % regress_rate
    
    if (current_price == 0 or today_open == 0)and (code not in halt_codes):
        halt_codes.append(code)
        preprocess_all()

    (last, far) = get_hold_duration(stock)
    durationstr = '     '
    if position > 0:
        durationstr = '%2d/%2d' %(last, far)

    stack = 0
    stackstr = '     '
    if stock.has_key('trades'):
        for trade in stock['trades']:
            direction = trade[1]
            if direction == 1:
                stack += 1
                stackstr = stackstr.replace(' ', '|', 1)

    index_profit_percent = 0
    buy_index = 0
    if position > 0:
        index_dh = previous_data_with_date(sh_index['code'], stock['last_buy_date'])
        buy_index = (index_dh['high'] + index_dh['low']) / 2
        index_profit_percent = (sh_index['price'] - buy_index) / buy_index
    index_profit_percentstr = '       '
    if index_profit_percent != 0:
        index_profit_percentstr = '%6.2f%%' % (index_profit_percent * 100)

    index_cost_percent = 0
    if stock.has_key('last_sell_date'):
        index_dh = previous_data_with_date(sh_index['code'], stock['last_sell_date'])
        sell_index = (index_dh['high'] + index_dh['low']) / 2
        # 处理累进买入的情况
        if buy_index != 0 and sell_index > buy_index and stock['last_sell_date'] != stock['last_buy_date']:
            sell_index = buy_index
        index_cost_percent = (sh_index['price'] - sell_index) / sell_index
    index_cost_percentstr = '       '
    if index_cost_percent < 0:
        index_cost_percentstr = '%6.2f%%' % (index_cost_percent * 100)

    #printstr = '(昨:%6.2f,今:%6.2f,现价:%6.2f,上次买:%6.2f卖:%6.2f,仓:%4d,盈:%s,回:%s,J:%6.2f,期:%s,栈:%s,点:%s)' \
    #    % (float(dh['close']) - float(dh['open']), \
    #    float(df['price'][0]) - float(df['open'][0]), \
    #    float(df['price'][0]), stock['last_buy'], \
    #    stock['last_sell'], position, profit_percentstr, regress_ratestr, j, \
    #    durationstr, stackstr, index_profit_percentstr)
    #stock['more_info'] = printstr
    stock['more_info_previousChange'] = float(dh['close']) - float(dh['open'])
    stock['more_info_todayChange'] = float(df['price'][0]) - float(df['open'][0])
    stock['more_info_currentPrice'] = float(df['price'][0])
    stock['more_info_lastBuy'] = stock['last_buy']
    stock['more_info_lastSell'] = stock['last_sell']
    stock['more_info_position'] = position
    stock['more_info_profit_percent'] = profit_percent
    stock['more_info_profit_percentstr'] = profit_percentstr
    stock['more_info_regress_rate'] = regress_rate
    stock['more_info_regress_ratestr'] = regress_ratestr
    stock['more_info_currentJ'] = j
    stock['more_info_duration_last'] = last
    stock['more_info_duration_far'] = far
    stock['more_info_durationstr'] = durationstr
    stock['more_info_stack'] = stack
    stock['more_info_stackstr'] = stackstr
    stock['more_info_index_profit_percent'] = index_profit_percent
    stock['more_info_index_profit_percentstr'] = index_profit_percentstr
    stock['more_info_index_cost_percent'] = index_cost_percent
    stock['more_info_index_cost_percentstr'] = index_cost_percentstr
    stock['more_info_today_change'] = position * (current_price - previous_close)

def whether_strong_buy(current_price, last_sell, last_buy):
    strong_buy = (last_buy == 0.0 and last_sell == 0.0) # 空仓且从未持有
    if (last_sell != 0.0 and last_buy == 0.0):
        strong_buy = current_price < last_sell - 0.5
    if (last_sell == 0.0 and last_buy != 0.0):
        next_buy = last_buy - (math.ceil(last_buy * 2 / 10) / 2)
        strong_buy = (strong_buy or current_price <= next_buy)
    if last_sell != 0.0:
        next_buy = last_sell - (math.ceil(last_sell * 2 / 10) / 2)
        strong_buy = (strong_buy or current_price <= next_buy)
        if strong_buy:
            next_buy = last_buy - (math.ceil(last_buy * 2 / 10) / 2)
            strong_buy = (strong_buy and current_price <= next_buy)
    return strong_buy

def whether_strong_sell(stock, current_price, last_sell, last_buy, today_high):
    recent_high = get_recent_high(stock, today_high)
    strong_sell = recent_high > last_buy * 1.2 and (recent_high - current_price) > (recent_high - last_buy) * 0.2
    return strong_sell

def get_recent_high(stock, today_high):
    recent_high = 0
    if stock.has_key('last_buy_date'):
        recent_high = get_recent_high_from_date(stock['code'], stock['last_buy_date'])
        if recent_high == 0:
            recent_high = today_high
    else:
        # go with high in last 14 days
        theDate = date.today() - timedelta(days=14)
        recent_high = get_recent_high_from_date(stock['code'], theDate)
    
    if recent_high < today_high:
        recent_high = today_high

    return recent_high

def get_recent_high_from_date(code, datestr):
    theDate = datetime.strptime(datestr, '%Y-%m-%d').date()
    recent_high = 0
    while theDate < date.today():
        dh = previous_data_with_date(code, datestr)
        if dh is not None and dh['high'] > recent_high:
            recent_high = dh['high']
        theDate = theDate + timedelta(days=1)
        datestr = theDate.strftime('%Y-%m-%d')
    return recent_high

def display_stock_group(stocks, action, line):
    global stock_index
    for stock in stocks:
        if (stock['action'] == action):
            display_stock(stock, line)
            stock_index += 1
            display_info(str(stock_index), 1, line)
            stock2line[str(stock_index)] = line
            line += 1
        
    return line

g_dark_enabled = 0

def display_stock(stock, line):
    global g_dark_enabled

    separator = 1
    index_width = 3
    code_width = 6
    name_width = 8
    action_width = 4
    previousChange_width = 10
    todayChange_width = 9
    currentPrice_width = 11
    lastBuy_width = 13
    lastSell_width = 9
    position_width = 7
    profit_width = 7
    regression_width = 6
    j_width = 8
    duration_width = 8
    stack_width = 8
    indexProfit_width = 10
    indexCost_width = 10
    turnover_width = 6
    todayChange_width = 10

    dark_enabled = (g_dark_enabled % 3 == 1 and stock['position'] > 0) or \
        (g_dark_enabled % 3 == 2 and stock['position'] == 0)
    colorpair = 6 if dark_enabled else 1

    # code
    location = 1 + index_width
    if not g_arg_simplified:
        display_info(stock['code'], location, line, colorpair)
    
    # name
        location += code_width + separator
    display_info(stock['name'], location, line, colorpair)

    # action
    location += name_width + separator
    if not g_arg_simplified:
        display_info(stock['action'], location, line, colorpair if dark_enabled else stock['action_color'])

    # more_info
        location += action_width + separator
        display_info('(昨:%6.2f' % (stock['more_info_previousChange']), location, line, colorpair)
        location += previousChange_width + separator
        display_info('今:%6.2f' % (stock['more_info_todayChange']), location, line, colorpair)
        location += todayChange_width + separator

    if g_arg_simplified:
        display_info('%6.2f/%6.2f' % (stock['more_info_currentPrice'], stock['more_info_lastBuy']), location, line, colorpair)
        location += 13 + separator
    else:
        display_info('现价:%6.2f' % (stock['more_info_currentPrice']), location, line, colorpair)
        location += currentPrice_width + separator
        display_info('上次买:%6.2f' % (stock['more_info_lastBuy']), location, line, colorpair)
        location += lastBuy_width + separator

    if not g_arg_simplified:
        display_info('卖:%6.2f' % (stock['more_info_lastSell']), location, line, colorpair)
        location += lastSell_width + separator
        display_info('仓:%4d' % (stock['more_info_position']), location, line, colorpair)
        location += position_width + separator
    currentProfit_color = 1
    duration = stock['more_info_duration_last'] if stock.has_key('more_info_duration_last') else 0
    if stock['more_info_profit_percent'] >= 7 + duration:
        currentProfit_color = 3
    display_info('盈:%s' % (stock['more_info_profit_percentstr']), location, line, colorpair if dark_enabled else currentProfit_color)
    location += profit_width + separator
    regress_rate_color = 1
    if (not stock.has_key('last100') and stock['more_info_regress_rate'] >= 28) \
        or stock.has_key('last100') and stock['last100'] and stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 58:
        regress_rate_color = 3
    display_info('回:%s' % (stock['more_info_regress_ratestr']), location, line, colorpair if dark_enabled else regress_rate_color)
    location += regression_width + separator
    currentJ_color = 1
    if stock['more_info_currentJ'] <= 20:
        currentJ_color = 2
    elif stock['more_info_currentJ'] >= 80:
        currentJ_color = 3
    display_info('J:%6.2f' % (stock['more_info_currentJ']), location, line, colorpair if dark_enabled else currentJ_color)
    location += j_width + separator
    if not g_arg_simplified:
        display_info('期:%s' % (stock['more_info_durationstr']), location, line, colorpair)
        location += duration_width + separator
        display_info('栈:%s' % (stock['more_info_stackstr']), location, line, colorpair)
        location += stack_width + separator
        index_profit_color = 1
        if stock['more_info_index_profit_percent'] * 100 >= 5:
            index_profit_color = 3
        display_info('点:%s' % (stock['more_info_index_profit_percentstr']), location, line, colorpair if dark_enabled else index_profit_color)
        location += indexProfit_width + separator
        index_cost_color = 1
        if stock['more_info_index_cost_percent'] * 100 <= -5 \
            and stock['more_info_index_profit_percent'] * 100 <= 0 \
            and stock['more_info_currentJ'] <= 20:
            index_cost_color = 2
        display_info('进:%s' % (stock['more_info_index_cost_percentstr']), location, line, colorpair if dark_enabled else index_cost_color)
        location += indexCost_width + separator
        display_info('转:%3d' % stock['turnover'], location, line, colorpair)
        location += turnover_width + separator
        display_info('详:%7d' % stock['more_info_today_change'], location, line, colorpair)
        location += todayChange_width + separator
        display_info(')', location, line, colorpair)

        # comment
        location += 1 + separator
        comment = ''
        comment_color = colorpair
        if stock.has_key('comment'):
            comment = stock['comment']
        if stock.has_key('margin'):
            comment = '[' + str(stock['margin'][0]) + ']' + comment
            comment_color = 2
        comment += ' ' * (30 - len(comment))
        display_info(comment, location, line, colorpair if dark_enabled else comment_color)

def display_highlight_info(index, highlight):
    separator = 1
    index_width = 3
    code_width = 6
    name_width = 8
    action_width = 4
    previousChange_width = 10
    todayChange_width = 9
    currentPrice_width = 11
    lastBuy_width = 13
    lastSell_width = 9
    position_width = 7
    profit_width = 7
    regression_width = 6
    j_width = 8
    duration_width = 8
    stack_width = 8
    indexProfit_width = 10
    indexCost_width = 10

    str = ' '
    color = 1
    if highlight:
        str = '-'
        color = 2

    location = 0
    display_info(str, location, index, color)
    location = index_width
    display_info(str, location, index, color)
    location += code_width + separator
    display_info(str, location, index, color)
    location += name_width + separator
    display_info(str, location, index, color)
    location += action_width + separator
    display_info(str, location, index, color)
    location += previousChange_width + separator
    display_info(str, location, index, color)
    location += todayChange_width + separator
    display_info(str, location, index, color)
    location += currentPrice_width + separator
    display_info(str, location, index, color)
    location += lastBuy_width + separator
    display_info(str, location, index, color)
    location += lastSell_width + separator
    display_info(str, location, index, color)
    location += position_width + separator
    display_info(str, location, index, color)
    location += profit_width + separator
    display_info(str, location, index, color)
    location += regression_width + separator
    display_info(str, location, index, color)
    location += j_width + separator
    display_info(str, location, index, color)
    location += duration_width + separator
    display_info(str, location, index, color)
    location += stack_width + separator
    display_info(str, location, index, color)
    location += indexProfit_width + separator
    display_info(str, location, index, color)
    location += indexCost_width + separator
    display_info(str, location, index, color)

def display_empty_line(line):  
    display_info(' ' * 192, 0, line)
    line += 1
    return line

def get_today_KDJ933(stock, current_price, today_high, today_low):
    if not stock.has_key('KDJ'):
        raise Exception('no KDJ' + stock['code'])
    real = is_tradedate(date.today())
    return compute_KDJ933(stock, date.today(), current_price, today_high, today_low, real)

def compute_KDJ933(stock, theDate, close, high, low, real):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if datetime.strptime(baseKDJDateStr, '%Y-%m-%d').date() == theDate:
        #print 'hit'
        return (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    (k_1, d_1, j_1) = get_previous_KDJ933(stock, theDate - timedelta(days=1))
    if not real:
        return (k_1, d_1, j_1)
    #print 'compute' + stock['code'] + ' ' + theDate.strftime('%Y-%m-%d') + ' ' + str(k_1) + ' ' + str(d_1) + " " + str(j_1)
    h9 = high
    l9 = low
    count = 1
    while count < 9:
        theDate = theDate - timedelta(days=1)
        datestr = theDate.strftime('%Y-%m-%d')
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
    datestr = theDate.strftime('%Y-%m-%d')
    dh = previous_data_with_date(stock['code'], datestr)
    if dh is None:
        print "dh is None. Shouldn't happen."
        return (0, 0, 0)
    if dh.has_key('theK') and (not reset_KDJ):
        return (dh['theK'], dh['theD'], dh['theJ'])
    (k, d, j) = compute_KDJ933(stock, theOriginDate, dh['close'], dh['high'], dh['low'], dh['real'])
    c_dayK.update({"code": stock['code'], "date": datestr}, {"$set": {"theK": k, "theD": d, "theJ": j}})
    return (k, d, j)

def previous_data(code):
    d = date.today()
    tdatestr = d.strftime('%Y-%m-%d')
    dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
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
                pdh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
                pdh = list(pdh)
                if len(pdh) != 0:
                    if len(dh) == 0:
                        c.insert({"code": code, "date": tdatestr, "close": pdh[0]['close'], "open": pdh[0]['open'], "high": pdh[0]['high']})
                    else:
                        c.update({"code": code, "date": tdatestr}, {"$set": {"high": pdh[0]['high']}})
                    dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
                    dh = list(dh)
                    return dh[0]
        if len(dh) == 0:
            c.insert({"code": code, "date": tdatestr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0]})
        else:
            c.update({"code": code, "date": tdatestr}, {"$set": {"high": df['high'][0]}})
        dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
        dh = list(dh)
        #print len(dh)

    return dh[0]

def previous_data_with_date(code, datestr):
    originDateStr = datestr
    dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
    dh = list(dh)
    
    if len(dh) == 0:
        log_status('Getting hist data for %s at %s' % (code, datestr))
        df = ts.get_hist_data(code, start=datestr, end=datestr)
        log_status('Done hist data for %s at %s' % (code, datestr))
        d = datetime.strptime(datestr, '%Y-%m-%d').date()
        if df is None or df.empty:
            d = d - timedelta(days=1)
            datestr = d.strftime('%Y-%m-%d')
            #df = ts.get_hist_data(code, start=datestr, end=datestr)
            dh = previous_data_with_date(code, datestr)
            c_dayK.insert({"code": code, "real": False, "date": originDateStr, "close": dh['close'], "open": dh['open'], "high": dh['high'], "low": dh['low']})
        else:
            c_dayK.insert({"code": code, "real": True, "date": originDateStr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0], "low": df['low'][0]})
        dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": originDateStr}}}])
        dh = list(dh)

    return dh[0]

def today_new_stocks():
    dh = db.new_stocks.find()
    dh = list(dh)
    new_stocks = []
    for record in dh:
        # see http://ryan-liu.iteye.com/blog/834831
        if record['ipo_date'] is not None and (datetime.strptime(record['ipo_date'], "%Y-%m-%dT%H:%M:%S.%fz").date() == date.today()):
            new_stocks.append(record['code'])
    return new_stocks

def is_tradedate(date):
    if date.weekday() == 5 or date.weekday() == 6:
        return False # Saturday or Sunday
    datestr = date.strftime('%Y-%m-%d')
    #print datestr
    if datestr in legalholidays.legal_holidays:
        #print 'False'
        return False
    if date.year < 2015 or date.year > 2016:
        raise Exception('year not supported!')
    return True

def update_metal():
    if g_arg_simplified:
        return
    conn = httplib.HTTPConnection("www.icbc.com.cn")
    conn.request("GET", "/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        #print theData
        dom = soupparser.fromstring(theData)
        # no tbody for first table. index starts from 1
        current_price = dom.xpath("//body/form/table/tr/td/table[6]/tbody/tr/td/div/table/tbody/tr[3]/td[3]")
        if len(current_price) > 0:
            current_price = current_price[0].text.strip()
            last_buy = precious_metals[0]["trades"][-1][3]
            profit_percent = math.floor((float(current_price) - last_buy) / last_buy * 10000) / 100
            if profit_percent > 0:
                profit_percentstr = str(profit_percent) + "%"
            else:
                profit_percentstr = " "
            display_info("银: " + current_price + " 盈: " + profit_percentstr, 100, 1)
    conn.close()

g_simplified_status = ''
def log_status(message):
    # temp: use space to avoid messy chars.
    global g_arg_simplified
    global g_simplified_status
    if g_arg_simplified:
        g_simplified_status = '' if len(g_simplified_status) > 8 else g_simplified_status + '.'
        display_info(g_simplified_status, 1, 0)
        return
    display_info('[%s]  %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message, ' ' * 30), 1, 0)
  
def display_info(str, x, y, colorpair=1):  
    '''''使用指定的colorpair显示文字'''  
    try:  
        global stdscr
        stdscr.addstr(y, x, str, curses.color_pair(colorpair))  
        stdscr.refresh()  
    except Exception,e:  
        pass  
  
def get_ch_and_continue():  
    '''''演示press any key to continue'''  
    global stdscr  
    #设置nodelay，为0时会变成阻塞式等待  
    stdscr.nodelay(0)  
    #输入一个字符  
    ch=stdscr.getch()  
    #重置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒  
    stdscr.nodelay(1)  
    return True  
  
def set_win():  
    '''''控制台设置'''  
    global stdscr  
    #使用颜色首先需要调用这个方法  
    curses.start_color()  
    #文字和背景色设置，设置了两个color pair，分别为1和2  
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)  
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLACK)  
    #关闭屏幕回显  
    curses.noecho()  
    #输入时不需要回车确认  
    curses.cbreak()  
    #设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒  
    stdscr.nodelay(1)  
  
def unset_win():  
    '''''控制台重置'''  
    global stdscr  
    #恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）  
    curses.nocbreak()  
    curses.echo()  
    #结束窗口  
    curses.endwin()  

def print_KDJ(stock, theDate):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if datetime.strptime(baseKDJDateStr, '%Y-%m-%d').date() == theDate:
        print baseKDJDateStr + " KDJ %6.2f %6.2f %6.2f" % (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    else:
        (k, d, j) = get_previous_KDJ933(stock, theDate)
        theDateStr = theDate.strftime('%Y-%m-%d')
        print theDateStr + " KDJ %6.2f %6.2f %6.2f" % (k, d, j)
        print_KDJ(stock, theDate - timedelta(days=1))

def print_KDJs(code):
    theDate = date.today()
    for stock in stockdata.all_stocks:
        if stock['code'] == code:
            print_KDJ(stock, theDate - timedelta(days=1))

const_tradeTimeOffset = 3

def is_trade_time(theTime):
    return (theTime.hour == 9 and theTime.minute >= 30 - const_tradeTimeOffset) or \
        (theTime.hour == 10) or (theTime.hour == 11 and theTime.minute <= 30 + const_tradeTimeOffset) or \
        (theTime.hour == 12 and theTime.minute >= 60 - const_tradeTimeOffset) or \
        (theTime.hour >= 13 and theTime.hour < 15) or \
        (theTime.hour == 15 and theTime.minute <= const_tradeTimeOffset)

def getch(stdscr):
    ichar = stdscr.getch()
    if ichar == 27 and stdscr.getch() == ord('['):
        ichar = stdscr.getch()
        if ichar == ord('A'):
            ichar = curses.KEY_UP
        elif ichar == ord('B'):
            ichar = curses.KEY_DOWN
        elif ichar == ord('C'):
            ichar = curses.KEY_RIGHT
        elif ichar == ord('D'):
            ichar = curses.KEY_LEFT
    return ichar

g_highlight_stock_index = 0
g_highlight_line = 5
g_show_all = False
g_hide_all = False

g_arg_simplified = False

def parse_args():
    global g_arg_simplified
    if len(sys.argv) >= 2 and sys.argv[1] == '-s':
        g_arg_simplified = True

DEBUG = False

if __name__=='__main__':  
    #global stdscr
    parse_args()
    if DEBUG:
        #try:  
            #set_win()
        #    preprocess_all()
        #    advice_all()
        #finally:
        #    pass
            #unset_win()  
        print_KDJs('601766')
    else:
        stdscr = curses.initscr()
        count = 0
        try:  
            set_win()  
            preprocess_all()
            while True:
                if count == 0 or is_trade_time(datetime.now()):
                    if g_hide_all:
                        for i in range(70):
                            display_info(' ' * 200, 0, i)
                    else:
                        advice_all()
                        if count == 0:
                            preprocess_all()
                            advice_all()

                count += 1
                seconds = 0
                while seconds < 30:
                    seconds += 1
                    time.sleep(1)
                    ichar = getch(stdscr)
                    if ichar == ord('d'):
                        g_dark_enabled += 1
                        advice_all()
                        seconds = 0
                    if ichar == ord('a'):
                        g_show_all = not g_show_all
                        advice_all()
                        seconds = 0
                    if ichar == ord('h'):
                        g_hide_all = not g_hide_all
                        break
                    stock_count = len(stock2line)
                    if ichar == ord('-') or ichar == curses.KEY_UP or ichar == curses.KEY_LEFT or ichar == ord('w'):
                        display_highlight_info(g_highlight_line, False)
                        g_highlight_stock_index = g_highlight_stock_index - 1
                        if g_highlight_stock_index <= 0: g_highlight_stock_index = stock_count
                        g_highlight_line = stock2line[str(g_highlight_stock_index)]
                        display_highlight_info(g_highlight_line, True)
                    elif ichar == ord('+') or ichar == curses.KEY_DOWN or ichar == curses.KEY_RIGHT or ichar == ord('s'):
                        display_highlight_info(g_highlight_line, False)
                        g_highlight_stock_index = g_highlight_stock_index + 1
                        if g_highlight_stock_index > stock_count: g_highlight_stock_index = 1
                        g_highlight_line = stock2line[str(g_highlight_stock_index)]
                        display_highlight_info(g_highlight_line, True)
                    elif ichar >= ord('0') and ichar <= ord('9'):
                        display_highlight_info(g_highlight_line, False)
                        g_highlight_stock_index = g_highlight_stock_index * 10 + ichar - ord('0')
                        if g_highlight_stock_index >= stock_count:
                            g_highlight_stock_index = ichar - ord('0')
                        if g_highlight_stock_index >= stock_count:
                            g_highlight_stock_index = 1
                        if g_highlight_stock_index <= 0: g_highlight_stock_index = stock_count
                        g_highlight_line = stock2line[str(g_highlight_stock_index)]
                        display_highlight_info(g_highlight_line, True)

                if count % 10 == 1:
                    update_metal()
                #time.sleep(60)
        #except Exception,e:  
        #    unset_win()  
        #    raise e  
        finally:  
            unset_win()
            pass

