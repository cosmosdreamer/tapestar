# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import kdj # own
import options # own
import posman # own
import screen # own
import tushare as ts

def display_overview(line, all_stocks, log):
    # Time 上证指数/涨跌/J 关注/持仓/停牌
    log('Getting sh index')
    df = ts.get_realtime_quotes(stockdata.sh_index['code'])
    log('Done sh index')

    stockdata.sh_index['price'] = today_price = float(df['price'][0])
    stockdata.sh_index['high'] = today_high = float(df['high'][0])
    stockdata.sh_index['low'] = today_low = float(df['low'][0])
    stockdata.sh_index['pre_close'] = pre_close = float(df['pre_close'][0])

    (k, d, j) = kdj.get_today_KDJ933(stockdata.sh_index, today_price, today_high, today_low)
    today_change_percent = (today_price - pre_close) / pre_close * 100
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    now = 'Time: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f  关注: %2d 持仓: %2d 停牌: %2d' \
        % (time_str, \
        today_price, today_change_percent, j, \
        len(all_stocks), posman.investments['positioned_stock_count'], len(posman.halt_codes))
    if options.g_arg_simplified:
        now = 'T: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f' \
        % (time_str, \
        today_price, today_change_percent, j)
    screen.display_info(now, 1, line)
    line += 1

    # workaround to color index J
    if not options.g_arg_simplified:
        indexJ = '%6.2f' % j
        indexJ_color = 1
        if j <= 20:
            indexJ_color = 2
        elif j >= 80:
            indexJ_color = 3
        screen.display_info(indexJ, 59, 1, indexJ_color)

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
    if not options.g_arg_simplified:
        screen.display_info(indexed_coststr, 1, line)
        line += 1
    return line

def display_cost(line):
    current_invest_base = (1 - (stockdata.sh_index['price'] / 500 - 2) * 0.1) * posman.investments['totalBase']
    invest_status = '仓/允: %6.0f/%6.0f, 除农: %6.0f, 除农比: %6.2f%%, 除停: %6.0f, 除停比: %6.2f%%, 大禾康占比: %6.2f%%' \
        % (posman.investments['total'], current_invest_base, posman.investments['totalExceptWhitelist'], \
        (posman.investments['totalExceptWhitelist'] - (current_invest_base - posman.investments['totalBase'] * const_baseOffsetPercent)) / (posman.investments['totalBase'] * const_baseOffsetPercent * 2) * 100, \
        posman.investments['totalExceptWhitelistAndHalt'], \
        (posman.investments['totalExceptWhitelistAndHalt'] - (current_invest_base - posman.investments['totalBase'] * const_baseOffsetPercent)) / (posman.investments['totalBase'] * const_baseOffsetPercent * 2) * 100, \
        posman.investments['totalVip'] / posman.investments['total'] * 100)
    if not g_arg_simplified:
        screen.display_info(invest_status, 1, line)
        line += 1
    return line
 
def display_fine_indexed_cost_dist(line):
    baseIndex = int(stockdata.sh_index['price']) / 100 * 100
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
        screen.display_info(indexed_coststr, 1, line)
        line += 1
    return line
