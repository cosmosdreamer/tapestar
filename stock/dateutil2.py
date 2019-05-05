# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import legalholidays # own

def is_today_trade_date():
    return is_trade_date(date.today())

# tested
def is_trade_date(date):
    if date.weekday() == 5 or date.weekday() == 6:
        return False # Saturday or Sunday
    datestr = date.strftime('%Y-%m-%d')
    #print datestr
    if datestr in legalholidays.legal_holidays:
        #print 'False'
        return False
    if date.year < 2015 or date.year > 2019:
        raise Exception('year not supported!')
    return True

# tested
def is_trade_time(theTime):
    const_tradeTimeOffset = 3
    return (theTime.hour == 9 and theTime.minute >= 30 - const_tradeTimeOffset) or \
        (theTime.hour == 10) or (theTime.hour == 11 and theTime.minute <= 30 + const_tradeTimeOffset) or \
        (theTime.hour == 12 and theTime.minute >= 60 - const_tradeTimeOffset) or \
        (theTime.hour >= 13 and theTime.hour < 15) or \
        (theTime.hour == 15 and theTime.minute <= const_tradeTimeOffset)

def parse_date(dateStr):
    return datetime.strptime(dateStr, '%Y-%m-%d').date()

def format_date(date):
    return date.strftime('%Y-%m-%d')

def previous_date(date):
    return date - timedelta(days=1)


