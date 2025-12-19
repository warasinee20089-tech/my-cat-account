import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ (เปลี่ยนชื่อแอปและปรับแต่งดีไซน์) ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF5F7 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #2D2D2D !important;
    }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; padding: 20px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล (v15) ---
conn = sqlite3.connect('meow_wallet_v15.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. ระบบ Login Session ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- หน้าแรก: Login Page (เปลี่ยนชื่อเป็น 🐾 Meow Wallet 🐾) ---
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱</h1>", unsafe_allow_html=True)
        name_input = st.text_input("ยินดีต้อนรับทาสแมว! กรุณากรอกชื่อของคุณ:", placeholder="ระบุชื่อที่นี่...", key="login_name")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_input.strip() != "":
                st.session_state.user_name = name_input
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("กรุณาใส่ชื่อก่อนนะเมี๊ยวว!")
    st.stop()

# --- หน้าหลัก: หลังจากล็อคอิน ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

# คำนวณยอดเงิน
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

st.markdown(f"<div class='main-title'>🐾 Meow Wallet ของ {user_name} 🐾</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติ"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
    with col2:
        # ระบบหมวดหมู่ตามประเภท (ฟังก์ชันเดิมที่ต้องการ)
        if type_in == "รายรับ 💰":
            cat_list = ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"]
        elif type_in == "รายจ่าย 💸":
            cat_list = ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"]
        else:
            cat_list = ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]
        
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_list)
        final_category = selected_cat
        # ระบบเพิ่มหมวดหมู่เอง (ฟังก์ชันเดิมที่ต้องการ)
        if selected_cat == "อื่นๆ ➕":
            final_category = st.text_input("✍️ ระบุชื่อหมวดหมู่เอง")
            
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
    st.markdown("### 🏦 ยอดเงินคงเหลือ")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp, SUM(savings) as sav FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    c_wallets = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        row = df_w[df_w['wallet'] == w_name]
        bal = row['inc'].sum() - row['exp'].sum() - row['sav'].sum() if not row.empty else 0.0
        c_wallets[i].metric(w_name, f"{bal:,.2f} ฿")

with tab4:
    st.markdown("### 🎯 สถานะการออม")
    st.metric("💰 เงินออมสะสม", f"{total_save:,.2f} ฿")
    # แก้ไข Error สีแดง (Division by Zero Fix)
    if total_in > 0:
        progress = min(total_save / total_in, 1.0)
        st.write(f"คุณออมไปแล้ว {progress*100:.1f}% ของรายรับ")
        st.progress(progress)
    else:
        st.info("ระบบจะเริ่มคำนวณแถบการออม เมื่อคุณมียอด 'รายรับ' เข้ามานะเมี๊ยวว!")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_show = df.sort_values(by=['date', 'id'], ascending=[False, False])
        st.dataframe(df_show[['date', 'wallet', 'category', 'sub_category', 'income', 'expense', 'savings']], use_container_width=True)
        # ฟังก์ชัน Download CSV (ฟังก์ชันเดิมที่ต้องการ)
        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลด CSV สำรองข้อมูล", data=csv, file_name=f'meow_wallet_{user_name}.csv', use_container_width=True)
    else:
        st.write("ยังไม่มีข้อมูลเมี๊ยวว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ (สลับทาสแมว)"):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.rerun()
