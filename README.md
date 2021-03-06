# nowapi
nosql webapp injection testing tool

Uses [$regex] to search for usernames and/or passwords in misconfigured nosql webapps.  It fires up the search in parallel a thread/process for each slot (up to max length) in the item being searched.  It runs through python's non-multibyte printable characters and skips a few others like `tab, newline, and carriage return`

It can be run with or without curses, with curses it does a simple animation of the username/password discovery.
If you are giving it an exact username make sure that username max length is set to it's length.  Otherwise the program will treat it as a partial username and do a search on it.

## Usage
```
usage: nowapi.py [-h] [-i] [-u USERNAME] [--ul UL] [--pl PL] [--params [PARAMS [PARAMS ...]]] [--no-curses] url

iterates usernames and/or passwords for nosql webapps that are injectable

positional arguments:
  url                   base url to use for the query

optional arguments:
  -h, --help            show this help message and exit
  -i, --iterate         attempt to find all usernames
  -u USERNAME, --username USERNAME
                        specify username or partial username
  --ul UL               username max length [20]
  --pl PL               password max length [20]
  --params [PARAMS [PARAMS ...]]
                        specify any other params needed [['login=login']]
  --no-curses

This program can be used to find usernames and passwords associated with an injectable webapp login.
It uses a POST of username/password payload, default form is a body of login=login&username=<username>&password=<password>,
params can be used to change everything except username and password parameters. that'll probably change in the future.

example: ./nowapi.py -u m http://server.example.com/login.htm

would search for any users starting with the letter 'm'
```
## Todo
[] add support for json payloads

[] add support for different username/password params

[] importing of Burpsuite captures

## Inspiration
This code was originally developed to help find passwords on [hackthebox.eu](https://www.hackthebox.eu/) mango server (retired).  It was initially based on code found in [PayloadsAllTheThings-NoSQL-Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/NoSQL%20Injection)

Then feature creep took over and it became a parallel injection finding program for both username and password with a bit of fun with curses thrown in.  With more feature creep to come in the future, `hopefully`.


## Notes
Username iteration is kind of slow, you can limit the number of letters in the username to look for with the --ul.

example:
```
./nowapi.py --ul 2 --iterate http://server.example.com/
```
would search for just the first two letters of any usernames

