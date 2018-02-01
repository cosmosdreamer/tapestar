from datetime import date, datetime, timedelta
import httplib
import json
import lxml.html.soupparser as soupparser
import tushare as ts

def get_copper_current():
    current = 0
    conn = httplib.HTTPConnection("www.cu168.com")
    conn.request("GET", "/data/lme.php")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        current = float(theData[10:17])
    conn.close()
    return current

def get_silver_current():
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

def get_euro_current():
    current = 0
    conn = httplib.HTTPConnection("www.icbc.com.cn")
    conn.request("GET", "/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        #print theData
        dom = soupparser.fromstring(theData)
        # no tbody for all tables. index starts from 1
        current_price = dom.xpath("//body/form/div/table/tr/td/table/tr[2]/td/table/tr[5]/td[4]")
        #print current_price
        if len(current_price) > 0:
            current_price = current_price[0].text.strip()
            current = float(current_price);
    conn.close()
    return current

def get_oil_current():
    return 240

def get_sh_current():
    df = ts.get_realtime_quotes('sh')
    return float(df['price'][0])

def get_sh_pe():
    pe = 0
    conn = httplib.HTTPConnection("www.csindex.com.cn")
    conn.request("GET", "/sseportal/ps/zhs/hqjt/csi/show_zsgz.js")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split('\n')[2]
        theData = theData[12:-2]
        #print theData
        pe = float(theData)
    conn.close()
    return pe

def get_hs_current():
    current = 0
    theDate = date.today()
    count = 0
    while current == 0 and count < 5:
        theDateStr = theDate.strftime('%d%b%y').lstrip('0')
        conn = httplib.HTTPConnection("www.hsi.com.hk")
        conn.request("GET", "/HSI-Net/static/revamp/contents/en/indexes/report/hsi/idx_" + theDateStr + ".csv")
        res = conn.getresponse()
        if res.status == 200:
            theData = res.read().split('\t')
            current = theData[(3 - 1) * 12 + 6 - 1]
            current = current.replace('"', '').replace('\0', '')
            current = float(current)
        conn.close()
        count += 1
        theDate = theDate - timedelta(days=1)
    return current

def get_hs_pe():
    pe = 0
    theDate = date.today()
    count = 0
    while pe == 0 and count < 5:
        theDateStr = theDate.strftime('%d%b%y').lstrip('0')
        conn = httplib.HTTPConnection("www.hsi.com.hk")
        conn.request("GET", "/HSI-Net/static/revamp/contents/en/indexes/report/hsi/idx_" + theDateStr + ".csv")
        res = conn.getresponse()
        if res.status == 200:
            theData = res.read().split('\t')
            pe = theData[(3 - 1) * 12 + 10 - 1]
            pe = pe.replace('"', '').replace('\0', '')
            pe = float(pe)
        conn.close()
        count += 1
        theDate = theDate - timedelta(days=1)
    return pe

def get_hl_current():
    pe = 0
    conn = httplib.HTTPConnection("www.csindex.com.cn")
    conn.request("GET", "/sseportal/ps/zhs/hqjt/csi/show_zsbx.js")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split('\n')[74]
        theData = theData[12:-2]
        #print theData
        pe = float(theData)
    conn.close()
    return pe

def get_hl_pe():
    pe = 0
    conn = httplib.HTTPConnection("www.csindex.com.cn")
    conn.request("GET", "/sseportal/ps/zhs/hqjt/csi/show_zsgz.js")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split('\n')[74]
        theData = theData[12:-2]
        #print theData
        pe = float(theData)
    conn.close()
    return pe

def get_sz162411_current():
    df = ts.get_realtime_quotes('162411')
    return float(df['price'][0])

def get_msft_current():
    current = 0
    conn = httplib.HTTPConnection("hq.sinajs.cn")
    conn.request("GET", "/list=gb_msft")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        current_price = theData[25:30]
        current = float(current_price)
    conn.close()
    return current

