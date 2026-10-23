import gzip, json, os, sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = "sentinel_data"                     # run from the folder that contains sentinel_data
skip = {"tables", "facts_tables"}
TEXT = ("md", "txt", "sql", "json")
out = []
cut = lambda x, n=300: str(x).replace("\n", " ")[:n]
ext_of = lambda name: ".".join(name.split(".")[1:]) or "(none)"


def preview(f, e):
    if e in ("jsonl.gz", "jsonl", "ndjson", "ndjson.gz"):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt", encoding="utf-8") as fh:
            rec = json.loads(fh.readline())
        if isinstance(rec, dict):
            return ["fields: " + ", ".join(rec.keys()), "sample: " + cut(json.dumps(rec, ensure_ascii=False))]
        return ["first record is not an object", "sample: " + cut(rec)]
    if e in ("csv.gz", "csv", "parquet"):
        df = pd.read_parquet(f).head(2) if e == "parquet" else pd.read_csv(f, nrows=2)
        return ["columns: " + ", ".join(df.columns), "first row: " + cut(df.iloc[0].to_dict())]
    if e in TEXT:
        with open(f, encoding="utf-8", errors="replace") as fh:
            return ["starts with: " + cut(fh.read(900), 800)]
    return ["(not previewed)"]


for d in sorted(os.listdir(root)):
    path = os.path.join(root, d)
    if not os.path.isdir(path) or d in skip:
        continue
    files = []
    for dirpath, dirnames, filenames in os.walk(path):
        files += [os.path.join(dirpath, n) for n in filenames]
    files.sort()
    total = sum(os.path.getsize(f) for f in files) / 2**20
    out += ["=" * 70, f"{d}: {len(files)} files, {total:.1f} MB"]
    groups = {}
    for f in files:
        rel = os.path.relpath(f, path).split(os.sep)
        sub = rel[0] if len(rel) > 1 else "(top level)"
        groups.setdefault((sub, ext_of(os.path.basename(f))), []).append(f)
    for (sub, e), fl in groups.items():
        out.append(f"-- {sub} [{e}]: {len(fl)} files; example: {os.path.relpath(fl[0], root)}")
        for f in fl[: 4 if e in TEXT else 1]:
            if e in TEXT:
                out.append(f"   file: {os.path.basename(f)}")
            try:
                out += ["   " + line for line in preview(f, e)]
            except Exception as ex:
                out.append(f"   could not read: {ex}")

open("folder_peek.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
print("\nSaved: folder_peek.txt")