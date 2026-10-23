import glob, os, sys
import pandas as pd

root = os.path.join("sentinel_data", "tables")
wanted = sys.argv[1:] or ["transactions", "labels", "features", "payment_outcomes", "customers", "merchants", "devices", "decision_audit", "reviewer_feedback", "gold_explanations", "preference_pairs", "documents", "document_chunks", "legacy_cases", "list_entries", "hard_rules", "threshold_sets", "config_changes"]

out = []
for t in wanted:
    files = sorted(glob.glob(os.path.join(root, t, "*", "part-00001.csv.gz")))
    for f in files:
        split = f.split(os.sep)[-2]
        df = pd.read_csv(f)
        out.append("=" * 72)
        out.append(f"{t} / {split}  (first part: {len(df)} rows, duplicate rows: {int(df.duplicated().sum())})")
        for c in df.columns:
            s = df[c]
            top = ""
            if s.nunique(dropna=False) <= 12:
                top = " | " + ", ".join(f"{k}:{v}" for k, v in s.value_counts(dropna=False).head(8).items())
            num = ""
            if pd.api.types.is_numeric_dtype(s) and s.nunique() > 2:
                num = f" | min={s.min():g} max={s.max():g} mean={s.mean():.4g}"
            out.append(f"{c:34s}{str(s.dtype):9s} null={s.isna().mean():6.1%} uniq={s.nunique():6d}{num}{top}")
open("quick_profile.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out[:60])); print("\nSaved: quick_profile.txt")