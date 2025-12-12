

# Mini SQL Engine

This is a small Python project that acts like a tiny SQL engine for CSV files.
You don’t need MySQL, PostgreSQL, or any database setup — just a CSV file and this script.
It’s mainly built for learning and experimenting with how basic SQL operations work under the hood.

---

## Features

* Select specific columns or fetch all columns
  Examples:
  `SELECT * FROM people;`
  `SELECT name, age FROM people;`

* Basic `WHERE` filtering

  * Single condition: `WHERE age > 30`
  * With AND/OR:

    * `WHERE occupation = "Chef" AND city = "Chennai"`
    * `WHERE city = "Bengaluru" OR city = "Chennai"`

* Supports `COUNT(*)` and `COUNT(column)`

* Case-insensitive value comparisons

* Automatically trims extra spaces in CSV values

* Simple interactive shell (REPL)

  * Type queries and see results immediately
  * Type `exit` or `quit` to leave

---

## How to Run

1. Make sure Python 3.6+ is installed

2. Put your CSV file in the same folder as `mini_sql.py`

3. Run:

   ```bash
   python mini_sql.py
   ```

4. When the prompt appears, start typing queries. Example:

   ```
   SELECT * FROM people;
   SELECT name, city FROM people WHERE city = "Chennai";
   SELECT COUNT(*) FROM people WHERE occupation = "Data Analyst";
   ```

---

## CSV Format

The script expects a standard CSV file with a header row.
Example:

```
name,age,city,occupation,salary
Rohith,28,Hyderabad,Chef,30000
Divya,27,Bengaluru,Data Analyst,40000
Harish,30,Chennai,Software Engineer,50000
```

Column names are case-insensitive, and extra spaces are cleaned up automatically.

---

## Supported SQL Syntax

### SELECT

```
SELECT * FROM table;
SELECT column1, column2 FROM table;
```

### FROM

Just give the CSV name (without `.csv`).

### WHERE

Supports the usual comparison operators:

`=, !=, <, >, <=, >=`

Works with both strings and numbers.

Examples:

```
WHERE age >= 25
WHERE city = "Chennai"
WHERE occupation != "Chef"
```

### COUNT

```
SELECT COUNT(*) FROM table;
SELECT COUNT(age) FROM people WHERE city = "Hyderabad";
```

---

## Limitations

This is a simple project, so it doesn’t support:

* Parentheses in WHERE
* JOINs
* GROUP BY
* ORDER BY
* Subqueries
* Multiple tables in one query

---

## Error Handling

The script gives clear messages when something goes wrong:

* Unknown column
* CSV file missing
* Bad SQL formatting

---

## Why This Exists

Mostly for learning — to understand how SQL parsing, filtering, and basic aggregation work internally.
It’s also handy if you want to quickly query a CSV file without importing it into a real database.

---


