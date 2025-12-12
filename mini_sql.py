


import csv
import os
import shlex
from typing import List, Dict, Optional

class QueryError(Exception):
    pass

def read_csv_table(basename: str) -> List[Dict[str, str]]:
    filename = basename + ".csv"
    if not os.path.isfile(filename):
        raise QueryError(f"CSV file not found: '{filename}'")

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        if not reader.fieldnames:
            raise QueryError(f"No columns found in '{filename}'. Is it a valid CSV with header?")
    return data

def print_table(rows: List[Dict[str, str]], columns: List[str]):
    if len(rows) == 0:
        print("(no rows)")
        return

    widths = {c: max(len(c), *(len(str(r.get(c, ''))) for r in rows)) for c in columns}

    header = " | ".join(c.ljust(widths[c]) for c in columns)
    sep = "-+-".join("-" * widths[c] for c in columns)
    print(header)
    print(sep)

    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))

def parse_query(raw: str) -> Dict:
    if not raw.strip():
        raise QueryError("Empty query.")

    up = raw.upper()
    if "SELECT" not in up or "FROM" not in up:
        raise QueryError("Query must contain SELECT and FROM.")

    sel_idx = up.find("SELECT")
    from_idx = up.find("FROM", sel_idx)
    if from_idx == -1:
        raise QueryError("Missing FROM clause.")
    where_idx = up.find("WHERE", from_idx)

    select_part = raw[sel_idx + len("SELECT"):from_idx].strip()

    if where_idx == -1:
        from_part = raw[from_idx + len("FROM"):]
        where_part = None
    else:
        from_part = raw[from_idx + len("FROM"):where_idx]
        where_part = raw[where_idx + len("WHERE"):]

    select_part = select_part.strip()
    from_part = from_part.strip()
    if not select_part:
        raise QueryError("SELECT clause is empty.")
    if not from_part:
        raise QueryError("FROM clause is empty.")

    def split_select(s: str) -> List[str]:
        parts = []
        cur = ""
        paren = 0
        for ch in s:
            if ch == '(':
                paren += 1
            elif ch == ')':
                paren -= 1
            if ch == ',' and paren == 0:
                parts.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            parts.append(cur.strip())
        return parts

    select_items = split_select(select_part)
    select_parsed = []

    for it in select_items:
        it_strip = it.strip()
        if it_strip == "*":
            select_parsed.append("*")
            continue

        up_it = it_strip.upper()
        if up_it.startswith("COUNT(") and up_it.endswith(")"):
            inner = it_strip[it_strip.find("(") + 1:-1].strip()
            if inner == "":
                raise QueryError("COUNT() must contain '*' or a column name.")
            select_parsed.append(f"COUNT({inner})")
            continue

        if "(" in it_strip or ")" in it_strip:
            raise QueryError(f"Unsupported select expression: '{it_strip}'")

        select_parsed.append(it_strip)

    table = from_part.split()[0].strip()

    where = None
    if where_part:
        try:
            tokens = shlex.split(where_part)
        except ValueError:
            raise QueryError("Unable to parse WHERE clause. Check quotes.")

        if len(tokens) == 3:
            col, op, val = tokens
        else:
            joined = where_part.strip()
            for op_char in ['>=', '<=', '!=', '>', '<', '=']:
                if op_char in joined:
                    left, right = joined.split(op_char, 1)
                    col = left.strip()
                    op = op_char
                    val = right.strip()
                    if len(val) >= 2 and ((val[0] == val[-1]) and val[0] in ("'", '"')):
                        val = val[1:-1]
                    break
            else:
                raise QueryError("Malformed WHERE clause.")
        if len(val) >= 2 and (val[0] == val[-1]) and val[0] in ("'", '"'):
            val = val[1:-1]
        where = {"col": col, "op": op, "val": val}

    return {"select": select_parsed, "from": table, "where": where}


def apply_where(data: List[Dict[str, str]], where: Optional[Dict]) -> List[Dict[str, str]]:
    if where is None:
        return data

    col = where["col"]
    op = where["op"]
    val_raw = where["val"]

    if len(data) > 0 and col not in data[0]:
        raise QueryError(f"WHERE column '{col}' does not exist.")

    def try_float(x):
        try:
            return float(x), True
        except:
            return x, False

    result = []
    for row in data:
        cell = row.get(col, "")
        cell_val, cell_is_num = try_float(cell)
        val_val, val_is_num = try_float(val_raw)
        matched = False

        if cell_is_num and val_is_num:
            a, b = cell_val, val_val
            if op == ">": matched = a > b
            elif op == "<": matched = a < b
            elif op == ">=": matched = a >= b
            elif op == "<=": matched = a <= b
            elif op in ("=", "=="): matched = a == b
            elif op in ("!=", "<>"): matched = a != b
            else:
                raise QueryError(f"Invalid operator '{op}'.")

        else:
            if op in ("=", "=="): matched = str(cell) == str(val_raw)
            elif op in ("!=", "<>"): matched = str(cell) != str(val_raw)
            else:
                raise QueryError(f"Operator '{op}' not allowed for strings.")

        if matched:
            result.append(row)

    return result


def execute(parsed: Dict, table_data: List[Dict[str, str]]):
    select_items = parsed["select"]
    where = parsed["where"]

    filtered = apply_where(table_data, where)

    counts = [s for s in select_items if s.upper().startswith("COUNT(")]
    if counts:
        if len(select_items) != len(counts):
            raise QueryError("Cannot mix COUNT with normal columns.")

        for cnt in counts:
            inner = cnt[cnt.find("(") + 1:cnt.rfind(")")].strip()
            if inner == "*":
                print(f"COUNT(*) = {len(filtered)}")
            else:
                col = inner
                if len(filtered) > 0 and col not in filtered[0]:
                    raise QueryError(f"Column '{col}' does not exist.")
                c = sum(1 for r in filtered if r.get(col, "") != "")
                print(f"COUNT({col}) = {c}")
        return

    if select_items == ["*"]:
        cols = list(filtered[0].keys()) if filtered else list(table_data[0].keys())
    else:
        cols = select_items
        if filtered:
            for c in cols:
                if c not in filtered[0]:
                    raise QueryError(f"Column '{c}' does not exist.")

    print_table(filtered, cols)


def repl(basename: str):
    try:
        data = read_csv_table(basename)
    except QueryError as e:
        print("Error:", e)
        return

    print(f"Loaded table '{basename}.csv' with columns: {', '.join(data[0].keys()) if data else '(none)'}")
    print("Type SQL queries. Type 'exit' to quit.")

    while True:
        try:
            raw = input("sql> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if raw.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        try:
            parsed = parse_query(raw)
            table = parsed["from"]

            if table != basename:
                table_data = read_csv_table(table)
            else:
                table_data = data

            execute(parsed, table_data)

        except QueryError as e:
            print("Query error:", e)
        except Exception as e:
            print("Unexpected error:", e)

if __name__ == "__main__":
    print("Mini SQL Engine")
    base = input("Enter CSV filename (without .csv): ").strip()
    if not base:
        print("No filename provided. Exiting.")
    else:
        repl(base)
