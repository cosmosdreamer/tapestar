
#import pymongo
#from pymongo import MongoClient

#stock_codes = ['002450', '601766', '601288', '000488', '002008', '600522', '002164', '600008']
#eyeon_stock_codes = ['002290', '600029', '002570', '000898']

#precious_metals = [
#    {
#        'code': 1,
#        'name': '白银',
#        'trades': [
#            ['2015-12-14', 1, 3000, 2.87],
#        ],
#    }
#]

#datetime.strptime(trade[0], '%Y-%m-%d').date()
#datetime.strptime(trade[4], '%Y-%m-%d').date()

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
    screen.display_info(str, location, index, color)
    location = index_width
    screen.display_info(str, location, index, color)
    location += code_width + separator
    screen.display_info(str, location, index, color)
    location += name_width + separator
    screen.display_info(str, location, index, color)
    location += action_width + separator
    screen.display_info(str, location, index, color)
    location += previousChange_width + separator
    screen.display_info(str, location, index, color)
    location += todayChange_width + separator
    screen.display_info(str, location, index, color)
    location += currentPrice_width + separator
    screen.display_info(str, location, index, color)
    location += lastBuy_width + separator
    screen.display_info(str, location, index, color)
    location += lastSell_width + separator
    screen.display_info(str, location, index, color)
    location += position_width + separator
    screen.display_info(str, location, index, color)
    location += profit_width + separator
    screen.display_info(str, location, index, color)
    location += regression_width + separator
    screen.display_info(str, location, index, color)
    location += j_width + separator
    screen.display_info(str, location, index, color)
    location += duration_width + separator
    screen.display_info(str, location, index, color)
    location += stack_width + separator
    screen.display_info(str, location, index, color)
    location += indexProfit_width + separator
    screen.display_info(str, location, index, color)
    location += indexCost_width + separator
    screen.display_info(str, location, index, color)

                    #stock_count = len(stock2line)
                    #if ichar == ord('-') or ichar == screen.KEY_UP or ichar == screen.KEY_LEFT or ichar == ord('w'):
                    #    display_highlight_info(g_highlight_line, False)
                    #    g_highlight_stock_index = g_highlight_stock_index - 1
                    #    if g_highlight_stock_index <= 0: g_highlight_stock_index = stock_count
                    #    g_highlight_line = stock2line[str(g_highlight_stock_index)]
                    #    display_highlight_info(g_highlight_line, True)
                    #elif ichar == ord('+') or ichar == screen.KEY_DOWN or ichar == screen.KEY_RIGHT or ichar == ord('s'):
                    #    display_highlight_info(g_highlight_line, False)
                    #    g_highlight_stock_index = g_highlight_stock_index + 1
                    #    if g_highlight_stock_index > stock_count: g_highlight_stock_index = 1
                    #    g_highlight_line = stock2line[str(g_highlight_stock_index)]
                    #    display_highlight_info(g_highlight_line, True)
                    #elif ichar >= ord('0') and ichar <= ord('9'):
                    #    display_highlight_info(g_highlight_line, False)
                    #    g_highlight_stock_index = g_highlight_stock_index * 10 + ichar - ord('0')
                    #    if g_highlight_stock_index >= stock_count:
                    #        g_highlight_stock_index = ichar - ord('0')
                    #    if g_highlight_stock_index >= stock_count:
                    #        g_highlight_stock_index = 1
                    #    if g_highlight_stock_index <= 0: g_highlight_stock_index = stock_count
                    #    g_highlight_line = stock2line[str(g_highlight_stock_index)]
                    #    display_highlight_info(g_highlight_line, True)

                #if count % 10 == 1:
                #    update_metal()
                #time.sleep(60)
        #except Exception,e:  
        #    unset_win()  
        #    raise e  




























