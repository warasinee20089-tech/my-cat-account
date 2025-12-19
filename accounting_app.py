import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ Meow Wallet (Cute Emoji Edition) ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐱")

def play_audio(url):
    """ฟังก์ชันสำหรับเล่นเสียงเอฟเฟกต์"""
    st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# ปรับแต่ง CSS โทนพาสเทลชมพู-ขาว เน้นความมุ้งมิ้ง
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 55px; font-weight: bold; text-shadow: 2px 2px #FFE4E1; padding: 20px; }
    
    /* ตกแต่งปุ่มกด */
    .stButton>button { 
        background: linear-gradient(45deg, #FFB7C5, #FF99AC); 
        color: white; border-radius: 30px; border: 3px solid #FFFFFF; 
        font-size: 22px; font-weight: bold; width: 100%; height: 60px;
        box-shadow: 0 4px 15px rgba(255, 183, 197, 0.4);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(255, 153, 172, 0.5); color: white !important; }
    
    /* ตกแต่งกล่องตัวเลขยอดเงิน */
    div[data-testid="stMetric"] { background: white; border-radius: 20px; border: 2px solid #FFD1DC; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_wallet_final_emoji.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. หน้าแรก (ใช้ Emoji แมวเหลืองและเงิน) ---
st.sidebar.markdown("<h2 style='text-align: center; color: #D87093;'>🐾 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", placeholder="กรอกชื่อของคุณ...")

if not user_name:
    st.markdown("<div class='main-title'>Meow Wallet</div>", unsafe_allow_html=True)
    # ใช้อิโมจิแมวส้ม/เหลืองแทนแมวดำ
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱💰✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #DB7093;'>กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเปิดกระเป๋าเงินนะเมี๊ยวว!</h3>", unsafe_allow_html=True)
    play_audio("https://www.myinstants.com/media/sounds/kawaii-desu-ne.mp3")
    st.stop()

# --- 4. เมนู Tabs ---
tab1, tab2, tab3 = st.tabs(["📝 บันทึกรายวัน", "📊 สรุปยอด", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ สมุดบันทึกของ คุณ{user_name}")
    col1, col2 = st.columns([1, 2])
    with col1:
        # ใช้อิโมจิแมวน่ารักๆ กับกองเงิน (ไม่มีแมวดำ)
        st.markdown("<h1 style='text-align: center; font-size: 110px;'>😸<br>💵</h1>", unsafe_allow_html=True)
    with col2:
        date_in = st.date_input("📅 วันที่", datetime.now())
        type_in = st.radio("✨ เลือกประเภท", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
        cat_in = st.text_input("🏷️ หมวดหมู่", placeholder="เช่น ค่าขนม, ค่าเดินทาง")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)
        
    if st.button("💖 บันทึกรายการเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, income, expense) VALUES (?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, inc, exp))
            conn.commit()
            
            # เสียงตอนบันทึกสำเร็จ
            play_audio("https://www.myinstants.com/media/sounds/cat-meow.mp3")
            st.balloons()
            st.success(f"บันทึกเรียบร้อย! ขอบคุณนะเมี๊ยวว ✨")
            st.rerun()

with tab2:
    st.markdown("### 📊 สรุปยอดเงิน")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        t_in, t_out = df['income'].sum(), df['expense'].sum()
        c1.metric("💰 รายรับ", f"{t_in:,.2f}")
        c2.metric("💸 รายจ่าย", f"{t_out:,.2f}")
        c3.metric("🍦 คงเหลือ", f"{t_in-t_out:,.2f}")
        
        st.write("---")
        fig = px.pie(df[df['expense']>0], values='expense', names='category', 
                     hole=0.4, title="🍩 สัดส่วนรายจ่าย",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>🐾</h1>", unsafe_allow_html=True)
        st.info("ยังไม่มีข้อมูลในระบบจ้า")

with tab3:
    st.markdown("### 📖 ประวัติการออม")
    df_history = pd.read_sql(f"SELECT date as วันที่, category as หมวดหมู่, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC", conn)
    st.dataframe(df_history, use_container_width=True)

# ส่วนท้าย Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<h1 style='text-align: center;'>😺💖💰</h1>", unsafe_allow_html=True)
st.sidebar.write("<center>Meow Wallet</center>", unsafe_allow_html=True)
