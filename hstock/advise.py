# -*- coding: utf-8 -*-
import curses  
from dateutil import rrule
from datetime import date, datetime, timedelta
import hshare as hs
import hstockdata # own
import httplib
import json
import locale
from lxml import etree
import lxml.html.soupparser as soupparser
import math
import pymongo
import strutil # own
import sys  
import time

sys.path.insert(0, '../stock/')
sys.path.insert(0, 'tapestar/stock/')
# print sys.path

import shshare as ss # own

reload(sys)  
sys.setdefaultencoding('utf8')  

locale.setlocale(locale.LC_ALL, '')
system_code = locale.getpreferredencoding()

stdscr = None

client = pymongo.MongoClient()
db = client.hstock
c_dayK = db.dayK

positioned_stock_count = 0

def preprocess_all():
    global positioned_stock_count
    positioned_stock_count = 0
    for stock in hstockdata.all_stocks:
        preprocess_stock(stock)

def preprocess_stock(stock):
    global positioned_stock_count
    last_buy = 0.0
    last_buy_date = date.min
    far_buy_date = date.max
    last_sell = 0.0
    last_sell_date = date.min
    position = 0
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
            if direction == 1 and theDate < far_buy_date:
                far_buy_date = theDate
            if direction == 1:
                position += direction * amount
    if not stock.has_key('last_buy_date') and last_buy_date != date.min:
        stock['last_buy_date'] = last_buy_date.strftime('%Y-%m-%d')
    if not stock.has_key('far_buy_date') and far_buy_date != date.max:
        stock['far_buy_date'] = far_buy_date.strftime('%Y-%m-%d')
    if not stock.has_key('last_buy'):
        stock['last_buy'] = last_buy
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

stock_index = 0

def advice_all():
    global positioned_stock_count
    theTime = datetime.now()

    # line 1
    now = 'Time: %s  关注: %2d 持仓: %2d' \
        % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
        len(hstockdata.all_stocks), positioned_stock_count)
    display_info(now, 1, 1)
    
    line = 2

    for stock in hstockdata.all_stocks:
        advise(stock)

    global stock_index
    stock_index = 0
    line = display_stock_group(hstockdata.all_stocks, "卖出", line)
    line = display_empty_line(line)
    line = display_stock_group(hstockdata.all_stocks, "买入", line)
    line = display_empty_line(line)
    line = display_stock_group(hstockdata.all_stocks, "弱买", line)
    line = display_stock_group(hstockdata.all_stocks, "追高", line)
    line = display_empty_line(line)
    line = display_stock_group(hstockdata.all_stocks, "忖卖", line)
    line = display_stock_group(hstockdata.all_stocks, "弱卖", line)
    line = display_stock_group(hstockdata.all_stocks, "薄卖", line)
    line = display_stock_group(hstockdata.all_stocks, "亏卖", line)
    line = display_empty_line(line)
    line = display_stock_group(hstockdata.all_stocks, "持有", line)
    line = display_empty_line(line)
    line = display_stock_group(hstockdata.all_stocks, "观望", line)
    line = display_stock_group(hstockdata.all_stocks, " -- ", line)
    if g_show_all:
        line = display_stock_group(hstockdata.all_stocks, "HIDE", line)
        line = display_stock_group(hstockdata.all_stocks, "    ", line)

    line = display_empty_line(line)
    line = display_empty_line(line)
    line = display_empty_line(line)

    elapsed = datetime.now() - theTime
    display_info(' ' + str(elapsed), 0, line + 1)

def advise(stock):
    log_status('Getting realtime quotes for %s' % (stock['code']))
    if stock['code'].startswith('sh') or stock['code'].startswith('sz'):
        df = ss.get_realtime_quotes(stock['code'])
    else:
        df = hs.get_realtime_quotes(stock['code'])
    log_status('Done realtime quotes for %s' % (stock['code']))

    code = stock['code']
    datestr = datetime.now().strftime('%Y-%m-%d')
    dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
    dh = list(dh)
    if len(dh) == 0:
        c_dayK.insert({"code": stock["code"], "date": datestr, "close": df['close'], "open": df['open'], "high": df['high'], "low": df['low']})
    else:
        c_dayK.update({"code": stock["code"], "date": datestr}, {"$set": {"high": df['high']}})

    # name
    stock['name'] = df['name'].decode("GB2312")
    namelen = strutil.width(stock['name'])
    if namelen < 8:
        for i in range(8 - namelen):
            stock['name'] += ' ' # '_'
    if namelen > 8:
        stock['name'] = stock['name'][0:7]
    #print len(stock['name'])
    #print namelen

    action = ''
    action_color = 1
    
    current_price = df['price']
    today_high = df['high']
    today_open = df['open']
    position = stock['position']
    last_sell = stock['last_sell']
    last_buy = stock['last_buy']
    previous_close = df['previous_close']

    if not g_show_all and stock.has_key('margin'):
        if len(stock['margin']) > 1 and stock['margin'][0] < current_price and stock['margin'][1] > current_price \
            or len(stock["margin"]) == 1 and stock['margin'][0] < current_price and (position == 0 or current_price < stock["last_buy"] * 1.04):
            stock['action'] = "HIDE"
            return
    elif not g_show_all and current_price > stock["last_buy"] * 0.90 and current_price < stock["last_buy"] * 1.04:
        stock['action'] = "HIDE"
        return
    elif not g_show_all and position == 0 and stock["last_sell"] > 0 and current_price * 1.06 > stock["last_sell"]:
        stock['action'] = "HIDE"
        return

    if today_open == 0:
        action = "    "
    elif current_price - today_open > 0:
        strong_buy = whether_strong_buy(current_price, last_sell, last_buy)
        if strong_buy:
            action = "买入"
            action_color = 2
        else:
            action = "弱买"
            action_color = 4
    elif current_price - today_open < 0:
        if current_price < last_buy:
            action = "亏卖"
            action_color = 5
        elif current_price > last_buy + 1.00 and current_price < last_buy * 1.1:
            strong_sell = whether_strong_sell(current_price, last_sell, last_buy, today_high)
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
            strong_sell = whether_strong_sell(current_price, last_sell, last_buy, today_high)
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
        recent_high = get_recent_high(stock, float(today_high))
        regress_rate = math.ceil((recent_high - current_price) / (recent_high - last_buy) * 100)
        regress_ratestr = '%2d%%' % regress_rate
    
    (last, far) = get_hold_duration(stock)
    durationstr = '     '
    if position > 0:
        durationstr = '%2d/%2d' %(last, far)

    stackstr = '     '
    if stock.has_key('trades'):
        for trade in stock['trades']:
            direction = trade[1]
            if direction == 1:
                stackstr = stackstr.replace(' ', '|', 1)

    stock['more_info_todayChange'] = current_price - today_open
    stock['more_info_currentPrice'] = current_price
    stock['more_info_lastBuy'] = stock['last_buy']
    stock['more_info_lastSell'] = stock['last_sell']
    stock['more_info_position'] = position
    stock['more_info_profit_percent'] = profit_percent
    stock['more_info_profit_percentstr'] = profit_percentstr
    stock['more_info_regress_rate'] = regress_rate
    stock['more_info_regress_ratestr'] = regress_ratestr
    stock['more_info_duration_last'] = last
    stock['more_info_duration_far'] = far
    stock['more_info_durationstr'] = durationstr
    stock['more_info_stackstr'] = stackstr

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

def whether_strong_sell(current_price, last_sell, last_buy, today_high):
    recent_high = today_high
    strong_sell = recent_high > last_buy * 1.2 and (recent_high - current_price) > (recent_high - last_buy) * 0.2
    return strong_sell

def get_recent_high(stock, today_high):
    recent_high = 0

    if stock.has_key('last_buy_date'):
        recent_high = get_recent_high_from_date(stock['code'], stock['last_buy_date'])
        if recent_high == 0:
            recent_high = today_high

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

def previous_data_with_date(code, datestr):
    originDateStr = datestr
    dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
    dh = list(dh)
    
    if len(dh) == 0:
        return None

    return dh[0]

def display_stock_group(stocks, action, line):
    global stock_index
    for stock in stocks:
        if (stock['action'] == action):
            display_stock(stock, line)
            stock_index += 1
            display_info(str(stock_index), 1, line)
            #stock2line[str(stock_index)] = line
            line += 1
        
    return line

#g_dark_enabled = 0

def display_stock(stock, line):
    #global g_dark_enabled

    separator = 1
    index_width = 3
    code_width = 6
    name_width = 8
    action_width = 4
    #previousChange_width = 10
    todayChange_width = 9
    currentPrice_width = 11
    lastBuy_width = 13
    lastSell_width = 9
    position_width = 7
    profit_width = 7
    regression_width = 6
    #j_width = 8
    duration_width = 8
    stack_width = 8
    #indexProfit_width = 10
    #indexCost_width = 10
    turnover_width = 6

    #dark_enabled = (g_dark_enabled % 3 == 1 and stock['position'] > 0) or \
    #    (g_dark_enabled % 3 == 2 and stock['position'] == 0)
    #colorpair = 6 if dark_enabled else 1
    colorpair = 1

    # code
    location = 1 + index_width
    display_info(stock['code'].replace('hh', ''), location, line, colorpair)
    
    # name
    location += code_width + separator
    display_info(stock['name'], location, line, colorpair)

    # action
    location += name_width + separator
    display_info(stock['action'], location, line, stock['action_color'])

    # more_info
    location += action_width + separator
    display_info('今:%6.2f' % (stock['more_info_todayChange']), location, line, colorpair)
    location += todayChange_width + separator

    display_info('现价:%6.2f' % (stock['more_info_currentPrice']), location, line, colorpair)
    location += currentPrice_width + separator
    display_info('上次买:%6.2f' % (stock['more_info_lastBuy']), location, line, colorpair)
    location += lastBuy_width + separator

    display_info('卖:%6.2f' % (stock['more_info_lastSell']), location, line, colorpair)
    location += lastSell_width + separator
    display_info('仓:%4d' % (stock['more_info_position']), location, line, colorpair)
    location += position_width + separator
    currentProfit_color = 1
    duration = stock['more_info_duration_last'] if stock.has_key('more_info_duration_last') else 0
    if stock['more_info_profit_percent'] >= 7 + duration:
        currentProfit_color = 3
    display_info('盈:%s' % (stock['more_info_profit_percentstr']), location, line, currentProfit_color)
    location += profit_width + separator
    regress_rate_color = 1
    if stock['more_info_regress_rate'] >= 28:
        regress_rate_color = 3
    display_info('回:%s' % (stock['more_info_regress_ratestr']), location, line, regress_rate_color)
    location += regression_width + separator
    display_info('期:%s' % (stock['more_info_durationstr']), location, line, colorpair)
    location += duration_width + separator
    display_info('栈:%s' % (stock['more_info_stackstr']), location, line, colorpair)
    location += stack_width + separator
    display_info('转:%3d' % stock['turnover'], location, line, colorpair)
    location += turnover_width + separator
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
    display_info(comment, location, line, comment_color)

def display_empty_line(line):  
    display_info(' ' * 185, 0, line)
    line += 1
    return line

def log_status(message):
    # temp: use space to avoid messy chars.
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

def is_trade_time():
    theTime = datetime.now()
    return (theTime.hour == 9 and theTime.minute >= 15) or \
        (theTime.hour == 10) or (theTime.hour == 11) or (theTime.hour == 12 and theTime.minute <= 3) or \
        (theTime.hour >= 13 and theTime.hour < 16) or \
        (theTime.hour == 16 and theTime.minute <= 3)

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

g_show_all = False

if __name__=='__main__':  
    if True:
        stdscr = curses.initscr()
        count = 0
        try:  
            set_win()  
            preprocess_all()
            while True:
                if count == 0 or is_trade_time():
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
        finally:  
            unset_win()
            pass

