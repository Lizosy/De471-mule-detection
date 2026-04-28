# DE471 Final Project — Mule Account Detection

การตรวจจับบัญชีม้า (Money Mule) ผ่าน Fan-in/Fan-out + Layering Depth

## Repository scope

Repo นี้เก็บเฉพาะไฟล์ที่เกี่ยวกับ **Final** เท่านั้น (ไฟล์ midterm / HW เก่าถูก ignore ไว้ใน `.gitignore`)

## โครงสร้าง

```
.
├── 02_Notebooks/
│   ├── Mule_Detection_Final_Analysis.ipynb   # วิเคราะห์หลัก + Rule-based + Precision/Recall
│   └── figures/                              # PNG export สำหรับ slide
└── 05_final/
    ├── Slide_FanInOut_Layering_Prompt.txt    # โครง slide deck (17 slides)
    ├── Final Project Instructions and Rubric.txt
    ├── Data_Requirements_Checklist.txt
    ├── generate_data.py                      # script สร้าง synthetic data
    ├── data/
    │   ├── Account_Summary.csv               (1,103 accounts)
    │   ├── Transactions.csv                  (7,277 transactions)
    │   ├── Layering_Detection_Rate.csv       (legacy baseline)
    │   ├── Mule_Detection_Dashboard*.twb     # Tableau workbooks
    │   └── viz_marts/                        # pre-aggregated CSVs สำหรับ Tableau
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

## Reference

- FATF (2024) Guidance on Money Mule-related Activity
- ธปท. — APP Fraud Report 2566
- ปปง. — พ.ร.บ. AML 2542
- UK Finance (2023) APP Fraud Report
