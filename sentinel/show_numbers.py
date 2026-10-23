import collections, glob, json, os, sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = "sentinel_data"                 # run from the folder that contains sentinel_data
out = []


def p(text=""):
    print(text)
    out.append(str(text))


def title(t):
    p("\n" + "=" * 74)
    p(t)
    p("=" * 74)


def first(table, split):
    fs = sorted(glob.glob(os.path.join(R, "tables", table, split, "part-00001.csv.gz")))
    return pd.read_csv(fs[0]) if fs else None


m = json.load(open(os.path.join(R, "manifest.json"), encoding="utf-8"))
dd = json.load(open(os.path.join(R, "data_dictionary.json"), encoding="utf-8"))

title("A. Counts declared in manifest.json")
for k, v in m["counts"].items():
    p(f"  {k:<24}{v:>12,}")
p(f"  fraud_rate declared: {m.get('fraud_rate')}    label_snapshot: {m.get('label_snapshot')}")

title("B. Rows per table and split, added up from manifest.json")
rows = collections.defaultdict(int)
for t in m["tables"]:
    rows[(t["table"], t["split"])] += t["rows"]
splits = ["train", "validation", "holdout", "warmup", "all"]
p(f"  {'table':<20}" + "".join(f"{s:>12}" for s in splits))
for t in sorted({k[0] for k in rows}):
    p(f"  {t:<20}" + "".join(f"{rows[(t, s)]:>12,}" if (t, s) in rows else f"{'-':>12}" for s in splits))
main = sum(rows[("transactions", s)] for s in ("train", "validation", "holdout"))
p(f"\n  transactions: train + validation + holdout = {main:,}   warm-up = {rows[('transactions', 'warmup')]:,}")

title("C. Columns, primary keys, foreign keys from data_dictionary.json")
total = 0
for t, v in dd.items():
    if not (isinstance(v, dict) and "columns" in v):
        continue
    cols = v["columns"]
    total += len(cols)
    pk = [c["name"] for c in cols if "PRIMARY KEY" in c["postgres_definition"]]
    fks = [f"{f[0]} -> {f[1]}.{f[2]}" if isinstance(f, list) and len(f) == 3 else str(f) for f in v.get("foreign_keys", [])]
    p(f"  {t:<19}{len(cols):>3} columns | PK: {', '.join(pk) or '-'} | FK: {'; '.join(fks) or 'none'}")
p(f"\n  total columns: {total}")

title("D. Sample checks: first part-file of each split (5,000 rows each)")
try:
    p(f"  {'transactions':<14}{'missing location':>18}{'missing device':>16}{'missing avg value':>19}{'duplicates':>12}{'max amount Rs':>15}")
    for s in ["train", "validation", "holdout", "warmup"]:
        df = first("transactions", s)
        if df is not None:
            p(f"  {s:<14}{df['customer_location'].isna().mean():>18.1%}{df['device_id'].isna().mean():>16.1%}"
              f"{df['average_transaction_value'].isna().mean():>19.1%}{int(df.duplicated().sum()):>12}{df['transaction_amount'].max():>15,.0f}")
    df = first("transactions", "train")
    p("\n  payment channel share (train sample): " + ", ".join(f"{k} {v:.0%}" for k, v in df["payment_channel"].value_counts(normalize=True).items()))
    df = first("transactions", "validation")
    p("  failed_transactions counts (validation sample): " + ", ".join(f"{k}:{v}" for k, v in df["failed_transactions"].value_counts().sort_index().items()))
    p(f"\n  {'labels':<14}{'fraud rows':>12}{'of':>8}{'fraud %':>10}")
    for s in ["train", "validation", "holdout", "warmup"]:
        df = first("labels", s)
        if df is not None:
            p(f"  {s:<14}{int(df['fraud_label'].sum()):>12}{len(df):>8,}{df['fraud_label'].mean():>10.2%}")
except Exception as ex:
    p(f"  could not compute: {ex}")

title("E. Files and size per folder (leaves out facts_tables)")
tf = tb = 0
for d in sorted(os.listdir(R)):
    path = os.path.join(R, d)
    if d == "facts_tables":
        continue
    n = b = 0
    if os.path.isdir(path):
        for dp, dn, fn in os.walk(path):
            for x in fn:
                n += 1
                b += os.path.getsize(os.path.join(dp, x))
    else:
        n, b = 1, os.path.getsize(path)
    tf += n
    tb += b
    p(f"  {d:<38}{n:>7,} files{b / 2**20:>10.1f} MB")
p(f"\n  TOTAL {tf:,} files, {tb / 2**20:.0f} MB")

open("numbers_for_talk.txt", "w", encoding="utf-8").write("\n".join(out))
print("\nSaved: numbers_for_talk.txt")