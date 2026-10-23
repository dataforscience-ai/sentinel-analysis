# Consolidated discussion findings: observations, decisions, open questions and learnings

## Method: How each piece of evidence was produced

Two methods were used: a written prompt given to an AI coding agent, and short Python scripts run by the pod. Both were checked by hand, and each has limits.

| **Evidence**                                                                                                           | **How it was produced**                                                                                                     | **What it gave**                                                                                                                             | **Limits and checks**                                                                                                                                                     |
|------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DATA_CARD.md, manifest.json, data_dictionary.json, feature_catalogue.json (to FE-03)                                   | Opened and read in VS Code; the text was read from screenshots                                                              | Purpose, time splits, declared counts, the schema with keys                                                                                  | Read by eye; a few table cells were cut off at the screen edge                                                                                                            |
| facts_tables folder: inventory.csv, tables_inventory.csv, manifest_table_split_counts.csv, data_dictionary_columns.csv | Prompt-driven: a written prompt given to Cline, an AI coding agent inside VS Code, which wrote and ran Python scripts       | File and folder counts and sizes; part-files per table and split; row counts from the manifest; every column with its type and key           | The run stopped when the AI provider's daily allowance ran out, so later steps were never produced. Cross-check found 13 files in tables that the inventory does not list |
| quick_profile.py and quick_profile.txt                                                                                 | Code-driven: a short Python script using pandas, written with AI assistance and run by the pod on a laptop with Python 3.14 | For all 18 tables: type, percentage missing, distinct values, range and common values per column                                             | First part-file of each split only (5,000 rows or fewer), so sample figures, not whole-table figures                                                                      |
| folder_peek.py and folder_peek.txt                                                                                     | Code-driven: a Python script that walks each non-table folder and previews its first file                                   | File counts and sizes, field names and a sample record for histories, training, parquet, corpus, documents, ground_truth, evaluation and sql | First file of each subfolder only. The first version reported zero files because of a bug in its file search; it was replaced and re-run                                  |
| Hand checks                                                                                                            | Arithmetic against the manifest, the data card and the CRD                                                                  | Main transactions total exactly 1,000,000; warm-up 100,000; channel mix and missing-data rates agree with the CRD                            | Done on sample figures                                                                                                                                                    |

**Why these files were read first.** The data card, the manifest and the data dictionary are the dataset's own documentation. They are small, quick to read, and they say what the data is, what exists and how it is laid out. The rest is about 750 MB in over 3,000 files and cannot be understood without them. The approach was to read the documentation first and then check the real files against it.

- **DATA_CARD.md:** why the dataset exists, the time splits, the rules of use and the limits.

- **manifest.json:** what exists and how much. Its declared counts were later checked against the files, which exposed 13 files the inventory does not list.

- **data_dictionary.json:** every column with its type and keys, which the attribute-by-attribute section needs.

Not read first: quality_report.json and requirements_coverage.json are still outstanding, and feature_catalogue.json has been read only as far as FE-03. They are second-level detail, but they are the next files to read, because quality_report.json bears on section 4 and requirements_coverage.json probably on section 3.

## Method: What the prompt asked for

The prompt told the AI agent to do descriptive analysis only, never to train a model or change a source file, to report only numbers it had actually computed, and to write UNKNOWN where it could not tell. It listed nine steps:

- Inventory every folder and file, with counts and sizes.

- Read the metadata files (manifest, data dictionary, feature catalogue, quality report and others).

- Profile every table: row counts, then per column type, missing values, distinct values and ranges.

- Check the relationships between tables through their keys.

- Analyse labels and fraud patterns by category, hour, region, device and amount.

- Check for leakage and for timing problems.

- Confirm the train, validation, holdout and warm-up periods.

- Describe the text tables with counts and examples.

- Finish with the 15 most important findings, each backed by a number.

Why a prompt: it covers a broad task quickly without writing code. Its weaknesses are that it depends on the AI service staying available and its output must be verified. Here only steps 1 and 2 were completed.

## Method: How the profiling code works, in plain words

quick_profile.py reads the first data file of every table split and describes each column:

- It points at the folder sentinel_data/tables and takes a list of table names (all 18 in the final version).

- For each table it finds the first file, part-00001.csv.gz, in every split folder.

- It loads that file into a pandas table.

- For every column it records the data type, the percentage of missing values and the number of distinct values.

- For numeric columns it adds the minimum, maximum and mean; for columns with 12 or fewer distinct values it lists the most common values with counts.

- It writes everything to quick_profile.txt, one block per table and split, with a count of duplicate rows.

folder_peek.py works the same way for the other folders. It walks each folder, counts files and sizes, groups the files by subfolder and file type, and previews the first file of each group: field names and a sample record for data files, or the opening text for markdown and SQL files.

**Why code as well as a prompt:** a script is repeatable, can be read line by line, and can be re-run on the full data. Its limit here is the same as the prompt's: it saw only the first file of each split, so every percentage is a sample estimate.

## Open questions raised by the analysis

Questions raised by the analysis that the pod may want to discuss:

- Why does features include reason_codes, and how is it derived? Is it safe to use?

- Why are four failed attempts more common than one, two or three?

- Which merchant categories are the other two of the ten? (The profile showed nine names.)

- Why are only 121 distance values present, and is location only at city level?

- How should the warm-up period be used, given half its rows are cold start?

- Why does BLOCK come almost only from the device blocklist, and is the near-absent model signal intended?

- How should the 42% of validation labels that are not eligible at the next split be treated?

- How should templated text, with about half of chunks repeated, be handled for the explanation tasks?

- Why are train documents linked to legacy cases while evaluation documents link to transactions?

- Since gold, reviewer and legacy samples are 25 to 40% fraud, how should they be used so they do not distort the 0.6% base rate?

- Why does histories/holdout contain a folder named part-00036.jsonl, and does it load cleanly?

- How do ground_truth events map to transactions, and how do we keep them out of model inputs?

- Why does the parquet view leave out merchant_id, and which view should a model use?

## Observations, working decisions and learnings

Working decisions below follow from the dataset's own documents (data card, manifest, dictionary) and from the sample profile. They are proposals for the pod to confirm.

| Topic | Key observation | Working decision | Learning |
|---|---|---|---|
| Where to start | The data card, manifest and data dictionary describe the whole dataset and are small | Read these three first, then check the real files against them | Checking the manifest against the disk exposed 13 files in `tables` that the inventory does not list |
| Sample against whole table | Profiles use the first 5,000 rows of each split | Label every percentage as a sample; run whole-table checks before relying on them | Missing-value and fraud rates differ by split (for example average value missing 0.5% to 51.6%) |
| Leakage | Labels, payment outcomes, simulated decisions, reviewer verdicts and ground-truth scenarios describe things after the payment or reveal the answer | Keep them out of model inputs (see the AI design file) | The data card itself warns against using predicted decisions, later verdicts and label-availability flags as features |
| Time handling | Timestamps are stored in UTC but splits start at midnight IST | Convert to IST before assigning splits, hour or night | The first holdout history is 31 Dec 2025 18:33 UTC, which is 1 Jan 2026 IST |
| Warm-up period | About half of warm-up rows are cold start (no history) | Use warm-up only to build customer histories, not as training targets (data card) | Features such as new device and new city are inflated in warm-up by the start-up effect |
| Enriched samples | Gold explanations are about 40% fraud, reviewer feedback 25 to 26%, legacy cases 27%, against 0.6 to 0.9% in labels | Do not use them to estimate the fraud rate | Prevalence must come from the labels table |
| Simulated decisions | decision_audit is simulated; almost every BLOCK comes from the device blocklist | Treat it as an audit-format example, not a benchmark | model_version reads SYNTHETIC-HEURISTIC-NOT-A-MODEL |
| Text quality | About half of document chunks repeat; explanations, gold targets and reviewer corrections have only dozens of distinct texts | De-duplicate and treat explanation scores with caution | The data card says semantic de-duplication is not certified |
