# Overview

Basic SQLite database curses viewer and editor.
* `q` to quit
* `w` to switch to table selector
* `e` to switch to column selector
* `r` to switch to row selector
Use the arrow keys to navigate.

While selecting columns, the space key may be used to select/deselect columns to be filtered for, pressing the enter key will query for with those filters.

While selecting rows, `i` can be used to insert new entries, `u` to update the selected entry, and `d` to delete the selected entry.

I created this software to better my understandning of SQL APIs as well as curses.

[Software Demo Video](http://youtube.com)

# Relational Database

SQLite3 was used as the test database

A sample database that was used for testing can be found in this repo.

# Development Environment

Editor: Vim

Languages and libaries: Python, SQLite3, and curses

# Useful Websites

* [Python SQLite Docs](https://docs.python.org/3/library/sqlite3.html)
* [Python Curses Docs](https://docs.python.org/3/howto/curses.html)

# Future Work

* More robust interface
* Support for complex queries
* Other features