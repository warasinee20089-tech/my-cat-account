import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. หน้าตั้งค่าและสไตล์ ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF5F7 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #2D2D2D !important;
    }
    .main-title { color: #FF69B4; text-align: center; font-size: 40px; font-weight: bold; padding: 15px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล (ใช้ชื่อใหม่กันสับสนและล็อคระบบ) ---
def init_db():
    conn = sqlite3.connect('meow_permanent_v1.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                  wallet TEXT, category TEXT, sub_category TEXT,
                  income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. ระบบ Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>🐱</h1>", unsafe_allow_html=True)
        name_input = st.text_input("ชื่อทาสแมวของคุณ:", placeholder="กรอกชื่อเพื่อล็อคอิน...", key="login_name")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. ดึงข้อมูล ---
user_name = st.session_state.user_name
# ดึงข้อมูลมาใส่ DataFrame และเตรียมตัวแปรให้พร้อมเสมอเพื่อป้องกัน Error
try:
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
except:
    df = pd.DataFrame(columns=['id', 'user_id', 'date', 'wallet', 'category', 'sub_category', 'income', 'expense', 'savings'])

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

st.markdown(f"<div class='main-title'>🐾 Meow Wallet ของ {user_name}</div>", unsafe_allow_html=True)

# --- 5. เมนู Tabs ---
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
            
        sub_cat_in = st.text_input("📝 รายละเอียด")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!", use_container_width=True):
        if amt_in > 0 and final_category:
            inc, exp, sav = (amt_in, 0, 0) if type_in == "รายรับ 💰" else (0, amt_in, 0) if type_in == "รายจ่าย 💸" else (0, 0, amt_in)
            c = conn.cursor()
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_category, sub_cat_in, inc, exp, sav))
            conn.commit()
            st.success("บันทึกเรียบร้อยเมี๊ยวว!")
            st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือรายกระเป๋า")
    c1, c2, c3 = st.columns(3)
    for i, w_name in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w_name]
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        [c1, c2, c3][i].metric(w_name, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์ภาพรวม")
    if not df.empty and total_in + total_out + total_save > 0:
        fig = px.bar(x=['รายรับ', 'รายจ่าย', 'เงินออม'], y=[total_in, total_out, total_save], 
                     labels={'x':'ประเภท', 'y':'จำนวนเงิน'}, color=['รายรับ', 'รายจ่าย', 'เงินออม'],
                     color_discrete_map={'รายรับ':'#4CAF50', 'รายจ่าย':'#FF5252', 'เงินออม':'#FF69B4'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลสำหรับวิเคราะห์เมี๊ยวว")

with tab4:
    st.markdown("### 🎯 การออมเงิน")
    st.metric("💰 ยอดเงินออมรวม", f"{total_save:,.2f} ฿")
    if total_in > 0:
        prog = min(total_save / total_in, 1.0)
        st.progress(prog)
        st.write(f"ออมไปแล้ว {prog*100:.1f}% ของรายได้")
    else:
        st.write("บันทึกรายรับเพื่อดูสถานะการออมนะเมี๊ยวว")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลด CSV", data=csv, file_name=f'meow_{user_name}.csv', use_container_width=True)
    else:
        st.write("ไม่มีข้อมูลประวัติเมี๊ยวว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
