# Project Canvas — Mule Account Detection

**Course:** DE471 Data Analytics & Business Intelligence
**Project:** Final · Mule Account Detection via Fan-in/Fan-out + Layering Depth
**Team:** ชฏาวีร์ สุริวงค์ (66102010166) · วิกรม มานพิริยะ (66102010185) · สมปราชญ์ บูรณะ (66102010189)

---

## ❶ Background & Pain Points · *Section 1 (7 pts)*

- APP Fraud (Authorized Push Payment) ในไทยปี 2566 มูลค่าเสียหายระดับแสนล้านบาท เหยื่อโอนเองด้วยความสมัครใจ ทำให้ธนาคาร reverse คืนยาก
- **Legacy detection** ของธนาคารดูธุรกรรมเดี่ยว → จับ Layer1 ได้ 80% แต่ **Layer3+ จับได้แค่ 12%**
- Compliance ต่อ พ.ร.บ. ป้องกันและปราบปรามการฟอกเงิน 2542 + แนวปฏิบัติ AML/CFT ของ ธปท.

## ❷ SMART Objectives · *Section 1 (8 pts)*

| | |
|---|---|
| **S**pecific | ตรวจจับบัญชีม้าจาก 1,103 บัญชี โดยใช้ Fan-in/Fan-out + Layering pattern |
| **M**easurable | Recall ≥ 90% AND FPR ≤ 5% (เป้าจุดสมดุล) |
| **A**chievable | Rule-based Risk Score (4 rules → 0-100) + ML stage |
| **R**elevant | ตอบโจทย์ AML/CFT compliance + ลดความเสียหาย APP Fraud |
| **T**ime-bound | Dataset 12 เดือน (2024-01-01 → 2024-12-31) |

## ❸ Stakeholders

- **Compliance Officer** — ใช้ระบบในการ flag/freeze บัญชี
- **Risk Management Team** — ตั้ง threshold + ปรับ rule
- **ลูกค้าธนาคาร** — กระทบโดยตรงถ้า FPR สูง (โดนบล็อกผิด)
- **ธปท. / ปปง.** — รายงานและตรวจสอบตามกฎหมาย

## ❹ Hypothesis & 5W1H · *Section 2 (10 pts)*

| 5W1H | คำถาม | สมมติฐาน |
|---|---|---|
| **Who?** | บัญชีกลุ่มไหนเสี่ยง? | บัญชีอายุ < 60 วัน + Fan-in สูง |
| **What?** | Pattern อะไรชี้ว่าเป็นม้า? | Hit & Run + Account Draining |
| **When?** | เกิดตอนไหน? | กลางคืน 22:00–05:59 |
| **Where?** | ช่องทางไหนถูกใช้? | PromptPay (52% ของ mule txn) |
| **Why?** | ทำไม legacy พลาด? | Traceability ต่ำเมื่อซ้อน Layer ลึก |
| **How?** | วัดยังไง? | Outflow Ratio + Velocity (Time-to-Outflow) |

## ❺ Data Sources · *Section 3 (10 pts)*

| File | Rows | ใช้ทำอะไร |
|---|---|---|
| `Transactions.csv` | 7,277 | Pattern analysis รายธุรกรรม |
| `Account_Summary.csv` | 1,103 | Boxplot, Risk Score |
| `Layering_Detection_Rate.csv` | 3 | Legacy baseline |

**Class imbalance:** Mule 5.3% / Normal 94.7% (สมจริง ไม่ลบ outliers)

## ❻ Method & Tools

- **Python:** pandas, matplotlib (Notebook: `02_Notebooks/Mule_Detection_Final_Analysis.ipynb`)
- **Tableau:** 8 worksheets + Dashboard (`05_final/data/Mule_Detection_Dashboard.twb`)
- **Rule-based Risk Score (0–100):** Fan-in > 4 (+30), Hit&Run ≤ 15min (+35), Outflow > 95% (+25), New Account + Fan-in (+10)
- **Evaluation:** Confusion Matrix → Precision / Recall / FPR · Threshold sweep 0–100

## ❼ Key Findings · *Section 4 (7 pts)*

| # | Finding | Evidence |
|---|---|---|
| 1 | Hit & Run velocity | Layer1 = 3.9 min · Normal = 0 min |
| 2 | Account draining | Mule outflow ratio > 95% |
| 3 | Layering ทำลาย legacy | 80% → 45% → 12% |
| 4 | PromptPay = ช่องทางหลัก | Mule 52% / Normal 30% |
| 5 | กลางคืนเป็นเวลาเสี่ยง | Mule 49% / Normal 8% |

## ❽ Recommendations & Impact · *Section 4 (8 pts)*

- **Real-time trigger:** Fan-in > 4 + Time-to-Outflow < 15 min → Auto-freeze
- **Watchlist:** บัญชีอายุ < 60 วัน + Fan-in สูง → Enhanced monitoring
- **Multi-channel score:** PromptPay + กลางคืน + ยอดต่ำ → score เพิ่ม
- **Trade-off ปัจจุบัน @ threshold 70:** Precision **100%** · FPR **0%** · Recall **16.3%**
- **Future Work:** ML (Logistic / Random Forest / XGBoost) + Graph DB (Neo4j) + Real-time Stream (Kafka)

---

**Repository:** ดู `README.md` · **Notebook reproduction:** `02_Notebooks/Mule_Detection_Final_Analysis.ipynb`
