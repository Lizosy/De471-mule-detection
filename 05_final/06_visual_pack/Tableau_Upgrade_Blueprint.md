# Tableau Upgrade Blueprint (Same Data, Better Story)

This upgrade keeps the exact same source data and only improves visualization quality and rubric coverage.

- Base files (unchanged):
  - ../data/Transactions.csv
  - ../data/Account_Summary.csv
  - ../data/Layering_Detection_Rate.csv
- Derived marts (generated from base files):
  - ../data/viz_marts/kpi_overview.csv
  - ../data/viz_marts/channel_mix_pct.csv
  - ../data/viz_marts/hourly_profile.csv
  - ../data/viz_marts/layer_performance_extended.csv
  - ../data/viz_marts/risk_score_bins.csv
  - ../data/viz_marts/rule_trigger_matrix.csv
  - ../data/viz_marts/layer_flow_edges.csv
  - ../data/viz_marts/false_positive_review.csv
  - ../data/viz_marts/threshold_tradeoff_curve.csv

## Why this upgrade is stronger

1. Better rubric evidence: explicit metrics for recall, precision, false positive rate, and layer drop-off.
2. Better slide fit: each visual directly maps to a target slide and key message.
3. Better operations story: includes false-positive review and rule-trigger explainability.

## Visual Pack (recommended)

1. KPI Cards (Slide 6, 13, 14)
- Source: kpi_overview.csv
- Show: Total_Transactions, Total_Accounts, Mule_Transactions_Pct, Recall_at_Risk70_Pct, FPR_at_Risk70_Pct.
- Use large number cards with short subtitles.

2. Layer Detection Gap Bars (Slide 11)
- Source: layer_performance_extended.csv
- X: Layer
- Y: Detection_Rate_Pct
- Label: Detection_Rate_Pct and Gap_to_Target50_Pct.
- Insight: Layer3+ has largest miss rate and target gap.

3. Rule Trigger Heatmap (Slide 14)
- Source: rule_trigger_matrix.csv
- Rows: Rules_Triggered
- Columns: Is_Mule
- Color: COUNT(Account_ID)
- Tooltip: Avg Risk_Score and percentage within group.
- Insight: more rule hits concentrate heavily in mule accounts.

4. Risk Score Bin Distribution (Slide 14)
- Source: risk_score_bins.csv
- X: Risk_Bin
- Y: Account_Count
- Color: Is_Mule
- Mark: stacked bar.

5. Channel Mix 100% Bars (Slide 12)
- Source: channel_mix_pct.csv
- X: Channel
- Y: Within_Group_Pct
- Color: Is_Mule
- Mark: side-by-side or stacked normalized bars.

6. Hourly Behavior Profile (Slide 12)
- Source: hourly_profile.csv
- Option A: Heatmap (Hour x Is_Mule, color = Txn_Count)
- Option B: Line chart (Hour on X, Within_Group_Pct on Y, color = Is_Mule)

7. Layer Flow Edges (Slide 5 or 13)
- Source: layer_flow_edges.csv
- Mark: Sankey-like if available, otherwise directed edge table/bar by Source_Layer -> Target_Layer.
- Value: Txn_Count and Total_Amount.

8. False Positive Review Table (Slide 15 backup)
- Source: false_positive_review.csv
- Show top rows by Risk_Score.
- Purpose: show customer-experience trade-off control.

9. Threshold Trade-off Curve (Slide 15)
- Source: threshold_tradeoff_curve.csv
- X: Risk_Threshold
- Y: Recall_Pct and FPR_Pct (dual axis line) or two separate aligned lines.
- Add markers for threshold 70 and 60.
- Insight: current score is very conservative (very low FPR, low recall).

10. Keep Existing Core Charts (Slides 8, 9, 10)
- Keep your current fan-in boxplot, time-to-outflow, outflow-vs-fan-in scatter.
- Improve only formatting, labels, and filter behavior.

## Slide-to-Visual Mapping

- Slide 6: KPI Cards + Dataset overview
- Slide 8: Fan-in boxplot (existing)
- Slide 9: Time-to-outflow (existing, add threshold line at 15)
- Slide 10: Outflow vs Fan-in scatter (existing)
- Slide 11: Layer Detection Gap Bars (new mart)
- Slide 12: Channel Mix + Hourly Profile (new marts)
- Slide 13: KPI cards (recall/fpr) + layer flow summary
- Slide 14: Rule Trigger Heatmap + Risk Score Bins
- Slide 15: Threshold Trade-off Curve + False Positive Review Table

## Current calibration note (from same data)

- At threshold 70: Recall 16.34%, Precision 100%, FPR 0%.
- There is no threshold point that gives Recall >= 90% and FPR <= 5% simultaneously with current score logic.
- This is a good discussion point for Slide 15 (security/customer trade-off and next-step model tuning).

## Visual style standard

- Normal: #1f77b4
- Watch: #ff7f0e
- High Risk / Layer1: #d62728
- Layer2: #ff7f0e
- Layer3+: #ffbb78
- Victim / neutral: #7f7f7f

- Use one decimal for percentages in labels.
- Put one key insight sentence under every chart.
- Keep titles action-oriented, not generic.

## Build order in Tableau

1. Connect all CSV files in ../data/viz_marts/.
2. Build KPI and Layer visuals first.
3. Build Rule Trigger Heatmap and Risk Bin chart.
4. Create one dashboard page for operations (rules + false positive review).
5. Export PNG 1920x1080 for slides.
