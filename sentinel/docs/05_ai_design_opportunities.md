# AI system design opportunities (understanding stage, no model selection)

This stage is understanding and discussion, not model selection or implementation.

## 5.1 Inputs, targets and excluded columns

| **Role**             | **Columns**                                                                                                                                                                                                                                | **Reason**                                                     |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| Prediction target    | labels.fraud_label                                                                                                                                                                                                                         | Binary fraud outcome (CRD objectives 1 to 4)                   |
| Second target (text) | gold_explanations.target                                                                                                                                                                                                                   | Reference explanations                                         |
| Candidate inputs     | transactions fields known at payment time; the engineered columns in features                                                                                                                                                              | Available before the decision (CRD FR-FE-01)                   |
| Must not be inputs   | labels.label_source, label_available_at, eligible_at_next_split_start; payment_outcomes; decision_audit; reviewer_feedback; later verdicts; ground_truth (scenario, use); scenario IDs; is_synthetic; split; identifiers; source documents | They reveal the answer or happen after the payment (data card) |
| Check before use     | features.reason_codes                                                                                                                                                                                                                      | Derivation unknown; may encode the answer                      |

## 5.2 Preprocessing steps

- Convert types: nullable booleans, UTC text to IST timestamps, jsonb locations to city fields.

- Handle missing values using the existing flags (missing_device, missing_customer_location, cold_start).

- Transform skewed amounts and ratios, for example with logarithms or caps.

- Encode categories such as merchant_category, payment_channel, device_kind and region.

- Use time-based splits only, treat warm-up separately, and filter on label eligibility for strict simulation.

- Handle the 0.6% imbalance and check calibration of scores.

- Check text tables for personal data and exact duplicates before use.

## 5.3 Feature engineering opportunities

- Customer history windows beyond the ten given: the histories folder lists each transaction's prior events (time, amount, channel, category, city, device), so new windows and novelty measures can be built.

- Interactions such as new device with night-time and an amount spike (combined_risk_flags is a simple start).

- Device and customer graph features for fraud rings (distinct_customers_per_device_7d is the first step).

- Merchant-level history, not only category-level rates.

- Geography beyond distance: only 121 distinct distance values suggest city-to-city distances, so finer location data may help (inferred).

## 5.4 Relevant approaches (concept level)

- Supervised classification on tabular features to produce a risk score, followed by calibration so a score behaves like a probability.

- Text generation limited to facts in the input, to explain decisions, using the gold and preference data.

- Retrieval over document chunks to ground explanations in playbooks and cases (the data card says chunks support later embedding).

- A rules and thresholds layer that can override scores, using the rule tables.

- Anomaly and network analysis for rings of customers sharing devices.

- Drift monitoring as patterns change over time.

## 5.5 Real-time versus batch

- **Real time:** scoring one payment needs the payer's recent history and velocity counts at the moment of payment, then thresholds and rules; the features table shows what must be computed.

- **Batch:** training, evaluation on the sealed holdout, calibration, monitoring for drift, label maturation after 60 days, and loading reviewer feedback.
