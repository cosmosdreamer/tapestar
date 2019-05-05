



import httplib
import json
#from dateutil import rrule
import lxml.html.soupparser as soupparser

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

    #if not g_show_all or (g_show_all and g_display_group_index == 0):
    #    line = display_stock_group(all_stocks, "卖出", line)
    #    line = display_empty_line(line)
    #    line = display_stock_group(all_stocks, "买入", line)
    #    line = display_empty_line(line)
    #    line = display_stock_group(all_stocks, "弱买", line)
    #    line = display_stock_group(all_stocks, "追高", line)
    #    line = display_empty_line(line)
    #    line = display_stock_group(all_stocks, "忖卖", line)
    #    line = display_stock_group(all_stocks, "弱卖", line)
    #    line = display_stock_group(all_stocks, "薄卖", line)
    #    line = display_stock_group(all_stocks, "亏卖", line)
    #if not g_show_all or (g_show_all and g_display_group_index == 1):
    #    line = display_empty_line(line)
    #    line = display_stock_group(all_stocks, "持有", line)
    #    line = display_empty_line(line)
    #    line = display_stock_group(all_stocks, "观望", line)
    #    line = display_stock_group(all_stocks, " -- ", line)
    #    if g_show_all or g_show_exceptX:
    #        line = display_stock_group(all_stocks, "HIDE", line)
    #        line = display_stock_group(all_stocks, "    ", line)

        #display_info('                          昨幅   今幅    现价   前买   前卖 仓位 盈利 回撤     J  久期 档位     指盈    指跌  转    浮盈   备注', 1, line)

    #log_status('(%d/%d) Getting realtime quotes for %s' % (index + 1, total, stock['code']))
    #df = ts.get_realtime_quotes(stock['code'])
    #log_status('(%d/%d) Done realtime quotes for %s' % (index + 1, total, stock['code']))

    #printstr = '(昨:%6.2f,今:%6.2f,现价:%6.2f,上次买:%6.2f卖:%6.2f,仓:%4d,盈:%s,回:%s,J:%6.2f,期:%s,栈:%s,点:%s)' \
    #    % (float(dh['close']) - float(dh['open']), \
    #    float(df['price'][0]) - float(df['open'][0]), \
    #    float(df['price'][0]), stock['last_buy'], \
    #    stock['last_sell'], position, profit_percentstr, regress_ratestr, j, \
    #    durationstr, stackstr, index_profit_percentstr)
    #stock['more_info'] = printstr

def display_stock_group(stocks, action, line):
    global stock_index
    for stock in stocks:
        if (stock['action'] == action):
            display_stock(stock, line)
            stock_index += 1
            screen.display_info(str(stock_index), 1, line)
            #stock2line[str(stock_index)] = line
            line += 1
        
    return line

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

    # code
    location = 1 + index_width
    if not g_arg_simplified:
        #display_info(stock['code'], location, line, colorpair)
        screen.display_info(columns.columns[1]['value'](stock), location, line, colorpair)
    
    # name
        location += code_width + separator
    screen.display_info(columns.columns[2]['value'](stock), location, line, colorpair)

    # action
    location += name_width + separator
    if not g_arg_simplified:
        screen.display_info(stock['action'], location, line, colorpair if dark_enabled else stock['action_color'])

    # more_info
        location += action_width + separator
        #display_info('(昨:%6.2f' % (stock['more_info_previousChange']), location, line, colorpair)
        screen.display_info('%6.2f' % (stock['more_info_previousChange']), location, line, colorpair)
        location += previousChange_width + separator
        #display_info('今:%6.2f' % (stock['more_info_todayChange']), location, line, colorpair)
        screen.display_info('%6.2f' % (stock['more_info_todayChange']), location, line, colorpair)
        location += todayChange_width + separator

    if g_arg_simplified:
        screen.display_info('%6.2f/%6.2f' % (stock['more_info_currentPrice'], stock['more_info_lastBuy']), location, line, colorpair)
        location += 13 + separator
    else:
        #display_info('现价:%6.2f' % (stock['more_info_currentPrice']), location, line, colorpair)
        screen.display_info('%6.2f' % (stock['more_info_currentPrice']), location, line, colorpair)
        location += currentPrice_width + separator
        #display_info('上次买:%6.2f' % (stock['more_info_lastBuy']), location, line, colorpair)
        screen.display_info('%6.2f' % (stock['more_info_lastBuy']), location, line, colorpair)
        location += lastBuy_width + separator

    if not g_arg_simplified:
        #display_info('卖:%6.2f' % (stock['more_info_lastSell']), location, line, colorpair)
        screen.display_info('%6.2f' % (stock['more_info_lastSell']), location, line, colorpair)
        location += lastSell_width + separator
        #display_info('仓:%4d' % (stock['more_info_position']), location, line, colorpair)
        screen.display_info('%4d' % (stock['more_info_position']), location, line, colorpair)
        location += position_width + separator
    currentProfit_color = 1
    duration = stock['more_info_duration_last'] if stock.has_key('more_info_duration_last') else 0
    if stock['more_info_profit_percent'] >= 7 + duration:
        currentProfit_color = 3
    elif stock['more_info_lastBuy'] == 0 and stock['more_info_profit_percentstr'] != '':
        currentProfit_color = 2
    #display_info('盈:%s' % (stock['more_info_profit_percentstr']), location, line, colorpair if dark_enabled else currentProfit_color)
    screen.display_info('%s' % (stock['more_info_profit_percentstr']), location, line, colorpair if dark_enabled else currentProfit_color)
    location += profit_width + separator
    regress_rate_color = 1
    #if (not stock.has_key('last100') and stock['more_info_regress_rate'] >= 28) \
    #    or stock.has_key('last100') and stock['last100'] and stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 58:
    if (stock['more_info_stack'] != 1 and stock['more_info_regress_rate'] >= 28) \
        or (stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 48):
        regress_rate_color = 3
    #display_info('回:%s' % (stock['more_info_regress_ratestr']), location, line, colorpair if dark_enabled else regress_rate_color)
    screen.display_info('%s' % (stock['more_info_regress_ratestr']), location, line, colorpair if dark_enabled else regress_rate_color)
    location += regression_width + separator
    currentJ_color = 1
    if stock['more_info_currentJ'] <= 20:
        currentJ_color = 2
    elif stock['more_info_currentJ'] >= 80:
        currentJ_color = 3
    #display_info('J:%6.2f' % (stock['more_info_currentJ']), location, line, colorpair if dark_enabled else currentJ_color)
    screen.display_info('%6.2f' % (stock['more_info_currentJ']), location, line, colorpair if dark_enabled else currentJ_color)
    location += j_width + separator
    if not g_arg_simplified:
        #display_info('期:%s' % (stock['more_info_durationstr']), location, line, colorpair)
        screen.display_info('%s' % (stock['more_info_durationstr']), location, line, colorpair)
        location += duration_width + separator
        #display_info('栈:%s' % (stock['more_info_stackstr']), location, line, colorpair)
        screen.display_info('%s' % (stock['more_info_stackstr']), location, line, colorpair)
        location += stack_width + separator
        index_profit_color = 1
        if stock['more_info_index_profit_percent'] * 100 >= 5:
            index_profit_color = 3
        #display_info('点:%s' % (stock['more_info_index_profit_percentstr']), location, line, colorpair if dark_enabled else index_profit_color)
        screen.display_info('%s' % (stock['more_info_index_profit_percentstr']), location, line, colorpair if dark_enabled else index_profit_color)
        location += indexProfit_width + separator
        index_cost_color = 1
        if stock['more_info_index_cost_percent'] * 100 <= -5 \
            and stock['more_info_index_profit_percent'] * 100 <= 0 \
            and stock['more_info_currentJ'] <= 20:
            index_cost_color = 2
        #display_info('进:%s' % (stock['more_info_index_cost_percentstr']), location, line, colorpair if dark_enabled else index_cost_color)
        screen.display_info('%s' % (stock['more_info_index_cost_percentstr']), location, line, colorpair if dark_enabled else index_cost_color)
        location += indexCost_width + separator
        #display_info('转:%3d' % stock['turnover'], location, line, colorpair)
        screen.display_info('%3d' % stock['turnover'], location, line, colorpair)
        location += turnover_width + separator
        #display_info('详:%7d' % stock['more_info_today_change'], location, line, colorpair)
        screen.display_info('%7d' % stock['more_info_today_change'], location, line, colorpair)
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
        screen.display_info(comment, location, line, colorpair if dark_enabled else comment_color)









































