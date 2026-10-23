# Project SENTINEL: dataset understanding (pod task)

Descriptive analysis of the synthetic SENTINEL payment-fraud dataset. No model was trained or selected, and no source file was changed. The written findings are in the `docs` folder as Markdown, so they can be read directly in the browser.

## Where each assessment item is answered

| Assessment item | File |
|---|---|
| Dataset overview and structure | [docs/01_dataset_overview.md](docs/01_dataset_overview.md) |
| Complete attribute understanding (all 171 attributes, with type, meaning and observed values) | [docs/02_data_dictionary.md](docs/02_data_dictionary.md) |
| Business relevance and mapping to the client's requirements | [docs/03_business_mapping.md](docs/03_business_mapping.md) |
| Data quality and relationships (31 observations, primary and foreign keys) | [docs/04_data_quality_and_relationships.md](docs/04_data_quality_and_relationships.md) |
| AI system design opportunities (inputs, targets, preprocessing, features, approaches, real-time against batch) | [docs/05_ai_design_opportunities.md](docs/05_ai_design_opportunities.md) |
| Consolidated discussion findings (method, observations, decisions, open questions) | [docs/06_discussion_findings.md](docs/06_discussion_findings.md) |
| Individual pod contributions | [docs/07_individual_contributions.md](docs/07_individual_contributions.md) |
| Folder guide, evidence and limits | [docs/08_appendices.md](docs/08_appendices.md) |
| The same report as one Word document | [report/](report/) |

## Key results
- **Size:** 18 tables, 171 attributes, 3,287 files, about 752 MB. 1,100,000 transactions: 1,000,000 main plus 100,000 warm-up.
- **Time splits:** warm-up Oct to Dec 2024, train Jan to Oct 2025, validation Nov to Dec 2025, holdout Jan to Feb 2026. Labels mature 60 days after a transaction.
- **Fraud rate:** declared 0.6%; the 5,000-row samples show 0.60% to 0.92%.
- **Missing data (sample):** customer location about 3%; device 0.3% to 1.8%; average transaction value 0.5% to 51.6% (the warm-up is a cold start).
- **Leakage risks:** labels and their timing, payment outcomes, simulated decisions, reviewer verdicts, ground-truth scenarios and `is_synthetic` must not be model inputs.
- **Synthetic limits:** decisions are simulated, gold and preference data are not human-reviewed, and the sample is far smaller than PayVista's real volume.

## How the evidence was produced
1. Read the dataset's own documents first: the data card, the manifest and the data dictionary.
2. Used a written prompt in an AI coding agent for the file and table inventories (see the discussion findings file for the prompt's scope and outcome).
3. Ran short Python scripts on the dataset: `quick_profile.py`, `folder_peek.py` and `show_numbers.py`. Their outputs are the `.txt` files in this folder.
4. Cross-checked totals against the manifest and the data card.

## How to run
Run from the folder that contains `sentinel_data` (not included here; about 750 MB of course material):
```
python show_numbers.py
python quick_profile.py
python folder_peek.py
```

## Limits
Figures come from the first part-file of each split (5,000 rows or fewer), not whole tables, and are labelled as samples. The scripts and the report drafting were written with AI assistance (Claude), and every number was produced by running the scripts on the real dataset.
