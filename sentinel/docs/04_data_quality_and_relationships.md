# Relationships between tables (primary and foreign keys)

| **Child column**                                                       | **Parent column**                      | **Relationship**                                                   |
|------------------------------------------------------------------------|----------------------------------------|--------------------------------------------------------------------|
| transactions.customer_id                                               | customers.customer_id                  | Many transactions per customer                                     |
| transactions.merchant_id                                               | merchants.merchant_id                  | Many transactions per merchant                                     |
| transactions.device_id (nullable)                                      | devices.device_id                      | Many transactions per device                                       |
| payment_outcomes, labels, features: transaction_id                     | transactions.transaction_id            | One-to-one (the key is both primary and foreign)                   |
| gold_explanations, preference_pairs, reviewer_feedback: transaction_id | transactions.transaction_id            | Zero or more per transaction                                       |
| documents.transaction_id (nullable)                                    | transactions.transaction_id            | Optional link from a document                                      |
| documents.legacy_case_id (nullable)                                    | legacy_cases.legacy_case_id            | Optional link from a document                                      |
| legacy_cases.customer_id                                               | customers.customer_id                  | Many cases per customer                                            |
| document_chunks.document_id                                            | documents.document_id                  | Many chunks per document                                           |
| decision_audit.transaction_id                                          | transactions.transaction_id (probable) | TO CONFIRM: schema line not seen; 5,000 distinct values per sample |
| histories.transaction_id                                               | transactions.transaction_id            | One history per transaction (inferred from the file contents)      |
| training sft, gold, dpo: transaction_id                                | transactions.transaction_id            | Training examples built from transactions                          |
| ground_truth.event_number                                              | Unclear: no transaction_id seen        | TO CONFIRM                                                         |

*Some foreign-key cells were cut off at the screen edge; only the visible part was read. Row counts per split match across transactions, labels, features, payment_outcomes and decision_audit, which supports the one-to-one reading.*

# Data quality observations

All figures come from the first part-file (5,000 rows) of each split, so they estimate rather than prove whole-table behaviour.

| **\#** | **Observation**                                | **Evidence**                                                                                                                           | **Impact / handling**                                                                      |
|--------|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| 1      | Missing customer_location                      | 2.7 to 3.0% of rows (CRD says about 3%)                                                                                                | Distance and new-city features are empty; a flag exists                                    |
| 2      | Missing device_id                              | 0.3% (validation, holdout) to 1.7 to 1.8% (train, warm-up)                                                                             | is_new_device and device-sharing features are empty; more common in earlier periods        |
| 3      | Missing average_transaction_value (cold start) | 0.5 to 0.6%, 4.2% (train sample), 51.6% (warm-up sample)                                                                               | amount_to_avg_ratio is empty; warm-up is not suitable as training targets (data card)      |
| 4      | Extreme amounts and ratios                     | Maximum Rs 5.8 lakh to Rs 69 lakh; ratio up to about 9,838                                                                             | Above the CRD's Rs 10 lakh caution; needs capping or transformation                        |
| 5      | Money stored twice                             | transaction_amount equals amount_paise / 100 in all samples                                                                            | Keep paise as authoritative; add a consistency check                                       |
| 6      | Booleans with nulls                            | is_new_device and is_new_city load as generic object type                                                                              | Convert to nullable boolean                                                                |
| 7      | Constant columns                               | is_synthetic always True; one failure code; one feature version; split constant per folder                                             | Exclude from model inputs                                                                  |
| 8      | Drift across time                              | Mean account_age 592 to 923; mean previous_transactions 1.4 to 4.4                                                                     | Time-based splits are essential (CRD FR-ML-05)                                             |
| 9      | Class imbalance                                | 30 to 46 fraud rows per 5,000 (0.60 to 0.92%)                                                                                          | Weighting or resampling; precision-recall metrics                                          |
| 10     | Label eligibility                              | Validation sample: 2,097 of 5,000 not eligible at next split start                                                                     | Filter on eligible_at_next_split_start for strict simulation                               |
| 11     | Time-dependent category encoding               | Train and warm-up samples use constant 0.006 with count 0; validation and holdout use a frozen 1 Nov 2025 encoder                      | Rates are not comparable across splits                                                     |
| 12     | Spike at four failed attempts                  | Value 4 appears 290 to 366 times, more than 1, 2 or 3                                                                                  | Ask why; check the generator and business logic                                            |
| 13     | Duplicates                                     | No duplicate rows and unique transaction_id in every sampled part                                                                      | Whole-table check still needed                                                             |
| 14     | Timestamps stored as UTC text                  | mcc_encoding_as_of 18:30 UTC equals midnight IST                                                                                       | Convert to IST before computing hour and night                                             |
| 15     | Very high failure rate                         | 11 to 13% of attempts FAILED, one simulated code                                                                                       | Realistic rates are lower; do not generalise                                               |
| 16     | Empty or unknown files                         | reason code.docx is 0 bytes; an Excel worksheet of unknown origin                                                                      | Re-download or ignore                                                                      |
| 17     | Unlisted files                                 | tables folder holds 1,170 files and 338.3 MB; the inventory accounts for 1,157 files and 330.4 MB                                      | 13 files and about 7.9 MB unexplained; check                                               |
| 18     | Duplicate chunk text                           | document_chunks: about 2,530 distinct texts per 5,000 chunks                                                                           | De-duplicate before text use (data card excludes exact duplicates from pre-training)       |
| 19     | Templated, low-diversity text                  | Explanations 46 to 54 distinct; gold targets 35 to 56; corrected explanations 43 to 52; template families 36 to 425                    | Explanation scores may overstate real quality                                              |
| 20     | Samples enriched with fraud                    | Gold 40%, reviewer feedback 25 to 26%, legacy cases 26.8%, against 0.6 to 0.9% in labels                                               | Not the real prevalence; do not use to estimate fraud rate                                 |
| 21     | One kind of rejected explanation               | All 5,000 preference pairs share the reason: unsupported fact absent from prompt                                                       | Teaches grounding only; other failure types are absent                                     |
| 22     | Nothing is human-reviewed                      | Gold, preference pairs and documents are marked synthetic_candidate_not_human_reviewed                                                 | Treat as candidates; do not claim reviewer approval                                        |
| 23     | Simulated decisions barely use a model         | fraud_probability maximum 0.82 to 0.87, mean 0.06 to 0.07; BLOCK from HARD_RULE: holdout 38 of 38, train 13 of 13, validation 17 of 18 | Not a benchmark for accuracy; never a feature or label (data card)                         |
| 24     | Legacy cases cannot yield features             | evidence says history_not_reconstructed true; channels are exactly 25% each                                                            | Use for narratives, not for training features                                              |
| 25     | Different links by split                       | Train documents carry legacy_case_id; validation and holdout documents carry transaction_id                                            | Training text comes from the archive; evaluation text from the main period                 |
| 26     | Policy fixtures start with the train period    | list_entries, threshold_sets and config_changes are all dated 1 Jan 2025 IST                                                           | Policy objects are not time-varying in this data                                           |
| 27     | Split boundaries are midnight IST              | First holdout history has as_of 31 Dec 2025 18:33 UTC, which is 1 Jan 2026 IST; the same pattern appears at the other split starts     | Splitting on UTC dates would misplace the first 5.5 hours of each split                    |
| 28     | Odd packaging in histories                     | histories/holdout holds a folder named part-00036.jsonl containing a file of the same name                                             | Loaders must handle it; check for an interrupted write                                     |
| 29     | Near-identical text across families            | The first 600 characters of playbooks and regulatory exercises 0001 to 0004 match apart from the title                                 | Template-level de-duplication needed (data card: semantic de-duplication is not certified) |
| 30     | Different column sets across views             | parquet transactions has 19 columns and no merchant_id; the transactions table has 18 columns and no label                             | State which view a model uses; do not mix them                                             |
| 31     | The dataset ships its own checks               | validate.sql tests money match, label delay of exactly 60 days, feature timestamps and account creation before transaction             | Run it on a database load; our sample agrees on money consistency                          |

## 4.1 Privacy and security

The data card says all events and text are fictional, and every sampled table has is_synthetic equal to True, so no real personal data is expected. Identifiers are pseudonymised, and merchant names are fictional. The card also says its PII scan is a deterministic sample check with limited patterns, not the client's human redaction audit. The dataset runs in a Supabase teaching environment, which does not recreate AWS residency, private networking or immutable storage requirements.

## 4.2 Checks not yet done

- Referential integrity across the full tables (orphan keys).

- Duplicates across all part files.

- Running validate.sql on a database load, and counting rows in parquet, histories and training.

- How ground_truth events map to transactions (no transaction_id was seen).

- quality_report.json, rules_config.json and requirements_coverage.json (not read yet), and feature_catalogue.json from FE-04 onward.

- Fraud rate by category, hour, region and amount band over the whole dataset.
