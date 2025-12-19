import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ v13.0 (Separated Login Page) ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF5F7 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #2D2D2D !important;
    }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; padding: 20px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; }
    .login-box { background-color: white; padding: 40px; border-radius: 20px; border: 3px solid #FF69B4; text-align: center; max-width: 500px; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_ultimate_v13.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. ระบบจัดการ Session (ล็อคอิน) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- หน้าแรก: Login Page ---
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet Ultimate</div>", unsafe_allow_html=True)
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

# --- หน้าหลัก: หลังจากล็อคอินแล้ว ---
user_name = st.session_state.user_name

# ดึงข้อมูล
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0
net_balance = total_in - total_out - total_save

st.markdown(f"<div class='main-title'>🐾 กระเป๋าของ {user_name}</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติ"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
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
            final_category = st.text_input("✍️ ระบุหมวดหมู่เอง")
            
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

with tab5:
    st.markdown("### 📖 ประวัติย้อนหลัง")
    if not df.empty:
        st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 สำรองข้อมูลเป็น CSV", data=csv, file_name=f'meow_{user_name}.csv')
    else:
        st.write("ยังไม่มีรายการบันทึกครับ")

# ปุ่มออกจากระบบด้านล่างสุด
st.markdown("---")
if st.button("🚪 ออกจากระบบ (เปลี่ยนผู้ใช้งาน)"):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.rerun()
