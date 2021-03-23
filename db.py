import sys
import sqlite3
import curses

# window indexes
SCR = 0
DB = 1
TAB = 2

# Gap space between columns
GAP = 4

"""
Model of the state of the application
The state determines how input should be processed depending on st
"""
class State:
    def __init__(self):
        self.st = "DATABASE"
        self.cur_x = 0
        self.cur_y = 0
        self.db_cur_y = 1
        self.tables = None
        self.table_sel = None
        self.columns = []
        self.query = None
        self.filters = []

        self.cursor = None
        self.connection = None
        self.tab_win = None
        self.keys = []

    def handle_input(self, c):
        # mode changes
        if c == ord('q'):
            return False
        elif c == ord('w'):
            self.st = "DATABASE"
            self.cur_x = 0
            self.cur_y = 0
        elif c == ord('e'):
            self.st = "COL"
            self.cur_x = 1
            self.cur_y = 0
        elif c == ord('r'):
            self.st = "ROW"
            self.cur_x = 0
            self.cur_y = 1

        # keys pressed for each mode
        elif self.st == "DATABASE":
            if c == curses.KEY_UP:
                if self.db_cur_y - 1 > 0:
                    self.db_cur_y -= 1
            elif c == curses.KEY_DOWN:
                if self.db_cur_y < len(self.tables):
                    self.db_cur_y += 1
            self.table_sel = self.tables[self.db_cur_y - 1][0]
        elif self.st == "COL":
            self.query = query_default
            if c == curses.KEY_LEFT:
                self.cur_x -= 1
            elif c == curses.KEY_RIGHT:
                self.cur_x += 1
            elif c == ord(' '):
                self.add_to_filter()
            elif c == 13 and len(self.filters) > 0: # 13 is \r
                self.query = query_filter
        elif self.st == "ROW":
            if c == curses.KEY_UP:
                self.cur_y -= 1
            elif c == curses.KEY_DOWN:
                self.cur_y += 1
            elif c == ord('i'):
                query_insert(self.cursor, self.connection, self.table_sel, get_input(self.tab_win, self.columns[self.db_cur_y - 1], 2))
            elif c == ord('u'):
                query_update(self.cursor, self.connection, self.table_sel, self.keys[self.db_cur_y - 1][self.cur_y - 1][0], self.columns[self.db_cur_y - 1], get_input(self.tab_win, self.columns[self.db_cur_y - 1], self.cur_y + 1))
            elif c == ord('d'):
                query_delete(self.cursor, self.connection, self.table_sel, self.columns[self.db_cur_y - 1][0], self.keys[self.db_cur_y - 1][self.cur_y - 1][0])

        return True

    def add_to_filter(self):
        if self.cur_x in self.filters:
            self.filters.remove(self.cur_x)
        else:
            self.filters.append(self.cur_x)


"""
Start curses along with the curses windows that will be returned
"""
def start_curses():
    scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    scr.keypad(True)
    curses.curs_set(0)

    h, w = scr.getmaxyx()
    db_win = curses.newwin(h, int(w * 0.2), 0, 0)
    table_win = curses.newwin(h, int(w * 0.8), 0, int(w * 0.2))

    return [scr, db_win, table_win]

def stop_curses(scr):
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()
    curses.endwin()

"""
Draw the list of the tables from the database file
"""
def draw_db(win, tables, cur):
    win.border(0)
    win.addstr(0, 0, "Database")
    for i in range(len(tables)):
        if i + 1 == cur:
            win.addstr(i + 1, 1, tables[i][0][:22], curses.A_STANDOUT)
        else:
            win.addstr(i + 1, 1, tables[i][0][:22])

"""
Draw the columns along with the rows from the selected table
"""
def draw_table(win, col, rows, cur_x, cur_y, filters):
    win.move(1, 1)
    win.clear()
    win.border(0)
    win.addstr(0, 1, "Columns")
    last = [1]
    for i in range(len(col)):
        if i + 1 == cur_x or i + 1 in filters:
            win.addstr(1, last[i], col[i], curses.A_STANDOUT)
        else:
            win.addstr(1, last[i], col[i])
        last.append(last[i] + len(col[i]) + GAP)
        #if last + len(col[i + 1]) >= MAX_LENGTH:
            #break
    for i in range(len(rows)):
        for j in range(len(rows[i])):
            if i + 1 == cur_y:
                win.addstr(i + 2, last[j], str(rows[i][j]), curses.A_STANDOUT)
            else:
                win.addstr(i + 2, last[j], str(rows[i][j]))

"""
Query functions
"""
def query_default(cursor, table, _):
    cursor.execute("SELECT * FROM {};".format(table))
    return cursor.fetchall()

def query_filter(cursor, table, cols):
    cursor.execute("SELECT {} FROM {};".format(", ".join(cols), table))
    return cursor.fetchall()

def query_insert(cursor, connection, table, data):
    for i in data:
        try:
            i = int(i)
        except ValueError:
            pass
    cursor.execute("INSERT INTO {} VALUES ({});"
            .format(table, ", ".join(len(data) * '?')), data)
    connection.commit()

def query_update(cursor, connection, table, key, cols, data):
    for i in data:
        try:
            i = int(i)
        except ValueError:
            pass
    if len(data) != len(cols): # error
        return
    q_str = "UPDATE {} SET ".format(table)
    for i in range(len(cols)):
        q_str += "{} = ?, ".format(cols[i])
    q_str = q_str[:-2] # trim the last comma off
    q_str += " WHERE {} = {};".format(cols[0], key)
    cursor.execute(q_str, data)
    connection.commit()

def query_delete(cursor, connection, table, key_col, key):
    cursor.execute("DELETE FROM {} WHERE {} = {}".format(table, key_col, key))
    connection.commit()

"""
Used for insert and update, gathers data from the user for those queries
"""
def get_input(win, col, r):
    win.move(r, 1)
    win.clrtoeol()
    win.border(0)
    win.addstr(0, 1, "Columns")
    last = 1
    input = []
    curses.echo()
    for i in range(len(col)):
        input.append(win.getstr(r, last, len(col[i]) + GAP - 1))
        last += len(col[i]) + GAP
    curses.noecho()
    ret = []
    for i in input:
        ret.append(i.decode())
    
    return ret

"""
Helper function to query_filter
"""
def index_col(nums, cols):
    return [cols[x - 1] for x in nums]

"""
Gathers all keys from a table
"""
def get_keys(cursor, table, key_col):
    cursor.execute("SELECT {} FROM {};".format(key_col, table))
    return cursor.fetchall()

def main():
    if len(sys.argv) != 2:
        print("Usage: python db.py <database file>")
        exit()

    # start the connection and the state
    connection = sqlite3.connect(sys.argv[1])
    cursor = connection.cursor()
    state = State()
    state.query = query_default

    # get the tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    state.tables = cursor.fetchall()
    state.table_sel = state.tables[0][0]

    state.cursor = cursor
    state.connection = connection

    # get the column names
    for i in state.tables:
        cursor.execute("PRAGMA table_info({})".format(i[0]))
        col = cursor.fetchall()
        state.columns.append([i[1] for i in col])
    # get the keys
    for i in range(len(state.tables)):
        state.keys.append(get_keys(cursor, state.tables[i][0], state.columns[i][0])) # assumes key is in the first col

    scr = start_curses()
    state.tab_win = scr[TAB]

    # first draw
    draw_db(scr[DB], state.tables, state.db_cur_y)
    draw_table(scr[TAB], state.columns[state.db_cur_y - 1], state.query(cursor, state.table_sel, state.filters), state.cur_x, state.cur_y, state.filters)
    for i in scr:
        i.refresh()

    # main loop, processes input and draws
    while state.handle_input(scr[SCR].getch()):
        draw_db(scr[DB], state.tables, state.db_cur_y)
        draw_table(scr[TAB], state.columns[state.db_cur_y - 1], state.query(cursor, state.table_sel, index_col(state.filters, state.columns[state.db_cur_y - 1])), state.cur_x, state.cur_y, state.filters)
        for i in scr:
            i.refresh()

    stop_curses(scr[0])

if __name__ == "__main__":
    main()
