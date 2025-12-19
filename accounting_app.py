import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ (ธีมพาสเทลแมว) ---
st.set_page_config(page_title="Meow Accounting (Private)", layout="wide", page_icon="🐱")

# --- 2. ระบบ Login ส่วนตัว (แยกข้อมูลตามชื่อ) ---
st.sidebar.markdown("### 🔐 เข้าสู่ระบบเมี๊ยวว")
user_name = st.sidebar.text_input("กรอกชื่อเล่น (เพื่อแยกกระเป๋าเงิน)", placeholder="เช่น Cat_Owner")

if not user_name:
    st.markdown("<h1 style='text-align: center; color: #D87093;'>🐱 ยินดีต้อนรับสู่ Meow Accounting</h1>", unsafe_allow_html=True)
    st.info("กรุณากรอกชื่อเล่นที่แถบด้านซ้าย เพื่อเริ่มใช้งานแบบส่วนตัวนะเมี๊ยวว!")
    st.stop()

# --- 3. ตกแต่งความสวยงาม (CSS พาสเทล) ---
st.markdown(f"""
    <style>
    .main {{ background-color: #FFF5F7; }}
    .stButton>button {{ background-color: #FFB7C5; color: white; border-radius: 20px; border: none; width: 100%; }}
    .stButton>button:hover {{ background-color: #FFD1DC; color: #D87093; }}
    h1, h2, h3 {{ color: #D87093; text-align: center; font-family: 'Kanit', sans-serif; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. จัดการฐานข้อมูล (SQLite) ---
conn = sqlite3.connect('cat_wallet_v4.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, desc TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 5. เมนูการใช้งาน ---
st.sidebar.success(f"สวัสดีคุณ {user_name} 🐾")
menu = st.sidebar.radio("เลือกเมนูเมี๊ยวว", ["🐾 บันทึกรายรับ/จ่าย", "📊 สรุปภาพรวม"])

if menu == "🐾 บันทึกรายรับ/จ่าย":
    st.markdown(f"<h1>🌸 บันทึกของ {user_name} 🌸</h1>", unsafe_allow_html=True)
    
    # ส่วนรับข้อมูล
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        with col1: d_in = st.date_input("วันที่", datetime.now())
        with col2: desc_in = st.text_input("รายการ (เช่น ค่าปลาทู)")
        with col3: type_in = st.selectbox("ประเภท", ["รายจ่าย", "รายรับ"])
        with col4: amt_in = st.number_input("จำนวนเงิน (฿)", min_value=0.0, step=1.0)
        
        if st.button("🐾 บันทึกรายการลงกระเป๋า"):
            if desc_in and amt_in > 0:
                inc, exp = (amt_in, 0) if type_in == "รายรับ" else (0, amt_in)
                c.execute("INSERT INTO records (user_id, date, desc, income, expense) VALUES (?,?,?,?,?)", 
                          (user_name, d_in.strftime('%Y-%m-%d'), desc_in, inc, exp))
                conn.commit()
                st.toast(f"บันทึก {desc_in} เรียบร้อยแล้วเมี๊ยวว!", icon='✅')
                st.rerun()

    st.write("---")
    
    # --- ส่วนแสดงตารางพร้อม "ยอดคงเหลือ" ---
    st.markdown("### 📋 ตารางบันทึกของคุณ")
    # ดึงข้อมูลจากฐานข้อมูล (เรียงตามวันที่จากเก่าไปใหม่เพื่อคำนวณยอดสะสม)
    df = pd.read_sql(f"SELECT date as วันที่, desc as รายการ, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date ASC, id ASC", conn)
    
    if not df.empty:
        # คำนวณช่องคงเหลือ (Cumulative Sum)
        df['คงเหลือ'] = df['รายรับ'].cumsum() - df['รายจ่าย'].cumsum()
        
        # จัดรูปแบบตัวเลขให้สวยงาม
        df_styled = df.style.format({"รายรับ": "{:,.2f}", "รายจ่าย": "{:,.2f}", "คงเหลือ": "{:,.2f}"})
        
        # แสดงตาราง (กลับด้านให้รายการล่าสุดอยู่บนสุด)
        st.table(df.iloc[::-1])
    else:
        st.info("ยังไม่มีข้อมูลบันทึกในชื่อนี้เมี๊ยวว ลองกรอกข้อมูลด้านบนดูนะ!")

elif menu == "📊 สรุปภาพรวม":
    st.markdown(f"<h1>📈 ภาพรวมการเงินของ {user_name}</h1>", unsafe_allow_html=True)
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    
    if not df.empty:
        t_inc, t_exp = df['income'].sum(), df['expense'].sum()
        balance = t_inc - t_exp
        
        # แสดงยอดสรุปแบบ Card
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 รายรับรวม", f"{t_inc:,.2f} ฿")
        m2.metric("💸 รายจ่ายรวม", f"{t_exp:,.2f} ฿")
        m3.metric("🐾 คงเหลือสุทธิ", f"{balance:,.2f} ฿")
        
        # กราฟแท่งเปรียบเทียบ
        fig = px.bar(df, x='date', y=['income', 'expense'], 
                     title="กราฟรายวัน",
                     labels={'value': 'จำนวนเงิน (฿)', 'date': 'วันที่', 'variable': 'ประเภท'},
                     color_discrete_sequence=['#FFB7C5', '#98FB98'],
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลให้ทำสรุปเมี๊ยวว ไปบันทึกข้อมูลก่อนนะ!")
