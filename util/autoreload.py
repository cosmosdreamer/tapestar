#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module is used to test how to reload the modules automatically when any
changes is detected.
"""
#__author__="Wenjun Xiao"
 
import os,sys,time,subprocess,thread
import signal

_sub_proc = None

def iter_module_files():
    for module in sys.modules.values():
        filename = getattr(module, '__file__', None)
        if filename:
            if filename[-4:] in ('.pyo', '.pyc'):
                filename = filename[:-1]
            yield filename
 
def is_any_file_changed(mtimes):
    for filename in iter_module_files():
        try:
            mtime = os.stat(filename).st_mtime
        except IOError:
            continue
        old_time = mtimes.get(filename, None)
        if old_time is None:
            mtimes[filename] = mtime
        elif mtime > old_time:
            return 1
    return 0
 
def start_change_detector():
    mtimes = {}
    while 1:
        if is_any_file_changed(mtimes):
            sys.exit(3)
        time.sleep(1)

def signal_handler(*args):
    global _sub_proc
    if _sub_proc:
        print "[%s]Stop subprocess:%s" % (os.getpid(), _sub_proc.pid)
        _sub_proc.terminate()
    sys.exit(0)

def restart_with_reloader():
    signal.signal(signal.SIGTERM, signal_handler)
    while 1:
        #print "restart with reloader[%s][%s]" % (sys.executable, sys.argv)
        args = [sys.executable] + sys.argv
        new_env = os.environ.copy()
        new_env['RUN_FLAG'] = 'true'
        global _sub_proc
        _sub_proc = subprocess.Popen(args, env=new_env)#, stdout=subprocess.PIPE,
        #    stderr=subprocess.STDOUT)
        #read_stdout(_sub_proc.stdout)
        exit_code = _sub_proc.wait()
        if exit_code != 3:
            return exit_code

def read_stdout(stdout):
    while 1:
        data = os.read(stdout.fileno(), 2**15)
        print "read stdout"
        if len(data) > 0:
            sys.stdout.write(data)
        else:
            stdout.close()
            sys.stdout.flush()
            break

def run_with_reloader(runner):
    if os.environ.get('RUN_FLAG') == 'true':
        thread.start_new_thread(runner, ())
        try:
            start_change_detector()
        except KeyboardInterrupt:
            import curses
            curses.nocbreak()  
            curses.echo()  
            curses.endwin()  
            pass
    else:
        try:
            sys.exit(restart_with_reloader())
        except KeyboardInterrupt:
            import curses
            curses.nocbreak()  
            curses.echo()  
            curses.endwin()  
            pass

