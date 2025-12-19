import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import time

# --- 1. การตั้งค่าหน้าเว็บ & สไตล์พาสเทลขั้นสุด ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    
    /* พื้นหลังพาสเทลแบบนุ่มนวล */
    .stApp {
        background: linear-gradient(135deg, #FFF5F7 0%, #F0F8FF 100%);
    }

    /* ตกแต่งหัวข้อ Meow Wallet */
    .main-title {
        color: #FF69B4;
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        text-shadow: 3px 3px #FFE4E1;
        margin-bottom: 10px;
    }

    /* ปุ่มกดมี Effect เมื่อเอาเมาส์วาง */
    .stButton>button {
        background: linear-gradient(45deg, #FFB7C5, #FF99AC);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 25px;
        font-size: 20px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 10px 20px rgba(255, 153, 172, 0.4);
    }

    /* ปรับแต่งตารางและกล่องตัวเลข */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 20px;
        border: 2px solid #FFD1DC;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_final_v7.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              desc TEXT, income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. ส่วน Sidebar และการเข้าชื่อ ---
st.sidebar.markdown("<h2 style='text-align: center; color: #D87093;'>🐾 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("กรอกชื่อเล่นเจ้าของเมี๊ยว", placeholder="เช่น มี๊ของน้องแมว")

if not user_name:
    st.markdown("<div class='main-title'>Meow Wallet</div>", unsafe_allow_html=True)
    # แมวดุ๊กดิ๊กตอนยังไม่เข้าชื่อ
    st.markdown("<center><img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJieW5pbmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5bmZ5JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/33p1YvO6S02Uolv0Hn/giphy.gif' width='300'></center>", unsafe_allow_html=True)
    st.info("กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเปิดกระเป๋าเงินนะเมี๊ยวว!")
    st.stop()

# --- 4. เมนู Tabs (เปลี่ยนชื่อตามสั่ง) ---
tab1, tab2, tab3 = st.tabs(["🐱 บันทึกรายวัน", "📊 สรุปยอด", "📖 ประวัติ"])

with tab1:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        # แมวขยับได้ในหน้าบันทึก
        st.markdown("<img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHR4MmtqbmFnd3JpZzB4bmN0Z2RzZ3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/JpGf6pGvUuM8e6pX5l/giphy.gif' width='200'>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### ✨ บันทึกของ {user_name}")
        date_in = st.date_input("เลือกวันที่", datetime.now())
        type_in = st.radio("ประเภท", ["รายจ่าย", "รายรับ"], horizontal=True)
        cat_in = st.text_input("🏷️ หมวดหมู่ (พิมพ์เองได้เลย)", placeholder="เช่น ค่าปลาทู, ค่าของเล่น")
        amt_in = st.number_input("จำนวนเงิน (บาท)", min_value=0.0)
        
    if st.button("🐾 กดบันทึกเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if type_in == "รายรับ" else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, desc, income, expense) VALUES (?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, "", inc, exp))
            conn.commit()
            # เอฟเฟกต์ลูกเล่น
            st.balloons() 
            st.snow()
            st.success("บันทึกสำเร็จ! เก่งมากเจ้าทาส 🐈")
            time.sleep(1)
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
        
        st.write("---")
        # กราฟวงกลมพาสเทล
        fig = px.pie(df[df['expense']>0], values='expense', names='category', 
                     title="🍩 สัดส่วนค่าใช้จ่าย",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("<center><img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ4MmtqbmFnd3JpZzB4bmN0Z2RzZ3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/VbnUQpnihPSIgIXOnv/giphy.gif' width='200'></center>", unsafe_allow_html=True)
        st.info("ยังไม่มีข้อมูลเลยเมี๊ยวว")

with tab3:
    st.markdown("### 📖 ประวัติการใช้เงิน")
    df_history = pd.read_sql(f"SELECT date as วันที่, category as หมวดหมู่, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC, id DESC", conn)
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True)
    else:
        st.write("สมุดยังว่างอยู่เลย...")

# สติ๊กเกอร์แมวขยับได้ที่แถบ Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<center><img src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHR4MmtqbmFnd3JpZzB4bmN0Z2RzZ3R6Z3R6Z3R6Z3R6Z3R6Z3R6Z3R6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/S67v8V0D0M8X5f3k6v/giphy.gif' width='100'></center>", unsafe_allow_html=True)
st.sidebar.write("<center>Meow Wallet v7.0</center>", unsafe_allow_html=True)
