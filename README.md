# DE471 Final Project — Mule Account Detection

การตรวจจับบัญชีม้า (Money Mule) ผ่าน Fan-in/Fan-out + Layering Depth

## Deliverables

- 📄 **Slide Deck (PDF)** — โครงสร้าง 17 slides ที่ [`05_final/Slide_FanInOut_Layering_Prompt.txt`](05_final/Slide_FanInOut_Layering_Prompt.txt)
- 🗂️ **Project Canvas (PDF)** — ภาพรวม 1 หน้า: [`PROJECT_CANVAS.md`](PROJECT_CANVAS.md) *(ดูข้างล่าง)*
- 💻 **GitHub Repository** — repo นี้
- 🎤 **Live 7-min Presentation + 3-min Q&A**

## Repository scope

Repo นี้เก็บเฉพาะไฟล์ที่เกี่ยวกับ **Final** เท่านั้น (ไฟล์ midterm / HW เก่าถูก ignore ไว้ใน `.gitignore`)

## โครงสร้าง

```
.
├── PROJECT_CANVAS.md                            # 1-page project canvas (deliverable)
├── DE471 Final Project Mule Account Detection.pdf
├── 02_Notebooks/
│   ├── Mule_Detection_Final_Analysis.ipynb      # วิเคราะห์หลัก + Rule-based + Precision/Recall
│   └── figures/                                 # PNG export สำหรับ slide
└── 05_final/
    ├── Slide_FanInOut_Layering_Prompt.txt       # โครง slide deck (17 slides)
    ├── Final Project Instructions and Rubric.txt
    ├── Data_Requirements_Checklist.txt
    ├── generate_data.py                         # script สร้าง synthetic data
    ├── data/
    │   ├── Account_Summary.csv                  (1,103 accounts)
    │   ├── Transactions.csv                     (7,277 transactions)
    │   ├── Layering_Detection_Rate.csv          (legacy baseline)
    │   ├── Mule_Detection_Dashboard*.twb        # Tableau workbooks
    │   └── viz_marts/                           # pre-aggregated CSVs สำหรับ Tableau
    └── 06_visual_pack/
        ├── build_visual_marts.py
        ├── Tableau_Upgrade_Blueprint.md
        ├── Tableau_Calculated_Fields.txt
        └── Slide_Visual_Mapping.csv
```

## Reproduce

```bash
# 1) สร้าง venv + ติดตั้ง package
python -m venv .venv
.venv/Scripts/python -m pip install pandas matplotlib jupyter ipykernel nbconvert

# 2) (ถ้าต้องการ) regenerate data
python 05_final/generate_data.py

# 3) Run notebook
.venv/Scripts/python -m jupyter nbconvert --to notebook --execute --inplace \
    02_Notebooks/Mule_Detection_Final_Analysis.ipynb
```

## Key results (Rule-Based Detection)

| Threshold | Recall | FPR | Precision |
|-----------|--------|-----|-----------|
| 70 (High_Risk) | 16.3% | 0.0% | 100.0% |
| 40 (Watch+) | 24.8% | 41.4% | 8.8% |

→ ไม่มี threshold ใดเข้าเป้า `Recall ≥ 90% AND FPR ≤ 5%` — ต้องเสริม ML stage

---

# 🗂️ Project Canvas

**Course:** DE471 Data Analytics & BI · **Project:** Mule Account Detection
**Team:** ชฏาวีร์ สุริวงค์ (66102010166) · วิกรม มานพิริยะ (66102010185) · สมปราชญ์ บูรณะ (66102010189)

### ❶ Background & Pain Points · *Section 1 (7 pts)*

- APP Fraud ไทยปี 2566 มูลค่าเสียหายระดับแสนล้านบาท — เหยื่อโอนสมัครใจ ธนาคาร reverse ยาก
- Legacy detection จับ Layer1 ได้ 80% แต่ **Layer3+ จับได้แค่ 12%**
- Compliance ต่อ พ.ร.บ. AML 2542 + แนว AML/CFT ของ ธปท.

### ❷ SMART Objectives · *Section 1 (8 pts)*

| | |
|---|---|
| **S**pecific | ตรวจม้าจาก 1,103 บัญชีด้วย Fan-in/Fan-out + Layering |
| **M**easurable | Recall ≥ 90% AND FPR ≤ 5% |
| **A**chievable | Rule-based Risk Score (0-100) + ML stage |
| **R**elevant | ตอบโจทย์ AML/CFT + ลดความเสียหาย APP Fraud |
| **T**ime-bound | Dataset 12 เดือน (2024-01-01 → 2024-12-31) |

### ❸ Stakeholders

Compliance Officer · Risk Team · ลูกค้าธนาคาร · ธปท./ปปง.

### ❹ Hypothesis & 5W1H · *Section 2 (10 pts)*

| 5W1H | คำถาม | สมมติฐาน |
|---|---|---|
| Who? | บัญชีกลุ่มไหนเสี่ยง? | บัญชีอายุ < 60 วัน + Fan-in สูง |
| What? | Pattern อะไรชี้ว่าเป็นม้า? | Hit & Run + Account Draining |
| When? | เกิดตอนไหน? | กลางคืน 22:00–05:59 |
| Where? | ช่องทางไหน? | PromptPay (52% ของ mule txn) |
| Why? | ทำไม legacy พลาด? | Traceability ต่ำเมื่อซ้อน Layer |
| How? | วัดยังไง? | Outflow Ratio + Time-to-Outflow |

### ❺ Data Sources · *Section 3 (10 pts)*

| File | Rows | ใช้ทำอะไร |
|---|---|---|
| `Transactions.csv` | 7,277 | Pattern analysis |
| `Account_Summary.csv` | 1,103 | Risk Score, Boxplot |
| `Layering_Detection_Rate.csv` | 3 | Legacy baseline |

Class imbalance: Mule 5.3% / Normal 94.7%

### ❻ Method & Tools

- Python (pandas, matplotlib) · Tableau (8 worksheets + dashboard)
- Rule-based Risk Score: Fan-in>4 (+30), Hit&Run ≤15min (+35), Outflow>95% (+25), New + Fan-in (+10)
- Evaluation: Precision / Recall / FPR + Threshold sweep 0-100

### ❼ Key Findings · *Section 4 (7 pts)*

| # | Finding | Evidence |
|---|---|---|
| 1 | Hit & Run velocity | Layer1 = 3.9 min vs Normal = 0 min |
| 2 | Account draining | Mule outflow ratio > 95% |
| 3 | Layering ทำลาย legacy | 80% → 45% → 12% |
| 4 | PromptPay = ช่องทางหลัก | Mule 52% / Normal 30% |
| 5 | กลางคืนเป็นเวลาเสี่ยง | Mule 49% / Normal 8% |

### ❽ Recommendations · *Section 4 (8 pts)*

- Real-time trigger: Fan-in > 4 + Time < 15 min → Freeze
- Watchlist: บัญชีอายุ < 60 วัน + Fan-in สูง
- Multi-channel score: PromptPay + กลางคืน + ยอดต่ำ → score+
- Current best @ threshold 70: Precision **100%** · FPR **0%** · Recall **16.3%**
- Future: ML (LogReg / RF / XGBoost) + Graph DB (Neo4j) + Stream (Kafka)

---

## Reference

- FATF (2024) Guidance on Money Mule-related Activity
- ธปท. — APP Fraud Report 2566
- ปปง. — พ.ร.บ. AML 2542
- UK Finance (2023) APP Fraud Report
