"""
Mule Account Detection Dataset Generator
DE471 Final Project - Fan-in/Fan-out + Layering Depth
"""
import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict
import os

random.seed(42)

# ==================================================
# CONFIG
# ==================================================
N_NORMAL_ACC = 950
N_VICTIMS    = 200
N_MULE_L1    = 20
N_MULE_L2    = 20
N_MULE_L3    = 10
START_DATE   = datetime(2024, 1, 1)
END_DATE     = datetime(2024, 12, 31)

CHANNELS_NORMAL = ['Mobile_App']*40 + ['PromptPay']*30 + ['Branch']*20 + ['ATM']*10
CHANNELS_MULE   = ['PromptPay']*55 + ['Mobile_App']*30 + ['ATM']*10 + ['Branch']*5

OUT_DIR = 'E:/01/dowload/power bi proeject/05_final/data/'
os.makedirs(OUT_DIR, exist_ok=True)

# ==================================================
# HELPERS
# ==================================================
def rand_dt(start, end, mule=False):
    delta = end - start
    days = random.randint(0, delta.days)
    if mule and random.random() < 0.6:
        hour = random.choice(list(range(22, 24)) + list(range(0, 7)))
    else:
        hour = random.choices(
            range(24),
            weights=[1,1,1,1,1,1,2,4,6,8,9,10,9,8,8,7,7,8,7,5,4,3,2,1]
        )[0]
    return start + timedelta(
        days=days, hours=hour,
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

def fmt(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# ==================================================
# ACCOUNTS
# ==================================================
normal_accs = [f"ACC{i+1:05d}" for i in range(N_NORMAL_ACC)]
victim_accs = [f"VIC{i+1:04d}" for i in range(N_VICTIMS)]
mule_l1 = [f"MULE_L1_{i+1:03d}" for i in range(N_MULE_L1)]
mule_l2 = [f"MULE_L2_{i+1:03d}" for i in range(N_MULE_L2)]
mule_l3 = [f"MULE_L3_{i+1:03d}" for i in range(N_MULE_L3)]

acc_age = {}
for a in normal_accs: acc_age[a] = random.randint(180, 3650)
for a in victim_accs: acc_age[a] = random.randint(365, 3650)
for a in mule_l1: acc_age[a] = random.randint(7, 60)
for a in mule_l2: acc_age[a] = random.randint(14, 120)
for a in mule_l3: acc_age[a] = random.randint(30, 180)

balance = defaultdict(lambda: round(random.uniform(2000, 50000), 2))
for a in mule_l1 + mule_l2 + mule_l3:
    balance[a] = round(random.uniform(0, 500), 2)

# ==================================================
# TRANSACTIONS
# ==================================================
txns = []
tid = 1

def add_txn(ts, src, dst, amt, mule, layer, pattern):
    global tid
    bef_src = balance[src]
    balance[src] = round(balance[src] - amt, 2)
    aft_src = balance[src]
    if dst != 'CASH_OUT':
        balance[dst] = round(balance[dst] + amt, 2)

    ch = random.choices(CHANNELS_MULE if mule else CHANNELS_NORMAL)[0]

    txns.append({
        'Transaction_ID': f"TXN{tid:07d}",
        'Timestamp': fmt(ts),
        'From_Account': src,
        'To_Account': dst,
        'Amount': amt,
        'Channel': ch,
        'Sender_Age_Days': acc_age.get(src, 0),
        'Receiver_Age_Days': acc_age.get(dst, 0) if dst != 'CASH_OUT' else 0,
        'Sender_Balance_Before': bef_src,
        'Sender_Balance_After': aft_src,
        'Layer_Depth': layer,
        'Pattern_Type': pattern,
        'Is_Mule': mule
    })
    tid += 1

# Normal transactions
for src in normal_accs:
    for _ in range(random.randint(2, 12)):
        ts = rand_dt(START_DATE, END_DATE, mule=False)
        dst = random.choice(normal_accs)
        if dst == src:
            continue
        amt = round(random.uniform(150, 12000), 2)
        add_txn(ts, src, dst, amt, 0, 0, 'Normal')

# Layer 1 mules
for m in mule_l1:
    base = rand_dt(START_DATE, END_DATE, mule=True)
    n_in = random.randint(5, 10)
    in_dts = []
    for v in random.sample(victim_accs, n_in):
        ts = base + timedelta(minutes=random.randint(0, 50))
        in_dts.append(ts)
        amt = round(random.uniform(8000, 80000), 2)
        add_txn(ts, v, m, amt, 1, 1, 'Fan-in')
    last_in = max(in_dts)
    n_out = random.randint(3, 6)
    for t in random.sample(mule_l2, min(n_out, len(mule_l2))):
        ts = last_in + timedelta(minutes=random.randint(2, 14))
        amt = round(random.uniform(5000, 35000), 2)
        add_txn(ts, m, t, amt, 1, 1, 'Fan-out')

# Layer 2 mules
for m in mule_l2:
    base = rand_dt(START_DATE, END_DATE, mule=True)
    n_in = random.randint(2, 4)
    in_dts = []
    for src in random.sample(mule_l1, min(n_in, len(mule_l1))):
        ts = base + timedelta(minutes=random.randint(0, 30))
        in_dts.append(ts)
        amt = round(random.uniform(3000, 25000), 2)
        add_txn(ts, src, m, amt, 1, 2, 'Fan-in')
    last_in = max(in_dts) if in_dts else base
    n_out = random.randint(2, 4)
    for t in random.sample(mule_l3, min(n_out, len(mule_l3))):
        ts = last_in + timedelta(minutes=random.randint(5, 25))
        amt = round(random.uniform(1500, 15000), 2)
        add_txn(ts, m, t, amt, 1, 2, 'Fan-out')

# Layer 3+ mules
for m in mule_l3:
    base = rand_dt(START_DATE, END_DATE, mule=True)
    n_in = random.randint(1, 3)
    in_dts = []
    for src in random.sample(mule_l2, min(n_in, len(mule_l2))):
        ts = base + timedelta(minutes=random.randint(0, 20))
        in_dts.append(ts)
        amt = round(random.uniform(1000, 12000), 2)
        add_txn(ts, src, m, amt, 1, 3, 'Fan-in')
    last_in = max(in_dts) if in_dts else base
    ts = last_in + timedelta(minutes=random.randint(10, 50))
    amt = round(random.uniform(500, 9000), 2)
    add_txn(ts, m, 'CASH_OUT', amt, 1, 3, 'Cash-out')

# ==================================================
# WRITE TRANSACTIONS
# ==================================================
header = [
    'Transaction_ID','Timestamp','From_Account','To_Account','Amount',
    'Channel','Sender_Age_Days','Receiver_Age_Days',
    'Sender_Balance_Before','Sender_Balance_After',
    'Layer_Depth','Pattern_Type','Is_Mule'
]
txns.sort(key=lambda x: x['Timestamp'])
with open(OUT_DIR + 'Transactions.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=header)
    w.writeheader()
    w.writerows(txns)

# ==================================================
# ACCOUNT SUMMARY
# ==================================================
in_amt = defaultdict(float)
out_amt = defaultdict(float)
in_count = defaultdict(int)
out_count = defaultdict(int)
in_srcs = defaultdict(set)
out_dsts = defaultdict(set)
last_in_ts = {}
first_out_after_in = {}
min_balance = defaultdict(lambda: float('inf'))
acc_mule = {}

for t in txns:
    s, d, a = t['From_Account'], t['To_Account'], float(t['Amount'])
    ts = datetime.strptime(t['Timestamp'], '%Y-%m-%d %H:%M:%S')
    out_amt[s] += a
    if d != 'CASH_OUT':
        in_amt[d] += a
        in_count[d] += 1
        in_srcs[d].add(s)
    out_count[s] += 1
    out_dsts[s].add(d)
    if t['Pattern_Type'] == 'Fan-in':
        last_in_ts[d] = ts
    if t['Pattern_Type'] in ('Fan-out', 'Cash-out') and s in last_in_ts:
        if s not in first_out_after_in:
            first_out_after_in[s] = (ts - last_in_ts[s]).total_seconds() / 60
    if t['Sender_Balance_After'] < min_balance[s]:
        min_balance[s] = t['Sender_Balance_After']
    if t['Is_Mule'] == 1:
        acc_mule[s] = 1
        if d != 'CASH_OUT':
            acc_mule[d] = 1

all_accs = set(list(in_amt.keys()) + list(out_amt.keys()))
all_accs.discard('CASH_OUT')

summary_rows = []
for a in sorted(all_accs):
    fi = len(in_srcs[a])
    fo = len(out_dsts[a])
    ti = round(in_amt[a], 2)
    to = round(out_amt[a], 2)
    ratio = round((to / ti * 100) if ti > 0 else 0, 1)
    avg_t2o = round(first_out_after_in.get(a, 0), 1)

    layer = 'Normal'
    if a.startswith('MULE_L1'): layer = 'Layer1'
    elif a.startswith('MULE_L2'): layer = 'Layer2'
    elif a.startswith('MULE_L3'): layer = 'Layer3+'
    elif a.startswith('VIC'): layer = 'Victim'

    score = 0
    if fi > 4: score += 30
    if 0 < avg_t2o <= 15: score += 35
    if ratio > 95: score += 25
    if acc_age.get(a, 9999) < 60 and fi > 3: score += 10
    score = min(100, score)

    if score >= 70:
        lvl = 'High_Risk'
    elif score >= 40:
        lvl = 'Watch'
    else:
        lvl = 'Normal'

    summary_rows.append({
        'Account_ID': a,
        'Account_Age_Days': acc_age.get(a, 0),
        'Layer': layer,
        'Total_In_Amount': ti,
        'Total_Out_Amount': to,
        'Outflow_Ratio_Pct': ratio,
        'Fan_In_Count': fi,
        'Fan_Out_Count': fo,
        'Total_Transactions': in_count[a] + out_count[a],
        'Avg_Time_To_Outflow_Min': avg_t2o,
        'Min_Balance': round(min_balance[a], 2) if min_balance[a] != float('inf') else 0,
        'Risk_Score': score,
        'Risk_Level': lvl,
        'Is_Mule': acc_mule.get(a, 0)
    })

sum_header = list(summary_rows[0].keys())
with open(OUT_DIR + 'Account_Summary.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=sum_header)
    w.writeheader()
    w.writerows(summary_rows)

# ==================================================
# LAYERING DETECTION RATE
# ==================================================
detection_rates = {'Layer1': 80, 'Layer2': 45, 'Layer3+': 12}
layer_counts = defaultdict(int)
for t in txns:
    if t['Is_Mule'] == 1:
        if t['Layer_Depth'] == 1: layer_counts['Layer1'] += 1
        elif t['Layer_Depth'] == 2: layer_counts['Layer2'] += 1
        elif t['Layer_Depth'] == 3: layer_counts['Layer3+'] += 1

with open(OUT_DIR + 'Layering_Detection_Rate.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Layer', 'Total_Mule_Transactions', 'Detection_Rate_Pct', 'Detected_Count', 'Missed_Count'])
    for lay, rate in detection_rates.items():
        total = layer_counts[lay]
        det = round(total * rate / 100)
        w.writerow([lay, total, rate, det, total - det])

# ==================================================
# STATS
# ==================================================
print(f"Transactions.csv          : {len(txns)} rows")
print(f"Account_Summary.csv       : {len(summary_rows)} accounts")
print(f"Layering_Detection_Rate.csv : 3 rows")
print()
print("=== STATS ===")
print(f"Mule txns      : {sum(1 for t in txns if t['Is_Mule']==1)}")
print(f"Normal txns    : {sum(1 for t in txns if t['Is_Mule']==0)}")
print(f"Mule accs      : {sum(1 for r in summary_rows if r['Is_Mule']==1)}")
print(f"Normal accs    : {sum(1 for r in summary_rows if r['Is_Mule']==0)}")
print(f"High Risk      : {sum(1 for r in summary_rows if r['Risk_Level']=='High_Risk')}")
print(f"Watch          : {sum(1 for r in summary_rows if r['Risk_Level']=='Watch')}")
print(f"Normal_Risk    : {sum(1 for r in summary_rows if r['Risk_Level']=='Normal')}")
