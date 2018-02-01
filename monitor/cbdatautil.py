from datetime import date, datetime, timedelta
import httplib
import json
import lxml.html.soupparser as soupparser
import tushare as ts

def get_cb_current():
    current = 0
    conn = httplib.HTTPConnection("www.icbc.com.cn")
    conn.request("GET", "/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        #print theData
        dom = soupparser.fromstring(theData)
        # no tbody for first table. index starts from 1
        current_price = dom.xpath("//body/form/table/tr/td/table[6]/tbody/tr/td/div/table/tbody/tr[3]/td[4]")
        if len(current_price) > 0:
            current_price = current_price[0].text.strip()
            current = float(current_price);
    conn.close()
    return current
