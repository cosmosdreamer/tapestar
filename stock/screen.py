# -*- coding: utf-8 -*-
import sys

import curses

DEBUG_SCREEN = True

KEY_UP = curses.KEY_UP
KEY_DOWN = curses.KEY_DOWN
KEY_LEFT = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT

stdscr = None

# no-test
def display_info(str, x, y, colorpair=1):
    if DEBUG_SCREEN:
        print str
        return

    '''''使用指定的colorpair显示文字'''  
    try:  
        global stdscr
        stdscr.addstr(y, x, str, curses.color_pair(colorpair))  
        stdscr.refresh()  
    except Exception,e:  
        pass  

# no-test
def set_win():
    if DEBUG_SCREEN:
        return

    '''''控制台设置'''  
    global stdscr  
    stdscr = curses.initscr()

    #使用颜色首先需要调用这个方法  
    curses.start_color()  
    #文字和背景色设置，设置了两个color pair，分别为1和2  
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)  
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLACK)  
    #关闭屏幕回显  
    curses.noecho()  
    #输入时不需要回车确认  
    curses.cbreak()  
    #设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒  
    stdscr.nodelay(1)  

def clear_win():
    global stdscr  
    stdscr.clear()

# no-test
def unset_win():  
    if DEBUG_SCREEN:
        return

    '''''控制台重置'''  
    global stdscr  
    #恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）  
    curses.nocbreak()  
    curses.echo()  
    #结束窗口  
    curses.endwin()  

# no-test
def getch():
    if DEBUG_SCREEN:
        return

    global stdscr
    ichar = stdscr.getch()
    if ichar == 27 and stdscr.getch() == ord('['):
        ichar = stdscr.getch()
        if ichar == ord('A'):
            ichar = curses.KEY_UP
        elif ichar == ord('B'):
            ichar = curses.KEY_DOWN
        elif ichar == ord('C'):
            ichar = curses.KEY_RIGHT
        elif ichar == ord('D'):
            ichar = curses.KEY_LEFT
    return ichar

