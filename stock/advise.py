# -*- coding: utf-8 -*-
import sys

# TODO: find a way to solve relative path issue.
sys.path.insert(0, './tapestar/monitor/')
sys.path.insert(0, '../monitor/')
sys.path.insert(0, './tapestar/hstock/')
sys.path.insert(0, '../hstock/')
sys.path.insert(0, './tapestar/util/')
sys.path.insert(0, '../util/')

import columns # own
import const # own
import dateutil2 # own
from datetime import date, datetime, timedelta
import dbman # own
import funddata # own
import hadvise # own
import keys # own
import kdj # own
import legalholidays # own
import locale
from lxml import etree
import math
import observer # own
import options # own
import overview # own
import posman # own
import pp # own
import screen # own
import sort # own
import stockdata # own
import stockdata2 # own
import strutil # own
import tdal # own
import time
import tushare as ts
import util # own

reload(sys)  
sys.setdefaultencoding('utf8')  

locale.setlocale(locale.LC_ALL, '')
system_code = locale.getpreferredencoding()

all_stocks = stockdata.all_stocks_1
all_stocks_index = 1
all_stocks_realtime_quotes = None

stock_index = 0
#stock2line = {}

g_advice_all_count = 0
g_display_group_index = 0

def display_new_stocks(line):
    new_stocks = today_new_stocks()
    if len(new_stocks) > 0:
        screen.display_info('今新: ' + ' '.join(new_stocks), 1, line)
        line += 1
    return line

def advice_all():
    global positioned_stock_count
    global g_advice_all_count
    global g_display_group_index
    global all_stocks_realtime_quotes
    global all_stocks
    startTime = datetime.now()

    line = 1

    # line 1-4?
    line = overview.display(line, all_stocks, log_status)
    # line 5
    line = display_new_stocks(line)
    # line 6
    line = display_header(line)

    all_stocks_realtime_quotes = tdal.get_realtime_quotes(all_stocks, log_status)

    ind = 0
    for stock in all_stocks:
        advise(stock, len(all_stocks), ind)
        ind += 1
        if g_show_exceptX and stock['action'] == 'HIDE' and stock.has_key('comment') and stock['comment'].find('XXX') != -1:
            stock['action'] = 'XXXX'

    origin_all_stocks = all_stocks
    all_stocks = filter(lambda stock: stock['action'] != 'XXXX' and stock['action'] != 'HIDE' and stock['action'] != '    ', all_stocks)
    #all_stocks.sort(compAction)
    #all_stocks.sort(util.compCurrentJ)
    all_stocks.sort(sort.compProfit)
    global stock_index
    stock_index = 0
    for stock in all_stocks:
        display_stock(stock, line)
        stock_index += 1
        screen.display_info(str(stock_index), 1, line)
        line += 1
    all_stocks = origin_all_stocks

    display_empty_line(line) # workaround
    line = display_current_amount(line, all_stocks)

    line = display_empty_line(line)
    line = display_empty_line(line)

    # 推荐产品
    origin_line = line
    if g_advice_all_count % 60 == 0:
        for item in observer.invest_items:
            item['comp_current'] = item['current']()
            item['comp_advice'] = item['advice'](item, item['comp_current'])
        for item in funddata.all_sfunds:
            item['comp_current'] = item['current'](item['code'], log_status)
            item['comp_advice'] = item['advice'](item, item['comp_current'])
    for item in observer.invest_items:
        if item['comp_advice'] != '':
            advice_str = '    %s    %9.3f    %s' % (item['name'], item['comp_current'], item['comp_advice'])
            screen.display_info(advice_str, 1, line)
            line += 1
    for item in funddata.all_sfunds:
        if item['comp_advice'] != '':
            advice_str = '    %s    %9.3f    %s' % (item['name'], item['comp_current'], item['comp_advice'])
            if item.has_key('comment'):
                    advice_str += item['comment']
            screen.display_info(advice_str, 1, line)
            line += 1
    g_advice_all_count += 1
    if line == origin_line:
        screen.display_info('无推荐', 1, line)
        line += 1

    line = display_empty_line(line)

    #TODO hadvise.advice_all(line)

    line = display_empty_line(line)

    elapsed = datetime.now() - startTime
    screen.display_info(' ' + str(elapsed).split('.')[0], 0, line + 1)

def display_current_amount(line, stocks):
    currentAmount = 0.0
    ind = 0
    for stock in stocks:
        if stock.has_key(keys.trades):
            for trade in stock[keys.trades]:
                direction = trade[1]
                volume = trade[2]
                if direction == 1:
                    price = float(all_stocks_realtime_quotes['price'][ind])
                    currentAmount += volume * price
        ind += 1
    screen.display_info(' %6.0f' % currentAmount, 0, line)
    line += 1
    return line
    

def display_header(line):
    if not options.g_arg_simplified:
        col = 1
        for i in range(len(columns.columns)):
            width = columns.columns[i]['width']
            if columns.columns[i]['header'] != '':
                header = columns.columns[i]['header']
                header_width = strutil.width(header.decode('utf-8'))
                if header_width < width:
                    header = ' ' * (width - header_width) + header
                screen.display_info(header, col, line)
            col += width + 1  
        line += 1
    return line


def advise(stock, total, index):
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
    stock['action_color'] = action_color

    recent_low = get_recent_low(stock)
    recent_rise_rate = (current_price - recent_low) / recent_low * 100 if recent_low != 0 else 0.0
    
    currentAmount = 0.0
    if stock.has_key(keys.trades):
        for trade in stock[keys.trades]:
            direction = trade[1]
            volume = trade[2]
            if direction == 1:
                currentAmount += volume * current_price
    stock['currentAmount'] = currentAmount

    last_profit = stock['last_buy_position'] * (current_price - last_buy)
    if position == 0 and recent_rise_rate >= 20.0 and recent_rise_rate <= 28.0 and not stock.has_key('margin'):
        pass
    # 设置了margin
    elif not g_show_all and stock.has_key('margin'):
        if len(stock['margin']) > 1 and stock['margin'][0] < current_price and stock['margin'][1] > current_price \
            or len(stock["margin"]) == 1 and stock['margin'][0] < current_price and (position == 0 or current_price < stock["last_buy"] * (1 + const.const_profitPercent)):
            stock['action'] = "HIDE"
            return
        elif last_profit > 0 and last_profit < 110.0:
            stock['action'] = "HIDE"
            return
    # 设置了reminder
    elif not g_show_all and stock.has_key('reminder'):
        if date.today() > dateutil2.parse_date(stock['reminder']):
            stock['comment'] = 'REMINDER'
            #stock['action'] = "买入"
        else:
            stock['action'] = "HIDE"
            return
    # last_buy * 0.x < current < last_buy * 1.x (暗示有仓位)
    elif not g_show_all and current_price > stock["last_buy"] * (1 - const.const_deficitPercent) and current_price < stock["last_buy"] * (1 + const.const_profitPercent):
        stock['action'] = "HIDE"
        return
    # 空仓，但操作过，卖飞了
    elif not g_show_all and position == 0 and stock["last_sell"] > 0 and current_price * (1 + const.const_profitPercent) > stock["last_sell"]:
        stock['action'] = "HIDE"
        return
    # 空仓，但操作过，没跌到位。熊市启用，震荡市可comment掉
    elif not g_show_all and position == 0 and stock["last_sell"] > 0 and current_price > stock["last_sell"] * (1 - const.const_deficitPercent):
        stock['action'] = "HIDE"
        return
    # profit不足110
    elif not g_show_all and last_profit > 0 and last_profit < 110.0:
        stock['action'] = "HIDE"
        return

    j = 0
    if stock.has_key('KDJ'):
        (k, d, j) = kdj.get_today_KDJ933(stock, current_price, today_high, today_low, log_status)
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
    
    if (current_price == 0 or today_open == 0)and (code not in posman.halt_codes):
        posman.halt_codes.append(code)
        pp.preprocess_all(all_stocks, stockdata.sh_index, log_status)

    (last, far) = util.get_hold_duration(stock)
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
                if stack <= 5:
                    stackstr = stackstr.replace(' ', '|', 1)
                elif stack <= 10:
                    stackstr = stackstr.replace('|', '+', 1)
                elif stack <= 15:
                    stackstr = stackstr.replace('+', '#', 1)
                else:
                    stackstr = stackstr.replace('#', '$', 1)


    index_profit_percent = 0
    buy_index = 0
    if position > 0:
        index_dh = tdal.previous_data_with_date(stockdata.sh_index['code'], stock['last_buy_date'], log_status)
        buy_index = (index_dh['high'] + index_dh['low']) / 2
        index_profit_percent = (stockdata.sh_index['price'] - buy_index) / buy_index
    index_profit_percentstr = '       '
    if index_profit_percent != 0:
        index_profit_percentstr = '%6.2f%%' % (index_profit_percent * 100)

    index_cost_percent = 0
    if stock.has_key('last_sell_date'):
        index_dh = tdal.previous_data_with_date(stockdata.sh_index['code'], stock['last_sell_date'], log_status)
        sell_index = (index_dh['high'] + index_dh['low']) / 2
        # 处理累进买入的情况
        if buy_index != 0 and sell_index > buy_index and stock['last_sell_date'] != stock['last_buy_date']:
            sell_index = buy_index
        index_cost_percent = (stockdata.sh_index['price'] - sell_index) / sell_index
    index_cost_percentstr = '       '
    if index_cost_percent < 0:
        index_cost_percentstr = '%6.2f%%' % (index_cost_percent * 100)

    stock['more_info_previousChange'] = previous_close - previous_open
    stock['more_info_todayChange'] = current_price - today_open
    stock['more_info_currentPrice'] = current_price
    stock['more_info_lastBuy'] = stock['last_buy']
    stock['more_info_lastSell'] = stock['last_sell']
    stock['more_info_position'] = stock['last_buy_position']#position
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
    log_status('Getting hist data for %s (%s)' % (code, theBeginDate))
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
        dh = tdal.previous_data_with_date(code, datestr, log_status)
        if dh is not None and dh['high'] > recent_high:
            recent_high = dh['high']
        theDate = theDate + timedelta(days=1)
        datestr = theDate.strftime('%Y-%m-%d')
    return recent_high

g_dark_enabled = 0

def display_stock(stock, line):
    global g_dark_enabled

    dark_enabled = (g_dark_enabled % 3 == 1 and stock['position'] > 0) or \
        (g_dark_enabled % 3 == 2 and stock['position'] == 0)
    default_colorpair = 6 if dark_enabled else 1

    comment = ''
    if stock.has_key('comment'):
        comment = stock['comment']
    if stock.has_key('margin'):
        comment = '[' + str(stock['margin'][0]) + ']' + comment
    comment += ' ' * (30 - len(comment))
    stock['more_info_comment'] = comment

    col = 1
    for i in range(len(columns.columns)):
        if options.g_arg_simplified and (columns.columns[i]['id'] in columns.s_columns) or \
                not options.g_arg_simplified:
            if columns.columns[i].has_key('value'):
                colorpair = default_colorpair
                if columns.columns[i].has_key('color'):
                    colorpair = columns.columns[i]['color'](stock, default_colorpair)
                screen.display_info(columns.columns[i]['value'](stock), col, line, colorpair)
            col += columns.columns[i]['width'] + 1  
    line += 1
    return line

def display_empty_line(line):  
    screen.display_info(' ' * 192, 0, line)
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

g_simplified_status = ''

# no-test
def log_status(message):
    # temp: use space to avoid messy chars.
    global g_simplified_status
    if options.g_arg_simplified:
        g_simplified_status = '' if len(g_simplified_status) > 8 else g_simplified_status + '.'
        screen.display_info(g_simplified_status, 1, 0)
        return
    screen.display_info('[%s]  %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message, ' ' * 30), 1, 0)

g_highlight_stock_index = 0
g_highlight_line = 5
g_show_all = False
g_hide_all = False
g_show_exceptX = False

# no-test
def parse_args():
    if len(sys.argv) >= 2 and sys.argv[1] == '-s':
        options.g_arg_simplified = True

DEBUG = False

def run_main():  
    global g_show_all
    global g_hide_all
    global g_dark_enabled
    global g_show_exceptX
    global g_highlight_stock_index
    global g_highlight_line
    global g_display_group_index
    global all_stocks
    global all_stocks_index
    #dbman.init()
    parse_args()
    if DEBUG:
        #try:  
            #set_win()
        #    preprocess_all()
        #    advice_all()
        #finally:
        #    pass
            #unset_win()  
        pass
    else:
        count = 0
        try:  
            screen.set_win()  
            pp.preprocess_all(all_stocks, stockdata.sh_index, log_status)
            hadvise.preprocess_all()
            while True:
                if count == 0 or dateutil2.is_trade_time(datetime.now()):
                    if g_hide_all:
                        screen.clear_win()
                    else:
                        advice_all()
                        if count == 0:
                            pp.preprocess_all(all_stocks, stockdata.sh_index, log_status)
                            advice_all()

                count += 1
                seconds = 0
                while seconds < 30:
                    seconds += 1
                    time.sleep(1)
                    ichar = screen.getch()
                    if ichar == ord('^'):
                        all_stocks_index = 2 if all_stocks_index == 1 else 1
                        if all_stocks_index == 1:
                            all_stocks = stockdata.all_stocks_1
                        else:
                            all_stocks = stockdata2.all_stocks_2
                        screen.clear_win()
                        pp.preprocess_all(all_stocks, stockdata.sh_index, log_status)
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
                        screen.clear_win()
                        advice_all()
                        seconds = 0
                    if ichar == ord('h'):
                        g_hide_all = not g_hide_all
                        #screen.clear_win()
                        seconds = 30
                        count = 0
                        break
                    if ichar == ord('x'):
                        g_show_all = not g_show_all
                        g_show_exceptX = not g_show_exceptX
                        advice_all()
                        seconds = 0
        finally:  
            screen.unset_win()
            pass

def profile_main():
    try:  
        screen.set_win()
        pp.preprocess_all(all_stocks, stockdata.sh_index, log_status)
        advice_all()
    finally:
        screen.unset_win()  

if __name__=='__main__':
    from autoreload import run_with_reloader
    run_with_reloader(run_main)

