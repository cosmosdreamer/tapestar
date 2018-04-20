# -*- coding: utf-8 -*-
import sys

# TODO: find a way to solve relative path issue.
sys.path.insert(0, './tapestar/monitor/')
sys.path.insert(0, '../monitor/')
sys.path.insert(0, './tapestar/hstock/')
sys.path.insert(0, '../hstock/')
sys.path.insert(0, './tapestar/util/')
sys.path.insert(0, '../util/')

import curses  
#from dateutil import rrule
import dateutil2 # own
from datetime import date, datetime, timedelta
import dbman # own
import funddata # own
import hadvise # own
import httplib
import json
import kdj # own
import legalholidays # own
import locale
from lxml import etree
import lxml.html.soupparser as soupparser
import math
import observer # own
import posman #own
import stockdata # own
import stockdata2 # own
import strutil # own
import tdal # own
import time
import tushare as ts

reload(sys)  
sys.setdefaultencoding('utf8')  

locale.setlocale(locale.LC_ALL, '')
system_code = locale.getpreferredencoding()

stdscr = None

all_stocks = stockdata.all_stocks_1
all_stocks_index = 1
all_stocks_realtime_quotes = None

sh_index = {
    'code': 'sh',
    'KDJ': { '2016-10-31': [67.27, 77.84, 46.12]},
    'price': 0,
}

whitelist_codes = ['601288', '000725', '603203'] # 农业银行, 京东方A, 快客股份
halt_codes = [] # real-time retrieve
vip_codes = ['002008', '002290', '002450'] # 大禾康

def preprocess_all():
    posman.reset()
    for stock in all_stocks:
        preprocess_stock(stock)

def preprocess_stock(stock):
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
                if stock['code'] not in whitelist_codes:
                    posman.investments['totalExceptWhitelist'] += direction * amount * price
                if (stock['code'] not in whitelist_codes) and (stock['code'] not in halt_codes):
                    posman.investments['totalExceptWhitelistAndHalt'] += direction * amount * price
                if stock['code'] in vip_codes:
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

g_advice_all_count = 0
g_display_group_index = 0

def display_overview(line):
    # Time 上证指数/涨跌/J 关注/持仓/停牌
    log_status('Getting sh index')
    df = ts.get_realtime_quotes(sh_index['code'])
    log_status('Done sh index')

    sh_index['price'] = today_price = float(df['price'][0])
    sh_index['high'] = today_high = float(df['high'][0])
    sh_index['low'] = today_low = float(df['low'][0])
    sh_index['pre_close'] = pre_close = float(df['pre_close'][0])

    (k, d, j) = kdj.get_today_KDJ933(sh_index, today_price, today_high, today_low)
    today_change_percent = (today_price - pre_close) / pre_close * 100
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    now = 'Time: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f  关注: %2d 持仓: %2d 停牌: %2d' \
        % (time_str, \
        today_price, today_change_percent, j, \
        len(all_stocks), posman.investments['positioned_stock_count'], len(halt_codes))
    if g_arg_simplified:
        now = 'T: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f' \
        % (time_str, \
        today_price, today_change_percent, j)
    display_info(now, 1, line)
    line += 1

    # workaround to color index J
    if not g_arg_simplified:
        indexJ = '%6.2f' % j
        indexJ_color = 1
        if j <= 20:
            indexJ_color = 2
        elif j >= 80:
            indexJ_color = 3
        display_info(indexJ, 59, 1, indexJ_color)

    return line

def display_indexed_cost_dist(line):
    indexed_coststr = '[>5000:%6.2f%%|>4500:%6.2f%%|>4000:%6.2f%%|>3500:%6.2f%%|>3000:%6.2f%%|>2500:%6.2f%%|>2000:%6.2f%%|>1500:%6.2f%%] - %7.2f' \
        % (posman.investments['indexed_cost'][0]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][1]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][2]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][3]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][4]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][5]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][6]/posman.investments['total'] * 100, \
        posman.investments['indexed_cost'][7]/posman.investments['total'] * 100, posman.investments['indexedTotal'] / posman.investments['total'])
    if not g_arg_simplified:
        display_info(indexed_coststr, 1, line)
        line += 1
    return line

def display_cost(line):
    current_invest_base = (1 - (sh_index['price'] / 500 - 2) * 0.1) * posman.investments['totalBase']
    invest_status = '仓/允: %6.0f/%6.0f, 除农: %6.0f, 除农比: %6.2f%%, 除停: %6.0f, 除停比: %6.2f%%, 大禾康占比: %6.2f%%' \
        % (posman.investments['total'], current_invest_base, posman.investments['totalExceptWhitelist'], \
        (posman.investments['totalExceptWhitelist'] - (current_invest_base - posman.investments['totalBase'] * const_baseOffsetPercent)) / (posman.investments['totalBase'] * const_baseOffsetPercent * 2) * 100, \
        posman.investments['totalExceptWhitelistAndHalt'], \
        (posman.investments['totalExceptWhitelistAndHalt'] - (current_invest_base - posman.investments['totalBase'] * const_baseOffsetPercent)) / (posman.investments['totalBase'] * const_baseOffsetPercent * 2) * 100, \
        posman.investments['totalVip'] / posman.investments['total'] * 100)
    if not g_arg_simplified:
        display_info(invest_status, 1, line)
        line += 1
    return line
 
def display_fine_indexed_cost_dist(line):
    baseIndex = int(sh_index['price']) / 100 * 100
    indexed_coststr = '[>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%]' \
        % (baseIndex + 300, posman.investments['fine_indexed_cost'][0]/posman.investments['total'] * 100, \
        baseIndex + 200, posman.investments['fine_indexed_cost'][1]/posman.investments['total'] * 100, \
        baseIndex + 100, posman.investments['fine_indexed_cost'][2]/posman.investments['total'] * 100, \
        baseIndex, posman.investments['fine_indexed_cost'][3]/posman.investments['total'] * 100, \
        baseIndex - 100, posman.investments['fine_indexed_cost'][4]/posman.investments['total'] * 100, \
        baseIndex - 200, posman.investments['fine_indexed_cost'][5]/posman.investments['total'] * 100, \
        baseIndex - 300, posman.investments['fine_indexed_cost'][6]/posman.investments['total'] * 100, \
        baseIndex - 400, posman.investments['fine_indexed_cost'][7]/posman.investments['total'] * 100)
    if not g_arg_simplified:
        display_info(indexed_coststr, 1, line)
        line += 1
    return line

def get_stock_code(stock):
    return stock['code']

def advice_all():
    global positioned_stock_count
    global g_advice_all_count
    global g_display_group_index
    global all_stocks_realtime_quotes
    theTime = datetime.now()

    line = 1

    # line 1
    line = display_overview(line)
    # line 2
    line = display_indexed_cost_dist(line)
    # line 3
    line = display_cost(line)
    # line 4
    line = display_fine_indexed_cost_dist(line)
    # line 5
    line = display_header(line)
    
    new_stocks = today_new_stocks()
    if len(new_stocks) > 0:
        display_info('今新: ' + ' '.join(new_stocks), 1, 4)
        line += 1

    total = len(all_stocks)
    all_codes = map(get_stock_code, all_stocks)
    all_stocks_realtime_quotes = None
    batch_all = total / 15 + (1 if total % 15 != 0 else 0)
    for ind in range(batch_all):
        start = ind * 15
        end = ind * 15 + 15
        end = end if end < total else total
        log_status('(%d/%d) Getting realtime quotes' % (ind + 1, batch_all))
        df = ts.get_realtime_quotes(all_codes[start : end])
        log_status('(%d/%d) Done realtime quotes' % (ind + 1, batch_all))
        if all_stocks_realtime_quotes is None:
            all_stocks_realtime_quotes = df
        else:
            all_stocks_realtime_quotes = all_stocks_realtime_quotes.append(df, True)

    ind = 0
    for stock in all_stocks:
        advise(stock, len(all_stocks), ind)
        ind += 1
        if g_show_exceptX and stock['action'] == 'HIDE' and stock.has_key('comment') and stock['comment'].find('XXX') != -1:
            stock['action'] = 'XXX'

    all_stocks.sort(compCurrentJ)
    global stock_index
    stock_index = 0
    if not g_show_all or (g_show_all and g_display_group_index == 0):
        line = display_stock_group(all_stocks, "卖出", line)
        line = display_empty_line(line)
        line = display_stock_group(all_stocks, "买入", line)
        line = display_empty_line(line)
        line = display_stock_group(all_stocks, "弱买", line)
        line = display_stock_group(all_stocks, "追高", line)
        line = display_empty_line(line)
        line = display_stock_group(all_stocks, "忖卖", line)
        line = display_stock_group(all_stocks, "弱卖", line)
        line = display_stock_group(all_stocks, "薄卖", line)
        line = display_stock_group(all_stocks, "亏卖", line)
    if not g_show_all or (g_show_all and g_display_group_index == 1):
        line = display_empty_line(line)
        line = display_stock_group(all_stocks, "持有", line)
        line = display_empty_line(line)
        line = display_stock_group(all_stocks, "观望", line)
        line = display_stock_group(all_stocks, " -- ", line)
        if g_show_all or g_show_exceptX:
            line = display_stock_group(all_stocks, "HIDE", line)
            line = display_stock_group(all_stocks, "    ", line)

    line = display_empty_line(line)
    line = display_empty_line(line)

    # 推荐产品
    origin_line = line
    if g_advice_all_count % 60 == 0:
        for item in observer.invest_items:
            item['comp_current'] = item['current']()
            item['comp_advice'] = item['advice'](item, item['comp_current'])
        for item in funddata.all_sfunds:
            item['comp_current'] = item['current'](item['code'])
            item['comp_advice'] = item['advice'](item, item['comp_current'])
    for item in observer.invest_items:
        if item['comp_advice'] != '':
            advice_str = '    %s    %9.3f    %s' % (item['name'], item['comp_current'], item['comp_advice'])
            display_info(advice_str, 1, line)
            line += 1
    for item in funddata.all_sfunds:
        if item['comp_advice'] != '':
            advice_str = '    %s    %9.3f    %s' % (item['name'], item['comp_current'], item['comp_advice'])
            if item.has_key('comment'):
                    advice_str += item['comment']
            display_info(advice_str, 1, line)
            line += 1
    g_advice_all_count += 1
    if line == origin_line:
        display_info('无推荐', 1, line)
        line += 1

    line = display_empty_line(line)

    #TODO hadvise.advice_all(line)

    line = display_empty_line(line)

    elapsed = datetime.now() - theTime
    display_info(' ' + str(elapsed).split('.')[0], 0, line + 1)

def display_header(line):
    if not g_arg_simplified:
        display_info('                          昨幅   今幅    现价   前买   前卖 仓位 盈利 回撤     J  久期 档位     指盈    指跌  转    浮盈   备注', 1, line)
        line += 1
    return line

const_profitPercent = 0.06
const_deficitPercent = 0.1

def advise(stock, total, index):
    #log_status('(%d/%d) Getting realtime quotes for %s' % (index + 1, total, stock['code']))
    #df = ts.get_realtime_quotes(stock['code'])
    #log_status('(%d/%d) Done realtime quotes for %s' % (index + 1, total, stock['code']))
    df = all_stocks_realtime_quotes
    code = stock['code']
    current_price = float(df['price'][index])
    today_high = float(df['high'][index])
    today_low = float(df['low'][index])
    today_open = float(df['open'][index])
    position = stock['position']
    last_sell = stock['last_sell']
    last_buy = stock['last_buy']
    
    # name
    stock['name'] = df['name'][index]
    namelen = strutil.width(stock['name'])
    if namelen < 8:
        for i in range(8 - namelen):
            stock['name'] += ' ' # '_'
    #print len(stock['name'])
    #print namelen

    dh = tdal.previous_data(stock['code'], log_status)
    
    previous_close = float(dh['close'])
    previous_open = float(dh['open'])
    action = ''
    action_color = 1

    recent_low = get_recent_low(stock)
    recent_rise_rate = (current_price - recent_low) / recent_low * 100 if recent_low != 0 else 0.0

    last_profit = stock['last_buy_position'] * (current_price - last_buy)
    if position == 0 and recent_rise_rate >= 20.0 and recent_rise_rate <= 28.0:
        pass
    # 设置了margin
    elif not g_show_all and stock.has_key('margin'):
        if len(stock['margin']) > 1 and stock['margin'][0] < current_price and stock['margin'][1] > current_price \
            or len(stock["margin"]) == 1 and stock['margin'][0] < current_price and (position == 0 or current_price < stock["last_buy"] * (1 + const_profitPercent)):
            stock['action'] = "HIDE"
            return
        elif last_profit > 0 and last_profit < 110.0:
            stock['action'] = "HIDE"
            return
    # last_buy * 0.x < current < last_buy * 1.x (暗示有仓位)
    elif not g_show_all and current_price > stock["last_buy"] * (1 - const_deficitPercent) and current_price < stock["last_buy"] * (1 + const_profitPercent):
        stock['action'] = "HIDE"
        return
    # 空仓，但操作过，卖飞了
    elif not g_show_all and position == 0 and stock["last_sell"] > 0 and current_price * (1 + const_profitPercent) > stock["last_sell"]:
        stock['action'] = "HIDE"
        return
    # 空仓，但操作过，没跌到位。熊市启用，震荡市可comment掉
    elif not g_show_all and position == 0 and stock["last_sell"] > 0 and current_price * (1 - const_deficitPercent) > stock["last_sell"]:
        stock['action'] = "HIDE"
        return
    # profit不足110
    elif not g_show_all and last_profit > 0 and last_profit < 110.0:
        stock['action'] = "HIDE"
        return

    j = 0
    if stock.has_key('KDJ'):
        (k, d, j) = kdj.get_today_KDJ933(stock, current_price, today_high, today_low)
    if today_open == 0:
        action = "    "
    elif position == 0 and recent_rise_rate >= 20.0 and recent_rise_rate <= 28.0:
        action = '买入'
        action_color = 2
    elif current_price - today_open > 0:
        if previous_close - previous_open < 0:
            strong_buy = whether_strong_buy(current_price, last_sell, last_buy)
            strong_buy = False if (j > 80) else strong_buy
            if stock.has_key('last_buy_date'):
                # 距离上次买入需超过3个月或下跌超过30%
                strong_buy = False if (date.today() - datetime.strptime(stock['last_buy_date'], '%Y-%m-%d').date()).days < 90 or \
                    current_price > stock["last_buy"] * 0.70 else strong_buy
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
    elif current_price - today_open < 0:
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
    if last_buy > 0 :#and position > 0:
        profit_percent = math.floor((current_price - last_buy) / last_buy * 100)
    elif last_sell > 0 :#and position > 0:
        profit_percent = math.floor((current_price - last_sell) / last_sell * 100)
        if profit_percent > 0:
            profit_percent = 0
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
        recent_high = get_recent_high(stock, today_high)
        regress_rate = math.ceil((recent_high - current_price) / (recent_high - last_buy) * 100)
        #if code == '002299':
        #    print str(recent_high) + ' ' + str(current_price) + ' ' + str(last_buy)
        regress_ratestr = '%2d%%' % regress_rate
    if position == 0 and recent_rise_rate > 0:
        regress_rate = recent_rise_rate
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
        index_dh = tdal.previous_data_with_date(sh_index['code'], stock['last_buy_date'])
        buy_index = (index_dh['high'] + index_dh['low']) / 2
        index_profit_percent = (sh_index['price'] - buy_index) / buy_index
    index_profit_percentstr = '       '
    if index_profit_percent != 0:
        index_profit_percentstr = '%6.2f%%' % (index_profit_percent * 100)

    index_cost_percent = 0
    if stock.has_key('last_sell_date'):
        index_dh = tdal.previous_data_with_date(sh_index['code'], stock['last_sell_date'])
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
    stock['more_info_previousChange'] = previous_close - previous_open
    stock['more_info_todayChange'] = current_price - today_open
    stock['more_info_currentPrice'] = current_price
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

def get_recent_low(stock):
    # mem cache
    if stock.has_key('recent_low'):
        return stock['recent_low']
    # db
    code = stock['code']
    today_str = dateutil2.format_date(date.today())
    dh = dbman.query_history(code, today_str)
    if len(dh) > 0 and dh[0].has_key('recent_low'):
        recent_low = stock['recent_low'] = dh[0]['recent_low']
        return recent_low
    # network
    code = stock['code']
    #theBeginDate = datetime.strptime(datestr, '%Y-%m-%d').date()
    theBeginDate = (date.today() - timedelta(days=90)).strftime('%Y-%m-%d')
    theEndDate = date.today().strftime('%Y-%m-%d')
    recent_low = 10000.0
    log_status('Getting hist data for %s' % (code))
    df = ts.get_hist_data(code, start=theBeginDate, end=theEndDate)
    log_status('Done hist data for %s' % (code))
    if df is not None:
        for index in range(len(df['low'])):
            if df['low'][index] < recent_low:
                recent_low = df['low'][index]
    else:
        recent_low = 0.0
    # update db
    if len(dh) > 0:
        dbman.update_history_recent_low(code, today_str, recent_low)
    stock['recent_low'] = recent_low
    return recent_low

def get_recent_high_from_date(code, datestr):
    theDate = datetime.strptime(datestr, '%Y-%m-%d').date()
    recent_high = 0
    while theDate < date.today():
        dh = tdal.previous_data_with_date(code, datestr)
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
    #previousChange_width = 10
    #todayChange_width = 9
    #currentPrice_width = 11
    #lastBuy_width = 13
    #lastSell_width = 9
    #position_width = 7
    #profit_width = 7
    #regression_width = 6
    #j_width = 8
    #duration_width = 8
    #stack_width = 8
    #indexProfit_width = 10
    #indexCost_width = 10
    #turnover_width = 6
    #todayChange_width = 10
    previousChange_width = 6
    todayChange_width = 6
    currentPrice_width = 6
    lastBuy_width = 6
    lastSell_width = 6
    position_width = 4
    profit_width = 4
    regression_width = 3
    j_width = 6
    duration_width = 5
    stack_width = 5
    indexProfit_width = 7
    indexCost_width = 7
    turnover_width = 3
    todayChange_width = 7

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
        #display_info('(昨:%6.2f' % (stock['more_info_previousChange']), location, line, colorpair)
        display_info('%6.2f' % (stock['more_info_previousChange']), location, line, colorpair)
        location += previousChange_width + separator
        #display_info('今:%6.2f' % (stock['more_info_todayChange']), location, line, colorpair)
        display_info('%6.2f' % (stock['more_info_todayChange']), location, line, colorpair)
        location += todayChange_width + separator

    if g_arg_simplified:
        display_info('%6.2f/%6.2f' % (stock['more_info_currentPrice'], stock['more_info_lastBuy']), location, line, colorpair)
        location += 13 + separator
    else:
        #display_info('现价:%6.2f' % (stock['more_info_currentPrice']), location, line, colorpair)
        display_info('%6.2f' % (stock['more_info_currentPrice']), location, line, colorpair)
        location += currentPrice_width + separator
        #display_info('上次买:%6.2f' % (stock['more_info_lastBuy']), location, line, colorpair)
        display_info('%6.2f' % (stock['more_info_lastBuy']), location, line, colorpair)
        location += lastBuy_width + separator

    if not g_arg_simplified:
        #display_info('卖:%6.2f' % (stock['more_info_lastSell']), location, line, colorpair)
        display_info('%6.2f' % (stock['more_info_lastSell']), location, line, colorpair)
        location += lastSell_width + separator
        #display_info('仓:%4d' % (stock['more_info_position']), location, line, colorpair)
        display_info('%4d' % (stock['more_info_position']), location, line, colorpair)
        location += position_width + separator
    currentProfit_color = 1
    duration = stock['more_info_duration_last'] if stock.has_key('more_info_duration_last') else 0
    if stock['more_info_profit_percent'] >= 7 + duration:
        currentProfit_color = 3
    elif stock['more_info_lastBuy'] == 0 and stock['more_info_profit_percentstr'] != '':
        currentProfit_color = 2
    #display_info('盈:%s' % (stock['more_info_profit_percentstr']), location, line, colorpair if dark_enabled else currentProfit_color)
    display_info('%s' % (stock['more_info_profit_percentstr']), location, line, colorpair if dark_enabled else currentProfit_color)
    location += profit_width + separator
    regress_rate_color = 1
    #if (not stock.has_key('last100') and stock['more_info_regress_rate'] >= 28) \
    #    or stock.has_key('last100') and stock['last100'] and stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 58:
    if (stock['more_info_stack'] != 1 and stock['more_info_regress_rate'] >= 28) \
        or (stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 48):
        regress_rate_color = 3
    #display_info('回:%s' % (stock['more_info_regress_ratestr']), location, line, colorpair if dark_enabled else regress_rate_color)
    display_info('%s' % (stock['more_info_regress_ratestr']), location, line, colorpair if dark_enabled else regress_rate_color)
    location += regression_width + separator
    currentJ_color = 1
    if stock['more_info_currentJ'] <= 20:
        currentJ_color = 2
    elif stock['more_info_currentJ'] >= 80:
        currentJ_color = 3
    #display_info('J:%6.2f' % (stock['more_info_currentJ']), location, line, colorpair if dark_enabled else currentJ_color)
    display_info('%6.2f' % (stock['more_info_currentJ']), location, line, colorpair if dark_enabled else currentJ_color)
    location += j_width + separator
    if not g_arg_simplified:
        #display_info('期:%s' % (stock['more_info_durationstr']), location, line, colorpair)
        display_info('%s' % (stock['more_info_durationstr']), location, line, colorpair)
        location += duration_width + separator
        #display_info('栈:%s' % (stock['more_info_stackstr']), location, line, colorpair)
        display_info('%s' % (stock['more_info_stackstr']), location, line, colorpair)
        location += stack_width + separator
        index_profit_color = 1
        if stock['more_info_index_profit_percent'] * 100 >= 5:
            index_profit_color = 3
        #display_info('点:%s' % (stock['more_info_index_profit_percentstr']), location, line, colorpair if dark_enabled else index_profit_color)
        display_info('%s' % (stock['more_info_index_profit_percentstr']), location, line, colorpair if dark_enabled else index_profit_color)
        location += indexProfit_width + separator
        index_cost_color = 1
        if stock['more_info_index_cost_percent'] * 100 <= -5 \
            and stock['more_info_index_profit_percent'] * 100 <= 0 \
            and stock['more_info_currentJ'] <= 20:
            index_cost_color = 2
        #display_info('进:%s' % (stock['more_info_index_cost_percentstr']), location, line, colorpair if dark_enabled else index_cost_color)
        display_info('%s' % (stock['more_info_index_cost_percentstr']), location, line, colorpair if dark_enabled else index_cost_color)
        location += indexCost_width + separator
        #display_info('转:%3d' % stock['turnover'], location, line, colorpair)
        display_info('%3d' % stock['turnover'], location, line, colorpair)
        location += turnover_width + separator
        #display_info('详:%7d' % stock['more_info_today_change'], location, line, colorpair)
        display_info('%7d' % stock['more_info_today_change'], location, line, colorpair)
        location += todayChange_width + separator
        #display_info(')', location, line, colorpair)

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

def today_new_stocks():
    dh = dbman.db.new_stocks.find()
    dh = list(dh)
    new_stocks = []
    for record in dh:
        # see http://ryan-liu.iteye.com/blog/834831
        if record['ipo_date'] is not None and (datetime.strptime(record['ipo_date'], "%Y-%m-%dT%H:%M:%S.%fz").date() == date.today()):
            new_stocks.append(record['code'])
    return new_stocks

# tested
def is_trade_date(date):
    if date.weekday() == 5 or date.weekday() == 6:
        return False # Saturday or Sunday
    datestr = date.strftime('%Y-%m-%d')
    #print datestr
    if datestr in legalholidays.legal_holidays:
        #print 'False'
        return False
    if date.year < 2015 or date.year > 2018:
        raise Exception('year not supported!')
    return True

#def update_metal():
#    if g_arg_simplified:
#        return
#    conn = httplib.HTTPConnection("www.icbc.com.cn")
#    conn.request("GET", "/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx")
#    res = conn.getresponse()
#    if res.status == 200:
#        theData = res.read()
#        #print theData
#        dom = soupparser.fromstring(theData)
#        # no tbody for first table. index starts from 1
#        current_price = dom.xpath("//body/form/table/tr/td/table[6]/tbody/tr/td/div/table/tbody/tr[3]/td[3]")
#        if len(current_price) > 0:
#            current_price = current_price[0].text.strip()
#            last_buy = precious_metals[0]["trades"][-1][3]
#            profit_percent = math.floor((float(current_price) - last_buy) / last_buy * 10000) / 100
#            if profit_percent > 0:
#                profit_percentstr = str(profit_percent) + "%"
#            else:
#                profit_percentstr = " "
#            display_info("银: " + current_price + " 盈: " + profit_percentstr, 100, 1)
#    conn.close()

g_simplified_status = ''

# no-test
def log_status(message):
    # temp: use space to avoid messy chars.
    global g_arg_simplified
    global g_simplified_status
    if g_arg_simplified:
        g_simplified_status = '' if len(g_simplified_status) > 8 else g_simplified_status + '.'
        display_info(g_simplified_status, 1, 0)
        return
    display_info('[%s]  %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message, ' ' * 30), 1, 0)

# no-test
def display_info(str, x, y, colorpair=1):  
    '''''使用指定的colorpair显示文字'''  
    try:  
        global stdscr
        stdscr.addstr(y, x, str, curses.color_pair(colorpair))  
        stdscr.refresh()  
    except Exception,e:  
        pass  

# no-test
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

# no-test
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

# no-test
def unset_win():  
    '''''控制台重置'''  
    global stdscr  
    #恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）  
    curses.nocbreak()  
    curses.echo()  
    #结束窗口  
    curses.endwin()  

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

const_tradeTimeOffset = 3

# tested
def is_trade_time(theTime):
    return (theTime.hour == 9 and theTime.minute >= 30 - const_tradeTimeOffset) or \
        (theTime.hour == 10) or (theTime.hour == 11 and theTime.minute <= 30 + const_tradeTimeOffset) or \
        (theTime.hour == 12 and theTime.minute >= 60 - const_tradeTimeOffset) or \
        (theTime.hour >= 13 and theTime.hour < 15) or \
        (theTime.hour == 15 and theTime.minute <= const_tradeTimeOffset)

# no-test
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
g_show_exceptX = False

g_arg_simplified = False

# no-test
def parse_args():
    global g_arg_simplified
    if len(sys.argv) >= 2 and sys.argv[1] == '-s':
        g_arg_simplified = True

DEBUG = False
stdscr = None

def run_main():  
    global stdscr
    global g_show_all
    global g_hide_all
    global g_dark_enabled
    global g_show_exceptX
    global g_highlight_stock_index
    global g_highlight_line
    global g_display_group_index
    global all_stocks
    global all_stocks_index
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
            hadvise.preprocess_all()
            while True:
                if count == 0 or is_trade_time(datetime.now()):
                    if g_hide_all:
                        stdscr.clear()
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
                    if ichar == ord('^'):
                        if all_stocks_index == 1:
                            all_stocks = stockdata2.all_stocks_2
                        else:
                            all_stocks = stockdata.all_stocks_1
                        all_stocks_index = 2 if all_stocks_index == 1 else 1
                        stdscr.clear()
                        preprocess_all()
                        advice_all()
                        seconds = 0
                    if ichar == ord('p'):
                        g_display_group_index = 0 if g_display_group_index == 1 else 1
                        advice_all()
                        seconds = 0
                    if ichar == ord('d'):
                        g_dark_enabled += 1
                        advice_all()
                        seconds = 0
                    if ichar == ord('a'):
                        g_show_all = not g_show_all
                        stdscr.clear()
                        advice_all()
                        seconds = 0
                    if ichar == ord('h'):
                        g_hide_all = not g_hide_all
                        break
                    if ichar == ord('x'):
                        g_show_all = not g_show_all
                        g_show_exceptX = not g_show_exceptX
                        advice_all()
                        seconds = 0
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

                #if count % 10 == 1:
                #    update_metal()
                #time.sleep(60)
        #except Exception,e:  
        #    unset_win()  
        #    raise e  
        finally:  
            unset_win()
            pass

def profile_main():
    global stdscr
    stdscr = curses.initscr()
    try:  
        set_win()
        preprocess_all()
        advice_all()
    finally:
        unset_win()  

if __name__=='__main__':
    from autoreload import run_with_reloader
    run_with_reloader(run_main)

