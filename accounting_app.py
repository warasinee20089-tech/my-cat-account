import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ & สไตล์ (โทนชมพูตามรูป) ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF0F5; }
    .main-title { color: #FF69B4; text-align: center; font-size: 50px; font-weight: bold; text-shadow: 2px 2px #FFE4E1; padding: 10px; }
    .stButton>button { background: linear-gradient(45deg, #FFB7C5, #FF99AC); color: white; border-radius: 25px; border: 2px solid #FFF; font-size: 18px; width: 100%; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.03); border: 2px solid #FF69B4; }
    div[data-testid="stMetric"] { background: white; border-radius: 15px; border: 2px solid #FFD1DC; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

def play_audio(url):
    st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_final_v1.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. ส่วน Login และน้องแมว (ใช้ SVG เพื่อให้แสดงผลแน่นอน) ---
st.sidebar.markdown("<h2 style='text-align: center; color: #D87093;'>🐾 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมวคนเก่ง", placeholder="กรอกชื่อที่นี่...")

if not user_name:
    st.markdown("<div class='main-title'>Meow Wallet</div>", unsafe_allow_html=True)
    # ใช้รูปแมวน่ารักแบบ SVG (แสดงผลได้แน่นอนทุกเครื่อง)
    st.markdown("""
        <center>
        <svg width="200" height="200" viewBox="0 0 200 200">
            <circle cx="100" cy="110" r="70" fill="#FFB7C5" />
            <circle cx="70" cy="90" r="10" fill="white" />
            <circle cx="130" cy="90" r="10" fill="white" />
            <path d="M 80 130 Q 100 150 120 130" stroke="white" stroke-width="5" fill="none" />
            <polygon points="40,60 70,80 30,100" fill="#FFB7C5" />
            <polygon points="160,60 130,80 170,100" fill="#FFB7C5" />
        </svg>
        <h3 style='color: #DB7093;'>กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเริ่มออมเงินนะเมี๊ยวว!</h3>
        </center>
    """, unsafe_allow_html=True)
    play_audio("https://www.myinstants.com/media/sounds/kawaii-desu-ne.mp3")
    st.stop()

# --- 4. เมนู Tabs ---
tab1, tab2, tab3 = st.tabs(["🐱 บันทึกรายวัน", "📊 สรุปยอด", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกของ {user_name}")
    col1, col2 = st.columns([1, 2])
    with col1:
        # ใช้รูปแมวเต้นจากแหล่งที่เสถียรที่สุด
        st.markdown("<img src='https://www.icegif.com/wp-content/uploads/2023/01/icegif-162.gif' width='100%'>", unsafe_allow_html=True)
    with col2:
        date_in = st.date_input("วันที่", datetime.now())
        type_in = st.radio("ประเภท", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
        cat_in = st.text_input("🏷️ หมวดหมู่ (พิมพ์เองได้เลย)", placeholder="เช่น ค่าขนม, ของเล่น")
        amt_in = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=1.0)
        
    if st.button("🐾 กดบันทึกเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, income, expense) VALUES (?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, inc, exp))
            conn.commit()
            play_audio("https://www.myinstants.com/media/sounds/cat-meow.mp3")
            st.balloons()
            st.success("บันทึกเรียบร้อยแล้วจ้า! 🎉")
            st.rerun()

with tab2:
    st.markdown("### 📊 สรุปยอด")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        t_in, t_out = df['income'].sum(), df['expense'].sum()
        c1.metric("💰 รายรับ", f"{t_in:,.2f}")
        c2.metric("💸 รายจ่าย", f"{t_out:,.2f}")
        c3.metric("🐾 คงเหลือ", f"{t_in-t_out:,.2f}")
        
        fig = px.pie(df[df['expense']>0], values='expense', names='category', 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("ยังไม่มีข้อมูลนะเมี๊ยวว")

with tab3:
    st.markdown("### 📖 ประวัติ")
    df_h = pd.read_sql(f"SELECT date as วันที่, category as รายการ, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC", conn)
    st.dataframe(df_h, use_container_width=True)
