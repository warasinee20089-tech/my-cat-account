import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import base64

# --- 1. การตั้งค่าหน้าเว็บ & สไตล์ ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

def play_audio(url):
    """ฟังก์ชันสำหรับเล่นเสียงจาก URL"""
    md = f"""
        <audio autoplay>
        <source src="{url}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #FFF5F7 0%, #F0F8FF 100%); }
    .main-title { color: #FF69B4; text-align: center; font-size: 50px; font-weight: bold; text-shadow: 2px 2px #FFE4E1; }
    .stButton>button { background: linear-gradient(45deg, #FFB7C5, #FF99AC); color: white; border-radius: 25px; border: none; font-size: 18px; transition: 0.3s; width: 100%; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 10px 20px rgba(255, 153, 172, 0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_wallet_v9.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. ส่วนชื่อผู้ใช้งาน ---
st.sidebar.markdown("<h2 style='text-align: center; color: #D87093;'>🐾 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("กรอกชื่อเล่นเจ้าของเมี๊ยว", placeholder="เช่น มี๊ของน้องแมว")

if not user_name:
    st.markdown("<div class='main-title'>Meow Wallet</div>", unsafe_allow_html=True)
    # แมวดุ๊กดิ๊ก
    st.markdown("<center><img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHR4MmtqbmFnd3JpZzB4bmN0Z2RzZ3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/JpGf6pGvUuM8e6pX5l/giphy.gif' width='300'></center>", unsafe_allow_html=True)
    st.info("กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเปิดกระเป๋าเงินนะเมี๊ยวว!")
    # เสียงต้อนรับ
    play_audio("https://www.myinstants.com/media/sounds/kawaii-desu-ne.mp3")
    st.stop()

# --- 4. เมนู Tabs ---
tab1, tab2, tab3 = st.tabs(["🐱 บันทึกรายวัน", "📊 สรุปยอด", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกของ {user_name}")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJieW5pbmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/33p1YvO6S02Uolv0Hn/giphy.gif' width='200'>", unsafe_allow_html=True)
    with col2:
        date_in = st.date_input("เลือกวันที่", datetime.now())
        type_in = st.radio("ประเภท", ["รายจ่าย", "รายรับ"], horizontal=True)
        cat_in = st.text_input("🏷️ หมวดหมู่ (พิมพ์เองได้เลย)", placeholder="เช่น ค่าขนม, ค่าเดินทาง")
        amt_in = st.number_input("จำนวนเงิน (บาท)", min_value=0.0)
        
    if st.button("🐾 กดบันทึกเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if type_in == "รายรับ" else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, income, expense) VALUES (?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, inc, exp))
            conn.commit()
            
            # เล่นเสียงเมี๊ยวตอนบันทึกสำเร็จ
            play_audio("https://www.myinstants.com/media/sounds/cat-meow.mp3")
            st.balloons()
            st.success("บันทึกสำเร็จแล้วจ้า! 🎉")
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
                     title="🍩 สัดส่วนค่าใช้จ่าย", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("ยังไม่มีข้อมูลสรุปนะเมี๊ยวว")

with tab3:
    st.markdown("### 📖 ประวัติการบันทึก")
    df_history = pd.read_sql(f"SELECT date as วันที่, category as หมวดหมู่, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC", conn)
    st.dataframe(df_history, use_container_width=True)

# เพิ่มแมวดุ๊กดิ๊กที่ Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<center><img src='https://media.giphy.com/media/S67v8V0D0M8X5f3k6v/giphy.gif' width='100'></center>", unsafe_allow_html=True)
