# Project SENTINEL: dataset overview

Part of the pod report *Dataset understanding*. Figures labelled sample come from the first part-file (5,000 rows or fewer) of each split, not whole tables. Meanings marked inferred come from column names; where the client requirement document or the data card defines a field, the text says so.

# Key findings at a glance

- **Size:** 18 tables, 171 attributes and 3,287 files (about 752 MB). There are 1,100,000 transactions: 1,000,000 main plus 100,000 warm-up.

- **Fraud rate:** declared at 0.6%; the five-thousand-row samples show 0.60% to 0.92% depending on the split.

- **Channel mix matches the CRD:** UPI 56 to 59%, card 31 to 33%, wallet 6 to 7%, net banking 4 to 5%.

- **Missing data:** customer_location about 3%, device_id 0.3 to 1.8%, and history-based fields are missing for 51.6% of the warm-up sample (cold start).

- **Extreme values:** amounts reach Rs 69 lakh against a mean near Rs 5,000, and the amount-to-average ratio reaches about 9,800.

- **All ten CRD features exist** as columns in the features table. has_recent_failures equals 3 or more failed attempts in all four samples.

- **Time matters:** account age and recent-transaction counts grow from the warm-up period to the holdout, and the merchant-category encoding is frozen at 1 November 2025 for validation and holdout.

- **Leakage risks:** labels, payment_outcomes, decision_audit, reviewer_feedback, the eligibility flag, is_synthetic and probably reason_codes must not be model inputs.

- **It is synthetic and small:** decision_audit values are simulated, gold and preference data have no human approval, and volumes are far below PayVista's real scale.

- **Simulated decisions:** decision_audit is 97.6 to 98.5% ALLOW, 1.2 to 1.6% REVIEW and 0.3 to 0.8% BLOCK. Almost every BLOCK comes from the device blocklist, because simulated probabilities rarely reach 0.85.

- **Text is templated and not human-reviewed:** explanations, gold targets and reviewer corrections have only dozens of distinct texts, and about half of document chunks repeat.

- **Some samples are enriched with fraud:** gold explanations 40%, reviewer feedback 25 to 26% and legacy cases 27%, against 0.6 to 0.9% in the labels.

- **Beyond the tables:** histories lists each transaction's prior events; training holds ready-made pre-training, fine-tuning, gold and preference sets plus a prompt-format comparison; ground_truth holds scenario labels marked never model input; sql ships the schema and its own zero-violation checks.

- **Still open:** quality_report.json, requirements_coverage.json, feature_catalogue.json from FE-04 onward, 13 files in the tables folder that the manifest does not list, running validate.sql, how ground_truth events map to transactions, and whole-table checks.

# First look: opening the dataset for the first time

This is what a newcomer sees before reading any file. Counts leave out the facts_tables folder, which was created during the analysis.

## The folders and files

```text
sentinel_data/   (3,287 files, about 752 MB)
|-- DATA_CARD.md                  3.9 KB    what the dataset is, rules of use
|-- manifest.json               890.6 KB    files, row counts, checksums
|-- data_dictionary.json         19.7 KB    every column, type and key
|-- feature_catalogue.json        3.5 KB    feature definitions (read to FE-03)
|-- quality_report.json           2.8 KB    not read yet
|-- requirements_coverage.json    1.4 KB    not read yet
|-- rules_config.json             3.9 KB    not read yet
|-- reference_sources.json        516 B     not read yet
|-- New Microsoft Excel Worksheet.xlsx      origin unknown
|-- reason code.docx              0 B       empty file
|-- tables/         1,170 files   322.6 MB   the 18 tables
|-- histories/        256 files   236.5 MB   prior events per transaction
|-- training/         214 files   133.6 MB   ready-made training sets
|-- parquet/           45 files    45.2 MB   flat transactions view
|-- corpus/            18 files     6.8 MB   source text
|-- documents/      1,525 files     2.8 MB   readable text copies
|-- ground_truth/      44 files     3.8 MB   simulator scenario labels
|-- evaluation/         1 file     84.1 KB   holdout explanations
|-- sql/                4 files    18.5 KB   database scripts
```

## The types of files

| **Type**               | **Files** | **Where**                                             | **What it is**                                                      |
|------------------------|-----------|-------------------------------------------------------|---------------------------------------------------------------------|
| **csv.gz**             | 1,170     | tables                                                | Compressed spreadsheet-style rows                                   |
| **jsonl.gz and jsonl** | 533       | histories, training, corpus, ground_truth, evaluation | Compressed records, one JSON record per line; can hold nested lists |
| **md**                 | 1,526     | documents, DATA_CARD                                  | Readable text                                                       |
| **parquet**            | 45        | parquet                                               | Compact columns for fast analysis                                   |
| **sql**                | 4         | sql                                                   | Database set-up and checks                                          |
| **json**               | 7         | loose files                                           | Documentation and settings                                          |
| **xlsx and docx**      | 2         | loose files                                           | Not part of the data (one is empty)                                 |

## The structure

- **Tables:** tables/\<table\>/\<split\>/part-00001.csv.gz and so on. Each part holds 5,000 rows, and the last part of a split is shorter.

- **Splits:** train, validation, holdout and warm-up for event tables, and all for reference tables such as customers and merchants.

- **Design:** a database exported to files. Each table has a key, and transaction_id links most of them.

- **Other folders:** training and corpus follow the same pattern, \<type\>/\<split\>/part-xxxxx.jsonl.gz.

## First conclusions

- It is a payment-fraud dataset arranged like a small database, with text added for language-model work.

- The tables, histories and training folders make up about 90% of the size.

- File types follow content: tables as csv.gz, nested or text records as jsonl.gz, fast views as Parquet, readable text as markdown.

- The sensible start is the documentation (data card, manifest, dictionary), then the tables, then the rest.

# 1. Dataset overview

## 1.1 Purpose and business problem

The dataset card describes SENTINEL as a synthetic teaching dataset that exercises the PayVista SENTINEL pipeline using fictional events and documents. It does not establish model accuracy, regulatory compliance, production throughput or investigator quality.

The business problem comes from the client requirement document: PayVista, an Indian payment gateway, needs to decide for every payment whether to ALLOW, REVIEW or BLOCK, with a fraud probability and a plain-language explanation. Losses are rising, too many genuine payments are declined or reviewed, and reviewers are overloaded. This dataset provides the payments, labels, features, rules and text needed to build and test that capability.

## 1.2 Structure

- **Tables:** 18 relational tables in a PostgreSQL-style schema named sentinel_demo, stored as compressed CSV parts of 5,000 rows under tables/\<table\>/\<split\>/.

- **Other folders:** corpus, documents, evaluation, ground_truth, histories, parquet, sql and training (see 1.6 and Appendix A).

- **Version:** 1.0.1, seed 20261010, label snapshot 1 May 2026 (IST), declared fraud rate 0.006.

- **Units and time:** all money is in INR with integer paise authoritative; timestamps are stored in UTC and read in IST for calendar splits and night features.

- **Records and attributes:** 5,679,150 rows across all tables (see 1.4) and 171 attributes (167 types read from the dictionary; 4 decision_audit columns identified from the profile).

## 1.3 Time splits

| **Split**  | **Period (data card)**    | **Transactions** | **Use**                                                 |
|------------|---------------------------|------------------|---------------------------------------------------------|
| warm-up    | October to December 2024  | 100,000          | Builds customer histories; not used as training targets |
| train      | January to October 2025   | 714,745          | Fitting                                                 |
| validation | November to December 2025 | 144,803          | Tuning and calibration                                  |
| holdout    | January to February 2026  | 140,452          | Sealed acceptance data                                  |

Labels mature 60 days after a transaction. The dataset snapshot is 1 May 2026. The data card warns that a two-month validation window with a 60-day delay leaves few prospectively mature validation examples, and that the retrospective split must not be mistaken for a no-delay production experiment.

## 1.4 Record counts per table and split (from the manifest)

| **Table**         | **Train** | **Validation** | **Holdout** | **Warm-up** | **All** | **Total** |
|-------------------|-----------|----------------|-------------|-------------|---------|-----------|
| transactions      | 714,745   | 144,803        | 140,452     | 100,000     | \-      | 1,100,000 |
| features          | 714,745   | 144,803        | 140,452     | 100,000     | \-      | 1,100,000 |
| labels            | 714,745   | 144,803        | 140,452     | 100,000     | \-      | 1,100,000 |
| payment_outcomes  | 714,745   | 144,803        | 140,452     | 100,000     | \-      | 1,100,000 |
| decision_audit    | 714,745   | 144,803        | 140,452     | \-          | \-      | 1,000,000 |
| documents         | 30,879    | 4,219          | 3,908       | \-          | \-      | 39,006    |
| document_chunks   | 61,753    | 8,438          | 7,816       | \-          | \-      | 78,007    |
| reviewer_feedback | 13,761    | 2,907          | 2,708       | \-          | \-      | 19,376    |
| gold_explanations | 8,000     | \-             | 500         | \-          | \-      | 8,500     |
| preference_pairs  | 5,000     | \-             | \-          | \-          | \-      | 5,000     |
| customers         | \-        | \-             | \-          | \-          | 25,000  | 25,000    |
| devices           | \-        | \-             | \-          | \-          | 100,120 | 100,120   |
| merchants         | \-        | \-             | \-          | \-          | 2,000   | 2,000     |
| legacy_cases      | \-        | \-             | \-          | \-          | 2,000   | 2,000     |
| list_entries      | \-        | \-             | \-          | \-          | 137     | 137       |
| hard_rules        | \-        | \-             | \-          | \-          | 2       | 2         |
| threshold_sets    | \-        | \-             | \-          | \-          | 1       | 1         |
| config_changes    | \-        | \-             | \-          | \-          | 1       | 1         |
| TOTAL             |           |                |             |             |         | 5,679,150 |

*Main transactions add up to exactly 1,000,000 and warm-up to 100,000, matching the manifest. reviewer_feedback holdout and validation counts are confirmed by the profile; the train total comes from the manifest.*

## 1.5 What each record represents

| **Table**             | **One row is**                           | **Purpose**                                       | **Basis**                        |
|-----------------------|------------------------------------------|---------------------------------------------------|----------------------------------|
| **transactions**      | One payment attempt                      | Core payment events to be scored                  | Documented (CRD 7.1)             |
| **labels**            | Fraud verdict for one transaction        | Prediction target and label timing                | Documented (CRD, data card)      |
| **features**          | Engineered clues for one transaction     | Model inputs (CRD section 8)                      | Documented by name               |
| **payment_outcomes**  | Authorisation result for one transaction | Success or failure and failure code               | Inferred                         |
| **customers**         | One payer                                | Payer attributes                                  | Inferred                         |
| **merchants**         | One merchant                             | Category and location                             | Inferred                         |
| **devices**           | One device fingerprint                   | Device type                                       | Inferred                         |
| **decision_audit**    | One simulated decision                   | Audit trail, latency, explanation (simulated)     | Documented (data card)           |
| **hard_rules**        | One policy rule                          | Rules that override the model                     | Confirmed by profile             |
| **threshold_sets**    | One set of risk thresholds               | Cut-offs for the risk bands                       | Confirmed by profile             |
| **list_entries**      | One list entry                           | Blocklist and allowlist entries                   | Confirmed by profile             |
| **config_changes**    | One configuration change                 | Log of rule and threshold changes                 | Confirmed by profile             |
| **reviewer_feedback** | One reviewer verdict                     | Analyst verdicts and corrected explanations       | Confirmed by profile             |
| **gold_explanations** | One reference explanation                | Training targets (8,000) and evaluation set (500) | Documented (manifest, data card) |
| **preference_pairs**  | One better-vs-worse explanation pair     | Preference tuning data (5,000)                    | Documented (manifest)            |
| **documents**         | One text document                        | Notes, narratives, playbooks, exercises           | Documented (manifest, data card) |
| **document_chunks**   | One chunk of a document                  | Text search and later embeddings                  | Documented (data card)           |
| **legacy_cases**      | One historical case (2021 to 2024)       | Legacy case archive                               | Documented (data card)           |

## 1.6 Beyond the tables: what the other folders add

*Described from the first file of each subfolder; all of it is fictional teaching data.*

- **histories (236.5 MB):** one record per transaction with its as_of time and a list of prior events (time, amount, channel, category, city, device). The as_of time equals the transaction time, so each history ends just before the payment it belongs to.

- **training (133.6 MB):** ready-made sets built from the tables. cpt holds document text; sft holds 201 files of prompts with fraud label, reason targets, explanation target, sample weight, token counts and label timing; gold and dpo repeat the gold and preference tables; format_comparison holds two prompt formats side by side with token counts.

- **parquet (45.2 MB):** a flat transactions view with 19 columns. It carries the CRD's 14 fields plus label_available_at, payment_channel, amount_paise, split and is_synthetic, and leaves out merchant_id.

- **corpus and documents:** corpus holds the source text as jsonl.gz with the same 14 fields as the documents table. The documents folder holds 1,525 markdown copies: 600 playbooks, 900 regulatory exercises, 4 guidelines, 1 RBA guide, and 10 each of investigator notes and chargeback narratives. Every file starts with a notice that it is fictional teaching material.

- **ground_truth (3.8 MB):** simulator records with event_number, scenario, split and use. The use field says generator_evaluation_only_never_model_input, and no transaction_id was seen, so the link to transactions is to confirm.

- **evaluation (84 KB):** the 500-case holdout explanation pack, with the same fields as gold_explanations. The prompts follow the CRD's \[TXN\], \[CUST\], \[CTX\] format.

- **sql (18.5 KB):** schema.sql builds the sentinel_demo schema with row-level security; indexes.sql adds indexes including full-text search on chunks; validate.sql lists checks whose violation counts must be zero, such as money consistency and a label delay of exactly 60 days; training_role_example.sql creates a training role limited to training views, so holdout stays unreadable.

- **Rules of use stated in the text:** four guidelines and one RBA guide say a decline is not a fraud label, labels are known 60 days after a transaction, pre-training text must be published before 1 November, the fraud score simulator is uncalibrated, and the hosted data is a teaching environment rather than the production design.
