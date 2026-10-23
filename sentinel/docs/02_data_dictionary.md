# Data dictionary: every attribute, its type, business meaning and observed values


Every attribute (171) is listed below, grouped by table. Types come from the schema. Meanings are taken from the client requirement document or the data card where stated, and otherwise inferred from names. The last column shows what the sample profile revealed.

## 2.1 customers

*Meanings for customer_age come from CRD 7.1; the other meanings are inferred from column names. Observed values: first part-file (5,000 of 25,000 rows).*

| **Attribute**     | **Type**          | **Business meaning**                             | **Observed in sample**                                                           |
|-------------------|-------------------|--------------------------------------------------|----------------------------------------------------------------------------------|
| **customer_id**  | text, primary key | Pseudonymised payer identifier (CRD)             | 5,000 distinct in sample                                                         |
| **created_at**   | timestamptz       | When the customer account was created (inferred) | 1,153 distinct values                                                            |
| **customer_age** | integer           | Payer age (CRD: from KYC)                        | 18 to 80, mean 49.3                                                              |
| **home_city**    | text              | Payer's home city (inferred)                     | 16 distinct cities                                                               |
| **region**        | text              | Region of the payer (inferred)                   | 6 values: south 25%, east 25%, north 19%, west 18%, northeast 6.5%, central 6.1% |
| **is_synthetic** | boolean           | Marks generated (fictional) data                 | True for all rows                                                                |

## 2.2 merchants

*Meanings from CRD 7.1 where noted, otherwise inferred. Observed values: all 2,000 rows.*

| **Attribute**          | **Type**          | **Business meaning**               | **Observed in sample**            |
|------------------------|-------------------|------------------------------------|-----------------------------------|
| **merchant_id**       | text, primary key | Merchant identifier                | 2,000 distinct                    |
| **synthetic_name**    | text              | Fictional merchant name            | 2,000 distinct                    |
| **merchant_category** | text              | MCC group (CRD)                    | 10 categories, 200 merchants each |
| **merchant_location** | jsonb             | Registered merchant location (CRD) | 16 distinct locations             |
| **is_synthetic**      | boolean           | Marks generated data               | True for all rows                 |

## 2.3 devices

*Inferred from column names. Observed values: first part-file (5,000 of 100,120 rows).*

| **Attribute**     | **Type**          | **Business meaning**            | **Observed in sample**   |
|-------------------|-------------------|---------------------------------|--------------------------|
| **device_id**    | text, primary key | Hashed device fingerprint (CRD) | 5,000 distinct in sample |
| **device_kind**  | text              | Type of device                  | mobile 75%, browser 25%  |
| **is_synthetic** | boolean           | Marks generated data            | True for all rows        |

## 2.4 transactions

*Meanings from CRD 7.1 unless marked inferred. Observed values: first part-file of each split (5,000 rows each), four samples.*

| **Attribute**                   | **Type**                      | **Business meaning**                                        | **Observed in sample**                                                              |
|---------------------------------|-------------------------------|-------------------------------------------------------------|-------------------------------------------------------------------------------------|
| **transaction_id**             | text, primary key             | Unique transaction reference (CRD)                          | Unique in every sample                                                              |
| **customer_id**                | text, FK to customers         | Pseudonymised payer (CRD)                                   | 2,544 to 2,705 distinct per 5,000 rows                                              |
| **merchant_id**                | text, FK to merchants         | Merchant being paid (inferred)                              | 1,372 to 1,384 distinct of 2,000                                                    |
| **device_id**                  | text, nullable, FK to devices | Device fingerprint (CRD)                                    | Missing: 0.3% (holdout, validation), 1.7% (train), 1.8% (warm-up)                   |
| **amount_paise**               | bigint, must be \> 0          | Amount in paise; authoritative (data card)                  | Minimum about Rs 22 to 27; maximum Rs 5.8 lakh (warm-up) to Rs 69 lakh (validation) |
| **transaction_amount**         | numeric(14,2)                 | Amount in rupees (CRD)                                      | Equals amount_paise / 100 in all four samples; mean Rs 3,337 to 5,364               |
| **payment_channel**            | text                          | Payment method (inferred)                                   | UPI 56 to 59%, card 31 to 33%, wallet 6 to 7%, net banking 4 to 5%                  |
| **merchant_category**          | text                          | MCC group (CRD)                                             | 10 values; grocery most common (about 18%)                                          |
| **transaction_time**           | timestamptz                   | Authorisation request time (CRD); stored in UTC (data card) | All distinct in sample                                                              |
| **customer_age**               | integer                       | Payer age (CRD)                                             | 18 to 80, mean 49 to 50                                                             |
| **customer_location**          | jsonb, nullable               | Payer location at transaction time (CRD)                    | Missing 2.7 to 3.0%; 16 distinct values                                             |
| **merchant_location**          | jsonb                         | Merchant location (CRD)                                     | 16 distinct; none missing                                                           |
| **account_age**                | integer (days)                | Days since account creation (CRD)                           | 0 to 2,193; mean rises 592 (warm-up), 698 (train), 882 (validation), 923 (holdout)  |
| **previous_transactions**      | integer                       | Payer's transactions in the last 30 days (CRD)              | 0 to 25; mean rises 1.4 (warm-up), 2.8 (train), 4.4 (validation), 4.1 (holdout)     |
| **average_transaction_value** | numeric(14,2), nullable       | Payer's mean transaction value over 90 days (CRD)           | Missing 0.5 to 0.6% (validation, holdout), 4.2% (train), 51.6% (warm-up)            |
| **failed_transactions**        | integer                       | Payer's failed attempts in the last 24 hours (CRD)          | 0 to 8, mean 0.44 to 0.56; 3 or more in 9.5 to 12.1% of rows                        |
| **split**                       | text                          | Time split the row belongs to (data card)                   | One value per folder                                                                |
| **is_synthetic**               | boolean                       | Marks generated data                                        | True for all rows                                                                   |

## 2.5 payment_outcomes

*Meanings inferred from column names and the data card. Observed values: first part-file of each split.*

| **Attribute**       | **Type**                              | **Business meaning**                                   | **Observed in sample**                                           |
|---------------------|---------------------------------------|--------------------------------------------------------|------------------------------------------------------------------|
| **transaction_id** | text, primary key, FK to transactions | One outcome per transaction                            | 5,000 distinct per sample (one-to-one)                           |
| **outcome_time**   | timestamptz                           | When the authorisation outcome was recorded (inferred) | All distinct                                                     |
| **status**          | text                                  | Result of the attempt                                  | SUCCESS or FAILED; FAILED is 11 to 13% (565 to 672 of 5,000)     |
| **failure_code**   | text, nullable                        | Reason for a failed attempt                            | Only value is SIMULATED_AUTH_FAILURE; empty exactly when SUCCESS |
| **is_synthetic**   | boolean                               | Marks generated data                                   | True for all rows                                                |

## 2.6 labels

*Meanings from CRD 7 and the data card unless marked inferred. Observed values: first part-file of each split.*

| **Attribute**                        | **Type**                              | **Business meaning**                                                                                     | **Observed in sample**                                                                                                                                |
|--------------------------------------|---------------------------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| **transaction_id**                  | text, primary key, FK to transactions | One label per transaction                                                                                | 5,000 distinct per sample (one-to-one)                                                                                                                |
| **fraud_label**                     | smallint, 0 or 1                      | 1 = confirmed fraud, 0 = genuine (CRD)                                                                   | Fraud 30 to 46 per 5,000 (0.60 to 0.92%)                                                                                                              |
| **label_source**                    | text                                  | How the label was decided (inferred)                                                                     | mature_no_fraud (about 99%), investigator_verdict, confirmed_chargeback; fraud labels are about 70 to 83% investigator verdicts, the rest chargebacks |
| **label_available_at**             | timestamptz                           | When the label became known (data card: labels mature after 60 days)                                     | All distinct                                                                                                                                          |
| **split**                            | text                                  | Time split                                                                                               | One value per folder                                                                                                                                  |
| **eligible_at_next_split_start** | boolean                               | True if the label was known when the next split starts (data card: filter on True for strict simulation) | All True in train, holdout and warm-up samples; validation 2,903 True and 2,097 False                                                                 |
| **is_synthetic**                    | boolean                               | Marks generated data                                                                                     | True for all rows                                                                                                                                     |

## 2.7 features

*FE numbers refer to CRD section 8. FE-01 to FE-03 definitions are confirmed from feature_catalogue.json (read as far as FE-03); other meanings are inferred. Observed values: first part-file of each split.*

| **Attribute**                            | **Type**                              | **Business meaning**                                                                                              | **Observed in sample**                                                                                                    |
|------------------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **transaction_id**                      | text, primary key, FK to transactions | One feature row per transaction                                                                                   | 5,000 distinct per sample                                                                                                 |
| **feature_as_of**                      | timestamptz                           | Time as of which the features were computed (inferred)                                                            | All distinct                                                                                                              |
| **amount_to_avg_ratio**               | double precision, nullable            | FE-01: current amount divided by the mean of the payer's preceding 90-day authorisations (feature catalogue)      | 0.0002 to 9,838; mean 2.1 to 4.9; missing 0.5 to 0.6% (validation, holdout), 4.2% (train), 51.6% (warm-up)                |
| **is_new_device**                      | boolean, nullable                     | FE-02: observed device absent from the payer's prior 90 days; null when the device is missing (feature catalogue) | True 4.7 to 5.1% (validation, holdout), 8.7% (train), 51.6% (warm-up); missing when device is missing                     |
| **customer_merchant_distance_km**     | double precision, nullable            | FE-03: Haversine distance between payer and merchant (feature catalogue)                                          | 0 to 2,429 km, mean about 1,050; only 121 distinct values; missing when location is missing                               |
| **is_new_city**                        | boolean, nullable                     | FE-03: city absent from the payer's preceding 90 days (feature catalogue)                                         | True 4.9 to 8.7% (train, validation, holdout), 51% (warm-up)                                                              |
| **hour_of_day**                        | integer                               | FE-04: hour of the transaction (night features use IST per data card)                                             | 0 to 23, mean 11 to 12                                                                                                    |
| **is_night**                            | boolean                               | FE-04: night-time flag                                                                                            | True 16.5 to 21.8%                                                                                                        |
| **has_recent_failures**                | boolean                               | FE-05: 3 or more recent failed attempts                                                                           | True 9.5 to 12.1%; equals failed_transactions of 3 or more in all four samples                                            |
| **is_new_account**                     | boolean                               | FE-06: account younger than 30 days (CRD)                                                                         | True 0.2 to 1.4%                                                                                                          |
| **txn_count_last_1h**                 | integer                               | FE-07: transactions in the last hour                                                                              | 0 to 9; zero in 54 to 57% of rows                                                                                         |
| **txn_amount_last_24h_paise**        | bigint                                | FE-07: amount transacted in the last 24 hours, in paise                                                           | 0 to about 6.9 x 10^8 paise                                                                                               |
| **distinct_customers_per_device_7d** | double precision, nullable            | FE-09: customers using the same device in 7 days                                                                  | 0 to 7; missing when device is missing (0.3 to 1.8%)                                                                      |
| **combined_risk_flags**                | integer                               | FE-10: count of risk flags that are true                                                                          | 0 to 4; mean 1.1 to 1.7                                                                                                   |
| **mcc_target_encoded_rate**           | double precision                      | FE-08: historical fraud rate of the merchant category                                                             | Validation and holdout: 10 values from 0.016% (travel) to 2.65% (gift_cards); train and warm-up samples: constant 0.006   |
| **mcc_encoding_as_of**                | timestamptz                           | Date the category rates were fitted (inferred)                                                                    | Validation and holdout: 1 Nov 2025 IST (frozen encoder, matches data card); train sample: 1 Jan 2025; warm-up: 1 Oct 2024 |
| **mcc_encoding_count**                 | integer                               | Number of labelled events behind the category rate (inferred)                                                     | 28,503 to 105,167 (validation, holdout); 0 in train and warm-up samples                                                   |
| **missing_customer_location**          | boolean                               | Flag: payer location missing                                                                                      | True 2.7 to 3.0%                                                                                                          |
| **missing_device**                      | boolean                               | Flag: device missing                                                                                              | True 0.3% (validation, holdout), 1.7% (train), 1.8% (warm-up)                                                             |
| **cold_start**                          | boolean                               | Flag: payer has no usable history (inferred)                                                                      | True 0.5 to 0.6% (validation, holdout), 4.2% (train), 51.6% (warm-up)                                                     |
| **reason_codes**                        | jsonb                                 | Pre-computed reason codes for the transaction (inferred; derivation unknown)                                      | 54 to 71 distinct combinations per sample                                                                                 |
| **feature_version**                     | text                                  | Version of the feature definitions                                                                                | sentinel-features-1.0.0 in all rows                                                                                       |

## 2.8 legacy_cases

*Data card: separate legacy case archive of 2021 to 2024 narratives. All 2,000 rows profiled.*

| **Attribute**         | **Type**              | **Business meaning**                   | **Observed in sample**                                                                                                            |
|-----------------------|-----------------------|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| **legacy_case_id**  | text, primary key     | Identifier of a historical case        | 2,000 distinct                                                                                                                    |
| **customer_id**      | text, FK to customers | Customer involved                      | 2,000 distinct: one case per customer                                                                                             |
| **transaction_time** | timestamptz           | When the original transaction happened | 964 distinct values                                                                                                               |
| **closed_at**        | timestamptz           | When the case was closed               | 964 distinct values                                                                                                               |
| **amount_paise**     | bigint                | Amount in paise                        | 5,949 to 2,998,400 (Rs 59 to Rs 29,984); mean about Rs 14,650                                                                     |
| **payment_channel**  | text                  | Payment method                         | Exactly 500 each: UPI, card, wallet, net_banking                                                                                  |
| **fraud_label**      | smallint              | Outcome of the case                    | Fraud 535 (26.8%), genuine 1,465                                                                                                  |
| **evidence**          | jsonb                 | Evidence recorded for the case         | Source synthetic_archived_snapshot; history_not_reconstructed true; 1,333 list R05_AMOUNT_SPIKE and R01_NEW_DEVICE, 667 list none |
| **is_synthetic**     | boolean               | Marks generated data                   | True for all rows                                                                                                                 |

## 2.9 documents

*Column meanings partly inferred. First part-file: holdout 3,264 of 3,908 rows, train 3,279 of 30,879, validation 3,258 of 4,219.*

| **Attribute**         | **Type**                           | **Business meaning**                                                                       | **Observed in sample**                                                                                                                                                                |
|-----------------------|------------------------------------|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **document_id**      | text, primary key                  | Document identifier                                                                        | Unique per row                                                                                                                                                                        |
| **kind**              | text                               | Type of document                                                                           | Train: investigator_notes 1,774, regulatory_exercises 900, playbooks 600, guidelines 4, rba_guides 1. Validation and holdout: about 70% investigator_notes, 30% chargeback_narratives |
| **title**             | text                               | Document title                                                                             | Unique per row                                                                                                                                                                        |
| **transaction_id**   | text, nullable, FK to transactions | Transaction the document is about                                                          | Filled for validation and holdout; 100% empty in the train sample                                                                                                                     |
| **legacy_case_id**  | text, nullable, FK to legacy_cases | Legacy case the document is about                                                          | Train: 1,774 distinct (notes link to legacy cases), 45.9% empty; 100% empty in validation and holdout                                                                                 |
| **split**             | text                               | Time split                                                                                 | One value per folder                                                                                                                                                                  |
| **published_at**     | timestamptz                        | Publication time (data card: late-published training notes are excluded from pre-training) | Between 1,798 and 3,015 distinct values                                                                                                                                               |
| **content**           | text                               | Full document text                                                                         | Unique per row                                                                                                                                                                        |
| **content_sha256**   | text                               | Hash used to find exact duplicates (data card)                                             | Unique per row: no exact duplicates in sample                                                                                                                                         |
| **template_family**  | text                               | Template the fiction came from                                                             | 36 (holdout), 40 (validation), 425 (train) distinct                                                                                                                                   |
| **cpt_eligible**     | boolean                            | Allowed for continued pre-training                                                         | True for all train rows; False for all validation and holdout rows (matches data card)                                                                                                |
| **review_status**    | text                               | Review state                                                                               | synthetic_candidate_not_human_reviewed in all rows                                                                                                                                    |
| **storage_path**     | text                               | Location of the source file                                                                | Points to corpus/\<kind\>/\<split\>/part-00001.jsonl.gz, linking this table to the corpus folder                                                                                      |
| **record_in_shard** | integer                            | Position of the record inside its file                                                     | 1 to 2,272                                                                                                                                                                            |
| **metadata**          | jsonb                              | Extra attributes                                                                           | Mostly distinct values                                                                                                                                                                |
| **is_synthetic**     | boolean                            | Marks generated data                                                                       | True for all rows                                                                                                                                                                     |

## 2.10 document_chunks

*Data card: supports text search and later local embeddings. First part-file: 5,000 rows per split (of 7,816 holdout, 61,753 train, 8,438 validation).*

| **Attribute**     | **Type**              | **Business meaning**                      | **Observed in sample**                                              |
|-------------------|-----------------------|-------------------------------------------|---------------------------------------------------------------------|
| **chunk_id**     | text, primary key     | Chunk identifier                          | Unique per row                                                      |
| **document_id**  | text, FK to documents | Parent document                           | About 2,500 distinct per 5,000 chunks: two chunks per document      |
| **chunk_index**  | integer               | Position of the chunk inside the document | 0 or 1 only                                                         |
| **content**       | text                  | Chunk text                                | Only about 2,530 distinct texts per 5,000 chunks: about half repeat |
| **word_count**   | integer               | Words in the chunk                        | 55 to 220; mean 145 to 152                                          |
| **split**         | text                  | Time split                                | One value per folder                                                |
| **cpt_eligible** | boolean               | Allowed for continued pre-training        | True for train; False for validation and holdout                    |
| **is_synthetic** | boolean               | Marks generated data                      | True for all rows                                                   |

## 2.11 gold_explanations

*Manifest: 8,000 gold plus 500 evaluation cases. First part-file: holdout 500 (all rows), train 5,000 of 8,000.*

| **Attribute**       | **Type**                 | **Business meaning**                     | **Observed in sample**                                      |
|---------------------|--------------------------|------------------------------------------|-------------------------------------------------------------|
| **example_id**     | text, primary key        | Example identifier                       | Unique per row                                              |
| **transaction_id** | text, FK to transactions | Transaction being explained              | Unique per row                                              |
| **split**           | text                     | Time split (train or holdout)            | One value per folder                                        |
| **prompt**          | text                     | Model input text for the case            | Unique per row                                              |
| **target**          | jsonb                    | Reference explanation in structured form | Only 35 (holdout) and 56 (train) distinct values: templated |
| **fraud_label**    | smallint                 | Fraud label for the case                 | About 40% fraud (200 of 500 holdout; 1,972 of 5,000 train)  |
| **review_status**  | text                     | Review state                             | synthetic_candidate_not_human_reviewed in all rows          |
| **is_synthetic**   | boolean                  | Marks generated data                     | True for all rows                                           |

## 2.12 preference_pairs

*Manifest: 5,000 pairs; train only. First part-file holds all 5,000.*

| **Attribute**         | **Type**                 | **Business meaning**                    | **Observed in sample**                                     |
|-----------------------|--------------------------|-----------------------------------------|------------------------------------------------------------|
| **pair_id**          | text, primary key        | Pair identifier                         | Unique per row                                             |
| **transaction_id**   | text, FK to transactions | Transaction the pair is about           | Unique per row                                             |
| **split**             | text                     | Time split                              | train in all rows                                          |
| **prompt**            | text                     | Model input text                        | Unique per row                                             |
| **chosen**            | jsonb                    | Preferred explanation                   | 55 distinct values                                         |
| **rejected**          | jsonb                    | Less preferred explanation              | 198 distinct values                                        |
| **rejection_reason** | text                     | Why the second explanation was rejected | One value in all rows: unsupported fact absent from prompt |
| **review_status**    | text                     | Review state                            | synthetic_candidate_not_human_reviewed in all rows         |
| **is_synthetic**     | boolean                  | Marks generated data                    | True for all rows                                          |

## 2.13 decision_audit

*Data card: all probabilities, latencies and decisions are simulated; model_version says SYNTHETIC-HEURISTIC-NOT-A-MODEL. First part-file per split (5,000 rows each). The first four columns were identified from the profile; their schema types were not seen.*

| **Attribute**                | **Type**                    | **Business meaning**                                       | **Observed in sample**                                                           |
|------------------------------|-----------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------|
| **transaction_id**          | text (schema not seen)      | Transaction that was scored                                | 5,000 distinct per sample; foreign key to transactions TO CONFIRM                |
| **scored_at**               | timestamp (schema not seen) | When the simulated decision was made                       | All distinct                                                                     |
| **fraud_probability**       | number (schema not seen)    | Simulated fraud score; never used as the label (data card) | 0.007 to 0.87; mean 0.063 to 0.074                                               |
| **decision**                 | text (schema not seen)      | ALLOW, REVIEW or BLOCK                                     | Holdout: 4,882 / 80 / 38; train: 4,922 / 65 / 13; validation: 4,923 / 59 / 18    |
| **risk_level**              | text                        | Risk band of the decision                                  | LOW 4,549 to 4,663, MEDIUM 271 to 369, HIGH 61 to 82; one CRITICAL in validation |
| **reason_codes**            | jsonb                       | Reason codes attached to the decision                      | 46 to 54 distinct combinations                                                   |
| **explanation**              | text                        | Explanation text of the decision                           | 46 to 54 distinct texts: one per reason-code combination (templated)             |
| **decision_source**         | text                        | Whether a model or a rule produced the decision (CRD 10.3) | MODEL 4,962 to 4,987; HARD_RULE 13 to 38                                         |
| **model_version**           | text                        | Model version label (simulated)                            | SYNTHETIC-HEURISTIC-NOT-A-MODEL-v1 in all rows                                   |
| **rules_version**           | text                        | Version of the rules in force                              | synthetic-rules-1 in all rows                                                    |
| **latency_ms**              | integer                     | Simulated decision latency                                 | 20 to 220 ms; mean about 119 to 120                                              |
| **explanation_latency_ms** | integer                     | Simulated explanation latency                              | 26 to 1,715 ms; mean about 860 to 870                                            |
| **prompt_format**           | text                        | Prompt format version                                      | fmt-v1 in all rows                                                               |
| **prompt_hash**             | text                        | Hash of the prompt                                         | All distinct                                                                     |
| **request**                  | jsonb                       | Request payload                                            | All distinct                                                                     |
| **feature_vector**          | jsonb                       | Features used for the decision                             | All distinct                                                                     |
| **split**                    | text                        | Time split                                                 | One value per folder                                                             |
| **is_synthetic**            | boolean                     | Marks generated data                                       | True for all rows                                                                |

## 2.14 threshold_sets

*The single row profiled. Matches the CRD 10.4 initial bands exactly.*

| **Attribute**      | **Type**          | **Business meaning**                            | **Observed in sample**           |
|--------------------|-------------------|-------------------------------------------------|----------------------------------|
| **threshold_id**  | text, primary key | Identifier of a threshold set                   | THR_DEFAULT_V1                   |
| **version**        | integer           | Version number                                  | 1                                |
| **mcc_group**     | text, nullable    | Merchant category group the thresholds apply to | Empty: applies to all categories |
| **medium_from**   | numeric(4,3)      | Score from which risk is MEDIUM                 | 0.30                             |
| **high_from**     | numeric(4,3)      | Score from which risk is HIGH                   | 0.60                             |
| **critical_from** | numeric(4,3)      | Score from which risk is CRITICAL               | 0.85                             |
| **status**         | text              | Whether the set is active                       | active_synthetic                 |
| **is_synthetic**  | boolean           | Marks generated data                            | True                             |

## 2.15 hard_rules

*Both rows profiled. Matches CRD FR-RE-02 (hard rules override the model) and FR-RE-03.*

| **Attribute**     | **Type**          | **Business meaning**            | **Observed in sample**                                             |
|-------------------|-------------------|---------------------------------|--------------------------------------------------------------------|
| **rule_id**      | text, primary key | Rule identifier                 | HR_BLOCKLIST_DEVICE, HR_ALLOWLIST_CUSTOMER                         |
| **code**          | text              | Short rule code                 | Same as rule_id                                                    |
| **expression**    | jsonb             | Condition the rule tests        | device_id in blocked_devices; customer_id in allowlisted_customers |
| **action**        | text              | Decision forced by the rule     | BLOCK; CAP_AT_REVIEW                                               |
| **priority**      | integer           | Order of evaluation             | 100 (blocklist); 10 (allowlist)                                    |
| **enabled**       | boolean           | Whether the rule is switched on | True for both                                                      |
| **is_synthetic** | boolean           | Marks generated data            | True for both                                                      |

## 2.16 list_entries

*All 137 rows profiled. Matches CRD FR-RE-02 and FR-RE-03 (blocklist and allowlist).*

| **Attribute**       | **Type**          | **Business meaning**            | **Observed in sample**                        |
|---------------------|-------------------|---------------------------------|-----------------------------------------------|
| **entry_id**       | text, primary key | Entry identifier                | 137 distinct                                  |
| **list_type**      | text              | Which list the entry belongs to | allowlisted_customers 125, blocked_devices 12 |
| **entity_id**      | text              | Customer or device on the list  | 137 distinct                                  |
| **effective_from** | timestamptz       | When the entry took effect      | All 1 Jan 2025 IST (31 Dec 2024 18:30 UTC)    |
| **reason**          | text              | Why the entry was added         | fictional seeded policy fixture in all rows   |
| **is_synthetic**   | boolean           | Marks generated data            | True for all rows                             |

## 2.17 config_changes

*The single row profiled. Matches CRD FR-RE-01 (every change is logged).*

| **Attribute**     | **Type**          | **Business meaning**    | **Observed in sample**                 |
|-------------------|-------------------|-------------------------|----------------------------------------|
| **change_id**    | text, primary key | Change identifier       | CHANGE_0001                            |
| **entity**        | text              | Kind of object changed  | threshold_sets                         |
| **entity_id**    | text              | Which object changed    | THR_DEFAULT_V1                         |
| **before_value** | jsonb, nullable   | Value before the change | Empty (initial setting)                |
| **after_value**  | jsonb             | Value after the change  | medium 0.3, high 0.6, critical 0.85    |
| **changed_by**   | text              | Who made the change     | SYNTHETIC_ADMIN                        |
| **changed_at**   | timestamptz       | When it was made        | 1 Jan 2025 IST (31 Dec 2024 18:30 UTC) |
| **reason**        | text              | Why it was made         | Initial CRD teaching thresholds        |
| **is_synthetic** | boolean           | Marks generated data    | True                                   |

## 2.18 reviewer_feedback

*Meanings inferred. Row counts confirmed by the profile for holdout (2,708) and validation (2,907); the train total of 13,761 comes from the manifest (first part 5,000).*

| **Attribute**              | **Type**                 | **Business meaning**             | **Observed in sample**                                                                                     |
|----------------------------|--------------------------|----------------------------------|------------------------------------------------------------------------------------------------------------|
| **feedback_id**           | text, primary key        | Feedback identifier              | Unique per row                                                                                             |
| **transaction_id**        | text, FK to transactions | Transaction reviewed             | Unique per row: one review per transaction                                                                 |
| **reviewed_at**           | timestamptz              | When the review happened         | All distinct                                                                                               |
| **verdict**                | text                     | Reviewer's decision              | GENUINE or FRAUD; FRAUD is 25 to 26% (684 of 2,708 holdout; 1,256 of 5,000 train; 766 of 2,907 validation) |
| **corrected_explanation** | text                     | Reviewer's corrected explanation | 43 to 52 distinct texts (templated)                                                                        |
| **reviewer_id**           | text                     | Reviewer identifier              | 46 distinct reviewers                                                                                      |
| **is_synthetic**          | boolean                  | Marks generated data             | True for all rows                                                                                          |
