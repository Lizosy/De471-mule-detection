================================================================
DATASET README
Mule Account Detection - Fan-in/Fan-out + Layering Depth
DE471 Final Project
================================================================


PATH ของไฟล์
─────────────────────────────────────────────
e:\01\dowload\power bi proeject\05_final\data\

ไฟล์ที่ Generate ออกมามี 3 ไฟล์:

1. Transactions.csv          (7,277 rows)
2. Account_Summary.csv       (1,103 accounts)
3. Layering_Detection_Rate.csv (3 rows)


================================================================
FILE 1: Transactions.csv  (ข้อมูลธุรกรรมระดับรายการ)
================================================================

ใช้สำหรับ: ดูรายละเอียดแต่ละธุรกรรม + วิเคราะห์ Pattern

คอลัมน์                  ประเภท     คำอธิบาย
─────────────────────────────────────────────────────────────
Transaction_ID           String     รหัสธุรกรรม (TXN0000001...)
Timestamp                DateTime   วันเวลาทำรายการ
From_Account             String     บัญชีต้นทาง
To_Account               String     บัญชีปลายทาง (CASH_OUT = ถอนสด)
Amount                   Float      ยอดเงิน (บาท)
Channel                  String     PromptPay / Mobile_App / ATM / Branch
Sender_Age_Days          Integer    อายุบัญชีต้นทาง (วัน)
Receiver_Age_Days        Integer    อายุบัญชีปลายทาง
Sender_Balance_Before    Float      ยอดคงเหลือต้นทางก่อนทำรายการ
Sender_Balance_After     Float      ยอดคงเหลือต้นทางหลังทำรายการ
Layer_Depth              Integer    0=Normal, 1, 2, 3 (ชั้นของบัญชีม้า)
Pattern_Type             String     Normal / Fan-in / Fan-out / Cash-out
Is_Mule                  Integer    0 = ปกติ, 1 = ม้า  (Ground Truth)
─────────────────────────────────────────────────────────────

หมายเหตุการตั้งชื่อบัญชี:
  ACC00001  ─→ บัญชีปกติ
  VIC0001   ─→ เหยื่อ (Victim)
  MULE_L1_001 ─→ บัญชีม้า ชั้นที่ 1
  MULE_L2_001 ─→ บัญชีม้า ชั้นที่ 2
  MULE_L3_001 ─→ บัญชีม้า ชั้นที่ 3+
  CASH_OUT  ─→ การถอนสด (ปลายสุด)


================================================================
FILE 2: Account_Summary.csv  (สรุปต่อบัญชี)
================================================================

ใช้สำหรับ: Dashboard + Boxplot + Risk Score Analysis

คอลัมน์                    ประเภท     คำอธิบาย
─────────────────────────────────────────────────────────────
Account_ID                 String     รหัสบัญชี
Account_Age_Days           Integer    อายุบัญชี (วัน)
Layer                      String     Normal / Victim / Layer1 / Layer2 / Layer3+
Total_In_Amount            Float      ยอดเงินที่รับเข้ารวม
Total_Out_Amount           Float      ยอดเงินที่โอนออกรวม
Outflow_Ratio_Pct          Float      % ของเงินที่โอนออก (out/in × 100)
Fan_In_Count               Integer   จำนวนบัญชีต้นทางที่แตกต่างกัน
Fan_Out_Count              Integer   จำนวนบัญชีปลายทางที่แตกต่างกัน
Total_Transactions         Integer   จำนวนธุรกรรมทั้งหมด
Avg_Time_To_Outflow_Min    Float     นาทีเฉลี่ยรับเงินถึงโอนออก
Min_Balance                Float     ยอดคงเหลือต่ำสุด (วัด Account Draining)
Risk_Score                 Integer   คะแนนความเสี่ยง 0-100
Risk_Level                 String    Normal / Watch / High_Risk
Is_Mule                    Integer   Ground Truth (0/1)
─────────────────────────────────────────────────────────────

วิธีคำนวณ Risk Score:
  Fan_In_Count > 4              → +30
  Time_To_Outflow ≤ 15 นาที     → +35
  Outflow_Ratio > 95%           → +25
  บัญชีอายุ < 60 วัน + Fan-in สูง → +10

  Score >= 70  → High_Risk  (🔴)
  Score 40-69  → Watch      (🟡)
  Score < 40   → Normal     (🟢)


================================================================
FILE 3: Layering_Detection_Rate.csv  (สถิติการตรวจจับตามชั้น)
================================================================

ใช้สำหรับ: Bar Chart แสดง Detection Rate ตามชั้น Layer

คอลัมน์                       คำอธิบาย
─────────────────────────────────────────────
Layer                         Layer1 / Layer2 / Layer3+
Total_Mule_Transactions       จำนวนธุรกรรมม้าทั้งหมดในชั้น
Detection_Rate_Pct            % ที่ระบบเดิมจับได้
Detected_Count                จำนวนที่จับได้
Missed_Count                  จำนวนที่พลาด


================================================================
สถิติของข้อมูล (Generated)
================================================================

Transactions:
  - Normal     :  6,890 (94.7%)
  - Mule       :    387  (5.3%)  ← Class Imbalance สมจริง
  - รวม        :  7,277

Accounts:
  - Normal     :    950 (86.1%)
  - Mule       :    153 (13.9%)  ← รวม victim ที่ flag จากการเชื่อมโยง
  - High Risk  :     25
  - Watch      :    406
  - Normal     :    672

Date Range: 2024-01-01 ถึง 2024-12-31 (12 เดือน)


================================================================
ขั้นตอนการนำเข้า TABLEAU
================================================================

วิธีที่ 1: เชื่อมต่อทีละไฟล์
  1. เปิด Tableau Desktop
  2. Connect → Text File
  3. เลือก Transactions.csv
  4. ลาก Sheet ไปที่ Canvas → Tableau จะ Auto-detect
  5. ทำซ้ำกับ Account_Summary.csv ในอีก Connection

วิธีที่ 2: Join ทั้ง 3 ไฟล์ใน 1 Workbook
  1. Connect → Text File → Transactions.csv
  2. Add Connection → เพิ่ม Account_Summary.csv
  3. Drag Account_Summary ใน Canvas
  4. Join: Transactions.From_Account = Account_Summary.Account_ID

วิธีที่ 3: ใช้แค่ Account_Summary.csv (ง่ายที่สุด)
  - เหมาะสำหรับทำ Boxplot, Bar Chart, Dashboard ทั่วไป
  - ไม่ต้องคำนวณ Aggregation เอง


================================================================
GRAPHS ที่แนะนำให้ทำใน TABLEAU (8 graphs)
================================================================

1. BOXPLOT — Fan-in Count by Layer
   File:    Account_Summary.csv
   Columns: Layer
   Rows:    Fan_In_Count
   Mark:    Box-and-Whisker
   Filter:  เอาเฉพาะ Layer != 'Victim'

2. BOXPLOT — Fan-out Count by Layer
   File:    Account_Summary.csv
   Columns: Layer
   Rows:    Fan_Out_Count

3. HISTOGRAM — Time to Outflow (Hit & Run)
   File:    Account_Summary.csv
   Columns: Avg_Time_To_Outflow_Min (Bin = 5 นาที)
   Rows:    COUNT(Account_ID)
   Color:   Layer
   *** ใส่ Log Scale ที่แกน Y เพื่อให้เห็น Mule ชัดขึ้น

4. SCATTER — Outflow Ratio vs Fan-in Count
   File:    Account_Summary.csv
   Columns: Fan_In_Count
   Rows:    Outflow_Ratio_Pct
   Color:   Is_Mule (0/1)
   Size:    Total_Out_Amount

5. BAR CHART — Layering Detection Rate
   File:    Layering_Detection_Rate.csv
   Columns: Layer
   Rows:    Detection_Rate_Pct
   Color:   ไล่จากเขียว (สูง) → แดง (ต่ำ)

6. BAR CHART — Channel Usage (Normal vs Mule)
   File:    Transactions.csv
   Columns: Channel
   Rows:    COUNT(Transaction_ID)
   Color:   Is_Mule
   Stack:   Side-by-Side

7. HEATMAP — Hour of Day vs Day of Week
   File:    Transactions.csv
   Columns: HOUR(Timestamp)
   Rows:    DAY(Timestamp)
   Color:   COUNT — Filter Is_Mule = 1
   Show:    บัญชีม้ามักทำตอนกลางคืน

8. DASHBOARD — Risk Monitor
   ประกอบด้วย:
   - KPI: COUNT(High_Risk), Detection Rate %, Avg Risk Score
   - Bar: Risk Level Distribution
   - Table: Top 10 Risky Accounts (เรียงตาม Risk_Score)


================================================================
TIPS สำหรับ TABLEAU
================================================================

[Tip 1] Imbalanced Data Visualization
  - บัญชีม้ามีแค่ 5% → ในกราฟปกติจะหายไป
  - ใช้ Log Scale ที่แกน Y
  - หรือ Filter ดูเฉพาะ Mule แล้วเปรียบกับ Normal

[Tip 2] สีที่ Consistent
  - Normal     = #1f77b4 (น้ำเงิน)
  - Watch      = #ff7f0e (ส้ม)
  - High_Risk  = #d62728 (แดง)
  - ใช้สีเดียวกันทุก Sheet/Dashboard

[Tip 3] Format ตัวเลข
  - Amount → Currency (฿)
  - Outflow_Ratio_Pct → Percent
  - Time_To_Outflow_Min → Number with "นาที" suffix

[Tip 4] Filter Action ใน Dashboard
  - คลิกที่ Layer → Filter ทุก Sheet ในหน้านั้น
  - คลิกที่ Account → Show รายละเอียดธุรกรรม


================================================================
การ RE-GENERATE ข้อมูลใหม่
================================================================

ถ้าต้องการสร้างข้อมูลใหม่:
  1. เปิด Terminal/Command Prompt
  2. cd "e:\01\dowload\power bi proeject\05_final"
  3. python generate_data.py

ปรับค่าต่างๆ ได้ในไฟล์ generate_data.py:
  - N_NORMAL_ACC = 950   (จำนวนบัญชีปกติ)
  - N_VICTIMS    = 200   (จำนวนเหยื่อ)
  - N_MULE_L1    = 20    (บัญชีม้าชั้น 1)
  - N_MULE_L2    = 20    (บัญชีม้าชั้น 2)
  - N_MULE_L3    = 10    (บัญชีม้าชั้น 3+)
  - START_DATE / END_DATE


================================================================
VISUAL UPGRADE (ใช้ DATA เดิม 100%)
================================================================

ถ้าต้องการอัปเกรด Visualization โดยไม่เปลี่ยนข้อมูลต้นฉบับ
ให้สร้างตาราง viz mart จากไฟล์เดิมด้วยคำสั่ง:

  1. cd "e:\01\dowload\power bi proeject\05_final\06_visual_pack"
  2. ..\..\.venv\Scripts\python.exe build_visual_marts.py

ไฟล์ที่ถูกสร้างจะอยู่ใน:
  e:\01\dowload\power bi proeject\05_final\data\viz_marts\

ประกอบด้วย:
  - kpi_overview.csv
  - channel_mix_pct.csv
  - hourly_profile.csv
  - layer_performance_extended.csv
  - risk_score_bins.csv
  - rule_trigger_matrix.csv
  - layer_flow_edges.csv
  - false_positive_review.csv
  - threshold_tradeoff_curve.csv

คู่มือการใช้งานอยู่ที่:
  - ..\06_visual_pack\Tableau_Upgrade_Blueprint.md
  - ..\06_visual_pack\Tableau_Calculated_Fields.txt
  - ..\06_visual_pack\Slide_Visual_Mapping.csv


================================================================
แหล่งอ้างอิง (สำหรับ Slide)
================================================================
- FATF (2024) Guidance on Money Mule-related Activity
- BoT — APP Fraud Report 2566
- ปปง. — พ.ร.บ. ป้องกันและปราบปรามการฟอกเงิน พ.ศ. 2542
- UK Finance (2023) Authorised Push Payment Fraud Report

================================================================
