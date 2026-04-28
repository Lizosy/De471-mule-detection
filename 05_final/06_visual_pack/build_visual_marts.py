"""Build visualization marts from existing final-project CSV files.

This script does not create synthetic records.
It only derives analysis-ready tables from existing data.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = DATA_DIR / "viz_marts"

TRANSACTIONS_PATH = DATA_DIR / "Transactions.csv"
ACCOUNT_SUMMARY_PATH = DATA_DIR / "Account_Summary.csv"
LAYER_RATE_PATH = DATA_DIR / "Layering_Detection_Rate.csv"


@dataclass
class SummaryRow:
    account_id: str
    layer: str
    risk_score: int
    is_mule: int
    account_age_days: int
    fan_in: int
    fan_out: int
    outflow_ratio_pct: float
    avg_time_to_outflow_min: float



def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default



def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default



def load_transactions(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))



def load_account_summary(path: Path) -> list[SummaryRow]:
    rows: list[SummaryRow] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(
                SummaryRow(
                    account_id=r.get("Account_ID", ""),
                    layer=r.get("Layer", ""),
                    risk_score=parse_int(r.get("Risk_Score", "0")),
                    is_mule=parse_int(r.get("Is_Mule", "0")),
                    account_age_days=parse_int(r.get("Account_Age_Days", "0")),
                    fan_in=parse_int(r.get("Fan_In_Count", "0")),
                    fan_out=parse_int(r.get("Fan_Out_Count", "0")),
                    outflow_ratio_pct=parse_float(r.get("Outflow_Ratio_Pct", "0")),
                    avg_time_to_outflow_min=parse_float(
                        r.get("Avg_Time_To_Outflow_Min", "0")
                    ),
                )
            )
    return rows



def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)



def build_kpi_overview(transactions: list[dict[str, str]], summary: list[SummaryRow]) -> None:
    total_txn = len(transactions)
    mule_txn = sum(parse_int(t.get("Is_Mule", "0")) for t in transactions)

    total_acc = len(summary)
    mule_acc = sum(r.is_mule for r in summary)

    predicted_positive = [r for r in summary if r.risk_score >= 70]
    predicted_negative = [r for r in summary if r.risk_score < 70]

    tp = sum(1 for r in predicted_positive if r.is_mule == 1)
    fp = sum(1 for r in predicted_positive if r.is_mule == 0)
    fn = sum(1 for r in predicted_negative if r.is_mule == 1)
    tn = sum(1 for r in predicted_negative if r.is_mule == 0)

    recall = (tp / (tp + fn) * 100) if (tp + fn) else 0.0
    precision = (tp / (tp + fp) * 100) if (tp + fp) else 0.0
    fpr = (fp / (fp + tn) * 100) if (fp + tn) else 0.0

    rows = [
        {
            "Metric": "Total_Transactions",
            "Value": total_txn,
            "Format": "number",
        },
        {
            "Metric": "Total_Accounts",
            "Value": total_acc,
            "Format": "number",
        },
        {
            "Metric": "Mule_Transactions_Pct",
            "Value": round((mule_txn / total_txn * 100) if total_txn else 0.0, 2),
            "Format": "percent",
        },
        {
            "Metric": "Mule_Accounts_Pct",
            "Value": round((mule_acc / total_acc * 100) if total_acc else 0.0, 2),
            "Format": "percent",
        },
        {
            "Metric": "Recall_at_Risk70_Pct",
            "Value": round(recall, 2),
            "Format": "percent",
        },
        {
            "Metric": "Precision_at_Risk70_Pct",
            "Value": round(precision, 2),
            "Format": "percent",
        },
        {
            "Metric": "FPR_at_Risk70_Pct",
            "Value": round(fpr, 2),
            "Format": "percent",
        },
        {
            "Metric": "ConfusionMatrix_TP",
            "Value": tp,
            "Format": "number",
        },
        {
            "Metric": "ConfusionMatrix_FP",
            "Value": fp,
            "Format": "number",
        },
        {
            "Metric": "ConfusionMatrix_FN",
            "Value": fn,
            "Format": "number",
        },
        {
            "Metric": "ConfusionMatrix_TN",
            "Value": tn,
            "Format": "number",
        },
    ]

    write_csv(
        OUT_DIR / "kpi_overview.csv",
        ["Metric", "Value", "Format"],
        rows,
    )



def build_hourly_profile(transactions: list[dict[str, str]]) -> None:
    counts: dict[tuple[int, int], int] = defaultdict(int)
    for t in transactions:
        ts = t.get("Timestamp", "")
        try:
            hour = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").hour
        except ValueError:
            continue
        is_mule = parse_int(t.get("Is_Mule", "0"))
        counts[(hour, is_mule)] += 1

    rows: list[dict[str, object]] = []
    totals_by_group = defaultdict(int)
    for (hour, is_mule), cnt in counts.items():
        totals_by_group[is_mule] += cnt

    for hour in range(24):
        for is_mule in (0, 1):
            cnt = counts.get((hour, is_mule), 0)
            grp_total = totals_by_group[is_mule]
            pct = (cnt / grp_total * 100) if grp_total else 0.0
            rows.append(
                {
                    "Hour": hour,
                    "Is_Mule": is_mule,
                    "Txn_Count": cnt,
                    "Within_Group_Pct": round(pct, 2),
                    "Time_Band": "Night_22_06" if hour >= 22 or hour <= 6 else "Day_07_21",
                }
            )

    write_csv(
        OUT_DIR / "hourly_profile.csv",
        ["Hour", "Is_Mule", "Txn_Count", "Within_Group_Pct", "Time_Band"],
        rows,
    )



def build_channel_mix(transactions: list[dict[str, str]]) -> None:
    counts: dict[tuple[str, int], int] = defaultdict(int)
    totals = defaultdict(int)

    for t in transactions:
        channel = (t.get("Channel", "") or "Unknown").strip()
        is_mule = parse_int(t.get("Is_Mule", "0"))
        counts[(channel, is_mule)] += 1
        totals[is_mule] += 1

    channels = sorted({c for c, _ in counts.keys()})
    rows: list[dict[str, object]] = []
    for channel in channels:
        for is_mule in (0, 1):
            cnt = counts.get((channel, is_mule), 0)
            total = totals[is_mule]
            pct = (cnt / total * 100) if total else 0.0
            rows.append(
                {
                    "Channel": channel,
                    "Is_Mule": is_mule,
                    "Txn_Count": cnt,
                    "Within_Group_Pct": round(pct, 2),
                }
            )

    write_csv(
        OUT_DIR / "channel_mix_pct.csv",
        ["Channel", "Is_Mule", "Txn_Count", "Within_Group_Pct"],
        rows,
    )



def build_rule_trigger_matrix(summary: list[SummaryRow]) -> None:
    rows: list[dict[str, object]] = []

    for r in summary:
        rule1 = 1 if r.fan_in > 4 else 0
        rule2 = 1 if 0 < r.avg_time_to_outflow_min <= 15 else 0
        rule3 = 1 if r.outflow_ratio_pct > 95 else 0
        rule4 = 1 if r.account_age_days < 60 and r.fan_in > 3 else 0
        triggered = rule1 + rule2 + rule3 + rule4

        rows.append(
            {
                "Account_ID": r.account_id,
                "Layer": r.layer,
                "Is_Mule": r.is_mule,
                "Risk_Score": r.risk_score,
                "Rule_FanIn": rule1,
                "Rule_HitRun": rule2,
                "Rule_Draining": rule3,
                "Rule_NewAcct": rule4,
                "Rules_Triggered": triggered,
                "Predicted_HighRisk": 1 if r.risk_score >= 70 else 0,
            }
        )

    write_csv(
        OUT_DIR / "rule_trigger_matrix.csv",
        [
            "Account_ID",
            "Layer",
            "Is_Mule",
            "Risk_Score",
            "Rule_FanIn",
            "Rule_HitRun",
            "Rule_Draining",
            "Rule_NewAcct",
            "Rules_Triggered",
            "Predicted_HighRisk",
        ],
        rows,
    )



def build_risk_bins(summary: list[SummaryRow]) -> None:
    bins = [(0, 19), (20, 39), (40, 59), (60, 69), (70, 79), (80, 89), (90, 100)]
    counts: dict[tuple[str, int], int] = defaultdict(int)

    def find_bin(score: int) -> str:
        for lo, hi in bins:
            if lo <= score <= hi:
                return f"{lo:02d}-{hi:02d}"
        return "Other"

    for r in summary:
        b = find_bin(r.risk_score)
        counts[(b, r.is_mule)] += 1

    ordered_bins = [f"{lo:02d}-{hi:02d}" for lo, hi in bins]
    rows: list[dict[str, object]] = []
    for b in ordered_bins:
        subtotal = counts.get((b, 0), 0) + counts.get((b, 1), 0)
        for is_mule in (0, 1):
            cnt = counts.get((b, is_mule), 0)
            pct = (cnt / subtotal * 100) if subtotal else 0.0
            rows.append(
                {
                    "Risk_Bin": b,
                    "Is_Mule": is_mule,
                    "Account_Count": cnt,
                    "Bin_Share_Pct": round(pct, 2),
                }
            )

    write_csv(
        OUT_DIR / "risk_score_bins.csv",
        ["Risk_Bin", "Is_Mule", "Account_Count", "Bin_Share_Pct"],
        rows,
    )



def build_layer_performance_extended(layer_path: Path) -> None:
    rows: list[dict[str, object]] = []
    with layer_path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rate = parse_float(r.get("Detection_Rate_Pct", "0"))
            miss = 100 - rate
            rows.append(
                {
                    "Layer": r.get("Layer", ""),
                    "Total_Mule_Transactions": parse_int(
                        r.get("Total_Mule_Transactions", "0")
                    ),
                    "Detection_Rate_Pct": rate,
                    "Miss_Rate_Pct": round(miss, 2),
                    "Gap_to_Target50_Pct": round(max(0.0, 50 - rate), 2),
                    "Detected_Count": parse_int(r.get("Detected_Count", "0")),
                    "Missed_Count": parse_int(r.get("Missed_Count", "0")),
                }
            )

    write_csv(
        OUT_DIR / "layer_performance_extended.csv",
        [
            "Layer",
            "Total_Mule_Transactions",
            "Detection_Rate_Pct",
            "Miss_Rate_Pct",
            "Gap_to_Target50_Pct",
            "Detected_Count",
            "Missed_Count",
        ],
        rows,
    )



def build_false_positive_review(summary: list[SummaryRow]) -> None:
    rows = [
        {
            "Account_ID": r.account_id,
            "Layer": r.layer,
            "Risk_Score": r.risk_score,
            "Fan_In_Count": r.fan_in,
            "Fan_Out_Count": r.fan_out,
            "Outflow_Ratio_Pct": round(r.outflow_ratio_pct, 2),
            "Avg_Time_To_Outflow_Min": round(r.avg_time_to_outflow_min, 2),
        }
        for r in summary
        if r.is_mule == 0 and r.risk_score >= 70
    ]

    rows.sort(key=lambda x: (x["Risk_Score"], x["Outflow_Ratio_Pct"]), reverse=True)

    write_csv(
        OUT_DIR / "false_positive_review.csv",
        [
            "Account_ID",
            "Layer",
            "Risk_Score",
            "Fan_In_Count",
            "Fan_Out_Count",
            "Outflow_Ratio_Pct",
            "Avg_Time_To_Outflow_Min",
        ],
        rows,
    )



def build_threshold_tradeoff(summary: list[SummaryRow]) -> None:
    rows: list[dict[str, object]] = []

    for threshold in range(0, 101, 5):
        tp = fp = fn = tn = 0
        for r in summary:
            pred = 1 if r.risk_score >= threshold else 0
            if pred == 1 and r.is_mule == 1:
                tp += 1
            elif pred == 1 and r.is_mule == 0:
                fp += 1
            elif pred == 0 and r.is_mule == 1:
                fn += 1
            else:
                tn += 1

        recall = (tp / (tp + fn) * 100) if (tp + fn) else 0.0
        precision = (tp / (tp + fp) * 100) if (tp + fp) else 0.0
        fpr = (fp / (fp + tn) * 100) if (fp + tn) else 0.0

        rows.append(
            {
                "Risk_Threshold": threshold,
                "TP": tp,
                "FP": fp,
                "FN": fn,
                "TN": tn,
                "Recall_Pct": round(recall, 2),
                "Precision_Pct": round(precision, 2),
                "FPR_Pct": round(fpr, 2),
            }
        )

    write_csv(
        OUT_DIR / "threshold_tradeoff_curve.csv",
        [
            "Risk_Threshold",
            "TP",
            "FP",
            "FN",
            "TN",
            "Recall_Pct",
            "Precision_Pct",
            "FPR_Pct",
        ],
        rows,
    )


def build_layer_flow_from_transactions(transactions: list[dict[str, str]]) -> None:
    def layer_bucket(account_id: str) -> str:
        if account_id.startswith("MULE_L1"):
            return "Layer1"
        if account_id.startswith("MULE_L2"):
            return "Layer2"
        if account_id.startswith("MULE_L3"):
            return "Layer3+"
        if account_id.startswith("VIC"):
            return "Victim"
        if account_id == "CASH_OUT":
            return "CashOut"
        return "Normal"

    edge_counts: Counter[tuple[str, str]] = Counter()
    edge_amounts: defaultdict[tuple[str, str], float] = defaultdict(float)

    for t in transactions:
        src = t.get("From_Account", "")
        dst = t.get("To_Account", "")
        src_layer = layer_bucket(src)
        dst_layer = layer_bucket(dst)
        if src_layer == "Normal" and dst_layer == "Normal":
            continue
        k = (src_layer, dst_layer)
        edge_counts[k] += 1
        edge_amounts[k] += parse_float(t.get("Amount", "0"))

    rows: list[dict[str, object]] = []
    for (src, dst), cnt in sorted(edge_counts.items(), key=lambda x: (-x[1], x[0])):
        rows.append(
            {
                "Source_Layer": src,
                "Target_Layer": dst,
                "Txn_Count": cnt,
                "Total_Amount": round(edge_amounts[(src, dst)], 2),
            }
        )

    write_csv(
        OUT_DIR / "layer_flow_edges.csv",
        ["Source_Layer", "Target_Layer", "Txn_Count", "Total_Amount"],
        rows,
    )



def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    transactions = load_transactions(TRANSACTIONS_PATH)
    summary = load_account_summary(ACCOUNT_SUMMARY_PATH)

    build_kpi_overview(transactions, summary)
    build_hourly_profile(transactions)
    build_channel_mix(transactions)
    build_rule_trigger_matrix(summary)
    build_risk_bins(summary)
    build_layer_performance_extended(LAYER_RATE_PATH)
    build_false_positive_review(summary)
    build_threshold_tradeoff(summary)
    build_layer_flow_from_transactions(transactions)

    print("Created visualization marts in:", OUT_DIR)


if __name__ == "__main__":
    main()
