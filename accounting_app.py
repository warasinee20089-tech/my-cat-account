import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Meow Accounting (Private)", layout="wide", page_icon="🐱")

# --- ระบบ Login ง่ายๆ ---
st.sidebar.markdown("### 🔐 เข้าสู่ระบบเมี๊ยวว")
user_key = st.sidebar.text_input("กรอกชื่อผู้ใช้ (เพื่อแยกกระเป๋าเงิน)", type="password")

if not user_key:
    st.markdown("<h1>🐱 ยินดีต้อนรับสู่ Meow Accounting</h1>", unsafe_allow_html=True)
    st.info("กรุณากรอกชื่อผู้ใช้ที่แถบด้านซ้าย เพื่อเริ่มใช้งานแบบส่วนตัวนะเมี๊ยวว!")
    st.stop()

# --- CSS โทนพาสเทล ---
st.markdown(f"""
    <style>
    .main {{ background-color: #FFF5F7; }}
    .stButton>button {{ background-color: #FFB7C5; color: white; border-radius: 20px; border: none; }}
    .record-box {{ background-color: #FFD1DC; color: #D87093; padding: 15px; border-radius: 20px; text-align: center; font-weight: bold; }}
    h1 {{ color: #D87093; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- ระบบฐานข้อมูล (เพิ่มคอลัมน์ user_id) ---
conn = sqlite3.connect('wallet_private.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS my_records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, desc TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0, is_debt INTEGER DEFAULT 0)''')
conn.commit()

# --- เมนูหลัก ---
menu = st.sidebar.radio(f"สวัสดีคุณ {user_key} 🐾", ["🐾 บันทึกรายรับ รายจ่าย", "📊 สรุปยอด Meow"])

if menu == "🐾 บันทึกรายรับ รายจ่าย":
    st.markdown(f"<h1>🌸 บันทึกของ {user_key} 🌸</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
    with col1: d_in = st.date_input("วันที่", datetime.now())
    with col2: desc_in = st.text_input("รายการ")
    with col3: type_in = st.selectbox("ประเภท", ["รายจ่าย", "รายรับ", "หนี้สิน"])
    with col4: amt_in = st.number_input("จำนวนเงิน (฿)", min_value=0.0)
    
    if st.button("🐾 บันทึกรายการ"):
        if desc_in and amt_in > 0:
            inc, exp, debt = (amt_in, 0, 0) if type_in == "รายรับ" else (0, amt_in, 0) if type_in == "รายจ่าย" else (amt_in, 0, 1)
            c.execute("INSERT INTO my_records (user_id, date, desc, income, expense, is_debt) VALUES (?,?,?,?,?,?)", 
                      (user_key, d_in.strftime('%Y-%m-%d'), desc_in, inc, exp, debt))
            conn.commit()
            st.success("บันทึกสำเร็จ!")
            st.rerun()

    st.write("---")
    st.markdown("### 📋 ช่องรายการของคุณ")
    # ดึงเฉพาะข้อมูลของ user_key นี้เท่านั้น
    df = pd.read_sql(f"SELECT id, date as วันที่, desc as รายการ, income as รายรับ, expense as รายจ่าย FROM my_records WHERE user_id='{user_key}' ORDER BY id DESC", conn)
    if not df.empty:
        st.table(df[['วันที่', 'รายการ', 'รายรับ', 'รายจ่าย']])
    else:
        st.info("ยังไม่มีข้อมูลบันทึกเมี๊ยวว")

elif menu == "📊 สรุปยอด Meow":
    st.markdown(f"<h1>📈 ภาพรวมของ {user_key}</h1>", unsafe_allow_html=True)
    df = pd.read_sql(f"SELECT * FROM my_records WHERE user_id='{user_key}'", conn)
    if not df.empty:
        t_inc, t_exp = df['income'].sum(), df['expense'].sum()
        st.metric("💰 คงเหลือสุทธิ", f"{t_inc-t_exp:,.2f} ฿")
        # แสดงกราฟเฉพาะของผู้ใช้
        fig = px.bar(df, x='date', y=['income','expense'], barmode='group', color_discrete_sequence=['#FFB7C5', '#98FB98'])
        st.plotly_chart(fig, use_container_width=True)

