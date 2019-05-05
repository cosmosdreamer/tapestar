# -*- coding: utf-8 -*-

# position manager

import sys
import const # own

whitelist_codes = ['601288', '000725', '603203'] # 农业银行, 京东方A, 快客股份
halt_codes = [] # real-time retrieve
vip_codes = ['002008', '002290', '002450'] # 大禾康

investments = {
    'totalBase': const.const_totalBase,
    'total': 0,
    'totalExceptWhitelist': 0,
    'totalExceptWhitelistAndHalt': 0,
    'totalVip': 0,
    'indexed_cost': [],
    'fine_indexed_cost': [],
    'indexedTotal': 0,
    'positioned_stock_count': 0,
}

def reset():
    investments['total'] = 0
    investments['totalExceptWhitelist'] = 0
    investments['totalExceptWhitelistAndHalt'] = 0
    investments['totalVip'] = 0
    investments['indexed_cost'] = [0, 0, 0, 0, 0, 0, 0, 0]
    investments['fine_indexed_cost'] = [0, 0, 0, 0, 0, 0, 0, 0]
    investments['indexedTotal'] = 0
    investments['positioned_stock_count'] = 0




