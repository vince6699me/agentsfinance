---
source: Official Docs (docs.python.org)
library: SQLite with Python
package: sqlite3
topic: database connection, async support, patterns
fetched: 2026-04-29
official_docs: https://docs.python.org/3/library/sqlite3.html
---

# SQLite3 Documentation

## Overview

The `sqlite3` module provides an SQL interface compliant with the DB-API 2.0 specification (PEP 249). SQLite is a C library that provides a lightweight disk-based database that doesn't require a separate server process.

## Tutorial - Basic Patterns

### Creating a Database Connection

```python
import sqlite3

# Create or open database
con = sqlite3.connect("tutorial.db")

# Create in-memory database
con = sqlite3.connect(":memory:")
```

### Creating a Cursor

```python
cur = con.cursor()
```

### Creating a Table

```python
cur.execute("CREATE TABLE movie(title, year, score)")
```

Note: Thanks to SQLite's flexible typing, specifying data types is optional.

### Inserting Data

```python
# Single insert
cur.execute("""
    INSERT INTO movie VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)
""")

# Multiple inserts using executemany
data = [
    ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
    ("Monty Python's The Meaning of Life", 1983, 7.5),
    ("Monty Python's Life of Brian", 1979, 8.0),
]
cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)

# Commit the transaction
con.commit()
```

### Querying Data

```python
# Fetch all results
res = cur.execute("SELECT title, year FROM movie ORDER BY year")
rows = res.fetchall()
for row in rows:
    print(row)

# Fetch one result
row = res.fetchone()

# Iterate over results
for row in cur.execute("SELECT year, title FROM movie ORDER BY year"):
    print(row)
```

### Using Placeholders (Important!)

**Always use placeholders instead of string formatting to prevent SQL injection:**

```python
# Correct - using placeholders
cur.execute("INSERT INTO movie VALUES(?, ?, ?)", (title, year, score))

# Wrong - vulnerable to SQL injection
# cur.execute(f"INSERT INTO movie VALUES('{title}', '{year}', '{score}')")
```

## Connection Objects

### sqlite3.connect() Parameters

```python
sqlite3.connect(
    database,              # Path to database file or ":memory:"
    timeout=5.0,           # Seconds to wait before raising OperationalError
    detect_types=0,        # Type detection (PARSE_DECLTYPES | PARSE_COLNAMES)
    isolation_level=None,  # Transaction control (DEFERRED, EXCLUSIVE, IMMEDIATE)
    check_same_thread=True,# Thread safety
    factory=Connection,    # Custom Connection subclass
    cached_statements=128, # Statement cache size
    uri=False,             # Interpret as URI
    autocommit=False       # Autocommit mode (Python 3.12+)
)
```

### Connection Methods

```python
# Create cursor
cur = con.cursor()

# Transaction control
con.commit()
con.rollback()
con.close()

# Execute methods (shortcuts)
con.execute(sql, parameters)
con.executemany(sql, parameters)
con.executescript(sql_script)

# Context manager (auto-commits)
with con:
    cur.execute(...)
# Automatically commits on success, rolls back on exception
```

## Cursor Objects

### Cursor Methods

```python
cur.execute(sql, parameters)      # Execute single statement
cur.executemany(sql, parameters)  # Execute multiple times
cur.executescript(sql_script)     # Execute multiple statements
cur.fetchone()                    # Fetch next row
cur.fetchall()                    # Fetch all rows
cur.fetchmany(size)               # Fetch size rows
```

## Row Factories

### Using Row Factory for Dict-like Access

```python
# Default - returns tuples
cur.execute("SELECT * FROM movie")
row = cur.fetchone()  # ('Monty Python...', 1975, 8.2)

# Using Row factory for dict-like access
con.row_factory = sqlite3.Row
cur = con.cursor()
row = cur.execute("SELECT * FROM movie").fetchone()
print(row["title"])   # Access by column name

# Custom row factory
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))

con.row_factory = dict_factory
```

## Transaction Control

### Autocommit Mode (Python 3.12+)

```python
# New autocommit parameter (Python 3.12+)
con = sqlite3.connect("test.db", autocommit=True)
```

### Legacy Transaction Control

```python
# Default: DEFERRED (transaction starts on first modification)
con = sqlite3.connect("test.db", isolation_level="DEFERRED")

# IMMEDIATE: Acquire write lock immediately
con = sqlite3.connect("test.db", isolation_level="IMMEDIATE")

# EXCLUSIVE: Acquire exclusive lock
con = sqlite3.connect("test.db", isolation_level="EXCLUSIVE")

# None: Disable implicit transactions
con = sqlite3.connect("test.db", isolation_level=None)
```

## Type Adapters and Converters

### Register Custom Adapter

```python
import sqlite3
from datetime import datetime

def adapt_datetime(val):
    return val.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime)

# Now datetime objects can be stored in SQLite
```

### Register Custom Converter

```python
def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.connect("test.db", detect_types=sqlite3.PARSE_DECLTYPES)
sqlite3.register_converter("datetime", convert_datetime)
```

## Connection Context Manager

```python
# Using context manager (recommended)
with sqlite3.connect("test.db") as con:
    cur = con.cursor()
    cur.execute("INSERT INTO movie VALUES(?, ?, ?)", (title, year, score))
    # Auto-commits on success
    # Auto-rollbacks on exception
    # Auto-closes connection
```

## Thread Safety

```python
# Default: check_same_thread=True
# Connection can only be used in the thread that created it

# For multi-threaded use:
con = sqlite3.connect("test.db", check_same_thread=False)
# WARNING: You must serialize write operations yourself
```

## Best Practices

### 1. Always Use Context Managers

```python
with sqlite3.connect("database.db") as con:
    cur = con.cursor()
    # ... operations
```

### 2. Always Use Parameterized Queries

```python
# Never use f-strings or % formatting for SQL!
cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 3. Close Connections

```python
con.close()
# Or use context manager
```

### 4. Handle Exceptions

```python
try:
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO table VALUES(?, ?)", (val1, val2))
except sqlite3.Error as e:
    print(f"Database error: {e}")
```

## SQLite with FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI, Depends
import sqlite3

app = FastAPI()

def get_db():
    con = sqlite3.connect("app.db")
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()

@app.get("/items")
def read_items(db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("SELECT * FROM items")
    rows = cur.fetchall()
    return [dict(row) for row in rows]
```

### Note on Async Support

The standard `sqlite3` module is **synchronous**. For async FastAPI applications:

1. Use `run_in_executor` to run sync SQLite operations in a thread pool
2. Or use `aiosqlite` for async SQLite operations:

```python
# aiosqlite - async SQLite for Python
import aiosqlite

async def get_items():
    async with aiosqlite.connect("app.db") as db:
        async with db.execute("SELECT * FROM items") as cursor:
            rows = await cursor.fetchall()
            return rows
```

## Key Constants

| Constant | Description |
|----------|-------------|
| `sqlite3.apilevel` | DB-API version ("2.0") |
| `sqlite3.paramstyle` | Parameter style ("qmark") |
| `sqlite3.sqlite_version` | SQLite library version |
| `sqlite3.threadsafety` | Thread safety level |
| `PARSE_DECLTYPES` | Detect types from column declarations |
| `PARSE_COLNAMES` | Detect types from column names |