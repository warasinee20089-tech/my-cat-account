import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ Meow Wallet ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

def play_audio(url):
    """ฟังก์ชันเล่นเสียง"""
    st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# ปรับแต่งความน่ารักด้วยสีพาสเทล
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 55px; font-weight: bold; text-shadow: 3px 3px #FFE4E1; padding: 10px; }
    .stButton>button { 
        background: linear-gradient(45deg, #FFB7C5, #FF99AC); 
        color: white; border-radius: 30px; border: 3px solid #FFFFFF; 
        font-size: 20px; font-weight: bold; width: 100%; height: 50px;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(255, 153, 172, 0.4); color: white !important; }
    div[data-testid="stMetric"] { background: white; border-radius: 20px; border: 2px solid #FFD1DC; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_stable_vfinal.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. ส่วนชื่อเจ้าของ และน้องแมวดุ๊กดิ๊กหน้าแรก ---
st.sidebar.markdown("<h2 style='text-align: center; color: #D87093;'>🐈 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", placeholder="กรอกชื่อตรงนี้จ้า...")

if not user_name:
    st.markdown("<div class='main-title'>Meow Wallet</div>", unsafe_allow_html=True)
    # ใช้ลิงก์แมวขยับได้ที่เสถียรที่สุดจาก Cloudinary
    st.markdown("<center><img src='https://res.cloudinary.com/dz97rq9nm/image/upload/v1683456789/cat-space.gif' width='300'></center>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #DB7093;'>ใส่ชื่อที่แถบด้านซ้ายเพื่อเริ่มออมเงินนะเมี๊ยวว!</h4>", unsafe_allow_html=True)
    play_audio("https://www.myinstants.com/media/sounds/kawaii-desu-ne.mp3")
    st.stop()

# --- 4. เมนู Tabs ---
tab1, tab2, tab3 = st.tabs(["📝 บันทึกรายวัน", "📊 สรุปยอด", "📖 ประวัติ"])

with tab1:
    col1, col2 = st.columns([1, 1.5])
    with col1:
        # แมวขยับได้หน้าบันทึก (น้องแมวเต้นเขย่าพุง)
        st.markdown("<img src='https://res.cloudinary.com/dz97rq9nm/image/upload/v1683456789/cute-cat-dance.gif' width='220'>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### ✨ บันทึกของ {user_name}")
        date_in = st.date_input("วันที่", datetime.now())
        type_in = st.radio("ประเภทเงิน", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
        cat_in = st.text_input("🏷️ หมวดหมู่", placeholder="เช่น ค่าปลาทู, ค่ากาแฟ")
        amt_in = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=1.0)
        
    if st.button("🐾 บันทึกรายการเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, income, expense) VALUES (?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, inc, exp))
            conn.commit()
            
            play_audio("https://www.myinstants.com/media/sounds/cat-meow.mp3")
            st.balloons()
            st.success(f"บันทึก '{cat_in}' เรียบร้อยแล้วเมี๊ยวว!")
            st.rerun()

with tab2:
    st.markdown("### 📊 สรุปยอด")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        t_in, t_out = df['income'].sum(), df['expense'].sum()
        c1.metric("🎀 รายรับ", f"{t_in:,.2f}")
        c2.metric("🍭 รายจ่าย", f"{t_out:,.2f}")
        c3.metric("🍦 คงเหลือ", f"{t_in-t_out:,.2f}")
        
        fig = px.pie(df[df['expense']>0], values='expense', names='category', 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลนะเมี๊ยวว")

with tab3:
    st.markdown("### 📖 ประวัติการบันทึก")
    df_h = pd.read_sql(f"SELECT date as วันที่, category as หมวดหมู่, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC", conn)
    st.dataframe(df_h, use_container_width=True)

# แถบด้านข้างตกแต่งเพิ่ม
st.sidebar.markdown("---")
st.sidebar.markdown("<center><img src='https://media.tenor.com/On7_5rl7S4AAAAAi/loading-cat.gif' width='80'></center>", unsafe_allow_html=True)
st.sidebar.write("<center>Meow Wallet 💖</center>", unsafe_allow_html=True)
