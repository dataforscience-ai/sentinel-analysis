# Appendix A. Folder guide

| **Folder or file** | **Files** | **Size**     | **What it holds (from the first file of each subfolder)**                                                                                                                                                                           | **Notes**                                                                                        |
|--------------------|-----------|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| tables             | 1,170     | 322.6 MB     | The 18 tables as csv.gz parts of 5,000 rows                                                                                                                                                                                         | See sections 1.4 and 2                                                                           |
| histories          | 256       | 236.5 MB     | Per transaction: transaction_id, as_of, history (list of prior events: time, amount_paise, channel, mcc, city, device_id), split. Parts: train 181, validation 38, holdout 37                                                       | as_of equals the transaction time; one holdout part is stored as a folder named part-00036.jsonl |
| training           | 214       | 133.6 MB     | cpt 7 files (document_id, text, source_kind); sft 201 (prompt, fraud_label, reason_targets, explanation_target, sample_weight, token counts, label timing); gold 2; dpo 1; format_comparison 3 (prompt_v1, prompt_v2, token counts) | sft files 201 = 143 + 29 + 29, one per main part                                                 |
| parquet            | 45        | 45.2 MB      | transactions only: 19 columns including fraud_label and label_available_at                                                                                                                                                          | No merchant_id; rows not yet counted                                                             |
| corpus             | 18        | 6.8 MB       | jsonl.gz with the same 14 fields as the documents table: chargeback_narratives 5 files, investigator_notes 9, guidelines 1, playbooks 1, rba_guides 1, regulatory_exercises 1                                                       | Source of the documents table (storage_path points here)                                         |
| documents          | 1,525     | 2.8 MB       | Markdown copies: 600 playbooks, 900 regulatory exercises, 4 guidelines, 1 RBA guide, 10 investigator notes, 10 chargeback narratives                                                                                                | Each starts with a fictional-material notice                                                     |
| ground_truth       | 44        | 3.8 MB       | simulator parts: event_number, scenario, split, use                                                                                                                                                                                 | use says never model input; link to transactions unclear                                         |
| evaluation         | 1         | 84 KB        | explanations/holdout: the 500-case pack (example_id, transaction_id, prompt, target, fraud_label, review_status)                                                                                                                    | Same fields as gold_explanations                                                                 |
| sql                | 4         | 18.5 KB      | schema.sql, indexes.sql, validate.sql, training_role_example.sql                                                                                                                                                                    | validate.sql lists zero-violation checks                                                         |
| Loose files        | 10        | about 0.9 MB | DATA_CARD.md, data_dictionary.json, feature_catalogue.json, manifest.json, quality_report.json, requirements_coverage.json, reference_sources.json, rules_config.json, an Excel worksheet, reason code.docx (0 bytes)               | Sizes confirmed; feature_catalogue.json read to FE-03; three JSON files not yet read             |

*Totals: 3,287 files and about 752 MB, not counting the facts_tables output folder.*

# Appendix B. Evidence and limits

- DATA_CARD.md and data_dictionary.json were read from screenshots; 167 of 171 column types were read from the dictionary and 4 decision_audit columns from the profile.

- manifest.json counts came from a derived CSV; reviewer_feedback holdout and validation counts are confirmed by the profile.

- The sample profile covers all 18 tables, using the first part-file of each split.

- Folder descriptions come from the first file of each subfolder, not from whole-folder statistics.

- How each file was produced, and the limits of each method, is set out in section 6.1.

- Sample percentages come from 5,000 rows per split and are not whole-table values.

- Meanings marked inferred come from column names; FE-01 to FE-03 are confirmed against feature_catalogue.json, and the rest still need confirming.
