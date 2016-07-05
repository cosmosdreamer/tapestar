import httplib

def get_realtime_quotes(code):
    if code.startswith('hh'):
        code = code.replace('hh', 'hk')
    quotes = {}
    conn = httplib.HTTPConnection("hq.sinajs.cn")
    conn.request("GET", "/list=" + code)
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split(',')
        #print theData
        quotes = {
            'name': theData[1],
            'price': float(theData[6]),
            'high': float(theData[4]),
            'open': float(theData[2]),
            'low': float(theData[5]),
            'close': float(theData[6]),
            'previous_close': float(theData[3]),
        }
    conn.close()
    return quotes

if __name__=='__main__':  
    df = get_realtime_quotes('hh00700')
    print df
