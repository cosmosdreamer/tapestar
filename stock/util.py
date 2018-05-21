
from datetime import date, datetime, timedelta
import math

def compCurrentJ(stockX, stockY):
    if not stockX.has_key('more_info_currentJ') or not stockY.has_key('more_info_currentJ'):
        return 0

    if stockX['more_info_currentJ'] < stockY['more_info_currentJ']:
        return 1
    elif stockX['more_info_currentJ'] > stockY['more_info_currentJ']:
        return -1
    else:
        return 0

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
