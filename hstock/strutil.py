import unicodedata

def wide_chars(s):
    return sum(unicodedata.east_asian_width(x)=='W' or unicodedata.east_asian_width(x)=='A' \
        or unicodedata.east_asian_width(x)=='F' for x in s)
def width(s):
    return len(s) + wide_chars(s)

