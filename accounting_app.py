import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ Meow Wallet v12.0 (iPhone & Anti-Translate Fix) ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

# ปรับปรุง Style ให้ทนทานต่อการแปลภาษาและโหมดมืดใน iPhone
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    
    /* บังคับสีพื้นหลังและตัวอักษรให้ชัดเจนทุกอุปกรณ์ */
    .stApp { background-color: #FFF5F7 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #2D2D2D !important; /* สีเทาเข้มเกือบดำ อ่านง่ายกว่าสีดำสนิท */
    }
    
    .main-title { color: #FF69B4; text-align: center; font-size: clamp(24px, 5vw, 45px); font-weight: bold; padding: 10px; }
    
    /* ปรับแต่งปุ่มและกล่องข้อมูล */
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 15px; }
    .report-card { background-color: white; padding: 20px; border-radius: 15px; border-top: 5px solid #FF69B4; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    
    /* ซ่อนไอคอนแปลภาษาไม่ให้กวนใจในมือถือ */
    .translated-ltr { margin-top: 0 !important; }
    .goog-te-banner-frame { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฐานข้อมูล ---
conn = sqlite3.connect('meow_ultimate_v12.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. Sidebar ---
st.sidebar.markdown("<h2 style='text-align: center;'>🐱 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", value="วราศิณี") # ใส่ชื่อเริ่มต้นให้ตามภาพ

if not user_name:
    st.markdown("<div class='main-title'>🐾 Meow Wallet Ultimate</div>", unsafe_allow_html=True)
    st.info("กรุณาใส่ชื่อที่แถบด้านซ้ายนะเมี๊ยวว!")
    st.stop()

# --- 4. ดึงข้อมูล ---
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0
net_balance = total_in - total_out - total_save

# --- 5. Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกรายการ (คุณ {user_name})")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายรับ 💰", "รายจ่าย 💸", "เงินออม 🐷"], horizontal=True)
    
    with col2:
        if type_in == "รายรับ 💰":
            cat_list = ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"]
        elif type_in == "รายจ่าย 💸":
            cat_list = ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"]
        else:
            cat_list = ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]
            
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_list)
        
        final_category = selected_cat
        if selected_cat == "อื่นๆ ➕":
            final_category = st.text_input("✍️ ระบุชื่อหมวดหมู่เอง", placeholder="เช่น ค่าอาบน้ำแมว...")
            
        sub_cat_in = st.text_input("📝 รายละเอียด", placeholder="พิมพ์โน้ตกันลืม...")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!", use_container_width=True):
        if amt_in > 0 and final_category != "":
            inc, exp, sav = (amt_in, 0, 0) if type_in == "รายรับ 💰" else (0, amt_in, 0) if type_in == "รายจ่าย 💸" else (0, 0, amt_in)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_category, sub_cat_in, inc, exp, sav))
            conn.commit()
            st.success("บันทึกเรียบร้อยเมี๊ยวว!")
            st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดเงินในมือ")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp, SUM(savings) as sav FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    c_wallets = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        row = df_w[df_w['wallet'] == w_name]
        bal = row['inc'].sum() - row['exp'].sum() - row['sav'].sum() if not row.empty else 0.0
        c_wallets[i].metric(w_name, f"{bal:,.2f} ฿")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_show = df.sort_values(by=['date', 'id'], ascending=[False, False])
        st.dataframe(df_show[['date', 'wallet', 'category', 'sub_category', 'income', 'expense', 'savings']], use_container_width=True)
        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลด CSV สำรองข้อมูล", data=csv, file_name=f'meow_backup_{user_name}.csv')
    else:
        st.write("ยังไม่มีข้อมูลเมี๊ยวว เริ่มบันทึกก่อนนะ!")

st.sidebar.markdown("---")
st.sidebar.write("🐱 *Meow Wallet v12.0*")
