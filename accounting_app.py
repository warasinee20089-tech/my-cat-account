import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ Meow Wallet (ธีมพาสเทล) ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

def play_audio(url):
    """ฟังก์ชันเล่นเสียง"""
    st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# ปรับแต่ง CSS ให้เป็นสีชมพูพาสเทลและฟอนต์น่ารักๆ
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF0F5; }
    .main-title { color: #FF69B4; text-align: center; font-size: 60px; font-weight: bold; text-shadow: 3px 3px #FFE4E1; padding: 20px; }
    
    /* ตกแต่งปุ่มกด */
    .stButton>button { 
        background: linear-gradient(45deg, #FFB7C5, #FF99AC); 
        color: white; border-radius: 30px; border: 3px solid #FFFFFF; 
        font-size: 22px; font-weight: bold; width: 100%; height: 60px;
        box-shadow: 0 4px 15px rgba(255, 183, 197, 0.4);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(255, 153, 172, 0.5); color: white !important; }
    
    /* ตกแต่งกล่องตัวเลข */
    div[data-testid="stMetric"] { background: white; border-radius: 20px; border: 2px solid #FFD1DC; padding: 15px; }
    
    /* ปรับแต่ง Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #FFFFFF; border-radius: 15px 15px 0 0; padding: 10px 20px; color: #D87093; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_emoji_v1.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. หน้าแรก (ใช้อิโมจิน่ารักๆ) ---
st.sidebar.markdown("<h2 style='text-align: center; color: #D87093;'>🎀 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อเจ้าของกระเป๋า", placeholder="กรอกชื่อเล่นตรงนี้จ้า...")

if not user_name:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #DB7093;'>ยินดีต้อนรับ! กรุณาใส่ชื่อที่แถบด้านซ้าย<br>เพื่อเริ่มบันทึกความสุขและการเงินนะเมี๊ยวว!</h3>", unsafe_allow_html=True)
    play_audio("https://www.myinstants.com/media/sounds/kawaii-desu-ne.mp3")
    st.stop()

# --- 4. เมนู Tabs (ใช้ไอคอนอิโมจิ) ---
tab1, tab2, tab3 = st.tabs(["🍓 บันทึกรายวัน", "🍩 สรุปยอด", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### 🧸 สมุดบันทึกของ คุณ{user_name}")
    col1, col2 = st.columns([1, 2])
    with col1:
        # ใช้ Emoji ตัวใหญ่ๆ แทนรูปภาพที่โหลดไม่ขึ้น
        st.markdown("<h1 style='text-align: center; font-size: 120px;'>🐈‍⬛<br>💸</h1>", unsafe_allow_html=True)
    with col2:
        date_in = st.date_input("📅 วันที่", datetime.now())
        type_in = st.radio("✨ ประเภทเงิน", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
        cat_in = st.text_input("🏷️ หมวดหมู่ (พิมพ์เองได้เลย)", placeholder="เช่น ค่าปลาทู, ค่าขนม")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)
        
    if st.button("💖 บันทึกรายการเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, income, expense) VALUES (?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, inc, exp))
            conn.commit()
            
            play_audio("https://www.myinstants.com/media/sounds/cat-meow.mp3")
            st.balloons()
            st.success(f"บันทึก '{cat_in}' เรียบร้อยแล้วจ้า! 🐾")
            st.rerun()

with tab2:
    st.markdown("### 📊 สรุปยอดเงิน")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        t_in, t_out = df['income'].sum(), df['expense'].sum()
        c1.metric("💰 รายรับรวม", f"{t_in:,.2f} ฿")
        c2.metric("💸 รายจ่ายรวม", f"{t_out:,.2f} ฿")
        c3.metric("🐾 คงเหลือสุทธิ", f"{t_in-t_out:,.2f} ฿")
        
        st.write("---")
        fig = px.pie(df[df['expense']>0], values='expense', names='category', 
                     hole=0.4, title="🍩 สัดส่วนค่าใช้จ่าย",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>📭</h1>", unsafe_allow_html=True)
        st.info("ยังไม่มีข้อมูลบันทึกนะเมี๊ยวว")

with tab3:
    st.markdown("### 📖 ประวัติการบันทึก")
    df_h = pd.read_sql(f"SELECT date as วันที่, category as หมวดหมู่, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC", conn)
    if not df_h.empty:
        st.dataframe(df_h, use_container_width=True)
    else:
        st.write("ประวัติยังว่างเปล่า...")

# ตกแต่ง Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<h1 style='text-align: center;'>🐱💖</h1>", unsafe_allow_html=True)
st.sidebar.write("<center>Meow Wallet v1.0</center>", unsafe_allow_html=True)
