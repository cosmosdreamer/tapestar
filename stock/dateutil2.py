# -*- coding: utf-8 -*-
from datetime import date, datetime

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
    if date.year < 2015 or date.year > 2018:
        raise Exception('year not supported!')
    return True

def parse_date(datestr):
    return datetime.strptime(dateStr, '%Y-%m-%d').date()

def format_date(date):
    return date.strftime('%Y-%m-%d')

def previous_date(date):
    return date - timedelta(days=1)


