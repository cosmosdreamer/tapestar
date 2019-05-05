# -*- coding: utf-8 -*-

import math

stock_action_weight = {
    '卖出': 65,
    '买入': 60,
    '弱买': 55,
    '追高': 50,
    '忖卖': 45,
    '弱卖': 40,
    '薄卖': 35,
    '亏卖': 30,
    '持有': 25,
    '观望': 20,
    ' -- ': 15,
    'HIDE': 10,
    '    ': 5,
    'XXXX': 0,
}

def compAction(stockX, stockY):
    return stock_action_weight[stockX['action']] - stock_action_weight[stockY['action']]

def compCurrentJ(stockX, stockY):
    if not stockX.has_key('more_info_currentJ') or not stockY.has_key('more_info_currentJ'):
        return 0

    if stockX['more_info_currentJ'] < stockY['more_info_currentJ']:
        return 1
    elif stockX['more_info_currentJ'] > stockY['more_info_currentJ']:
        return -1
    else:
        return 0

def compProfit(stockX, stockY):
    profitX = math.ceil(stockX['more_info_profit_percent'] if stockX.has_key('more_info_profit_percent') else 0.0)
    profitY = math.ceil(stockY['more_info_profit_percent'] if stockY.has_key('more_info_profit_percent') else 0.0)
    return int(profitX - profitY)
