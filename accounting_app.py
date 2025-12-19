import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
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
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฐานข้อมูล ---
conn = sqlite3.connect('meow_wallet_v16.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. ระบบ Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center;'>🐱</h1>", unsafe_allow_html=True)
        name_input = st.text_input("ชื่อทาสแมว:", key="login_name")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. ดึงข้อมูล ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

# --- 5. Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกรายการ (คุณ {user_name})")
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
        if amt_in > 0 and final_category:
            inc, exp, sav = (amt_in, 0, 0) if type_in == "รายรับ 💰" else (0, amt_in, 0) if type_in == "รายจ่าย 💸" else (0, 0, amt_in)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_category, sub_cat_in, inc, exp, sav))
            conn.commit()
            st.success("บันทึกเรียบร้อยเมี๊ยวว!")
            st.rerun()

with tab3:
    st.markdown("### 📊 วิเคราะห์ภาพรวม")
    if not df.empty:
        # กราฟ 1: เปรียบเทียบ รายรับ/รายจ่าย/เงินออม
        st.write("💰 สรุปยอดรวม (บาท)")
        summary_df = pd.DataFrame({
            'ประเภท': ['รายรับ', 'รายจ่าย', 'เงินออม'],
            'จำนวนเงิน': [df['income'].sum(), df['expense'].sum(), df['savings'].sum()]
        })
        fig_bar = px.bar(summary_df, x='ประเภท', y='จำนวนเงิน', color='ประเภท',
                         color_discrete_map={'รายรับ':'#4CAF50', 'รายจ่าย':'#FF5252', 'เงินออม':'#FF69B4'})
        st.plotly_chart(fig_bar, use_container_width=True)

        # กราฟ 2: แยกตามหมวดหมู่
        st.write("📁 รายจ่ายแยกตามหมวดหมู่")
        exp_df = df[df['expense'] > 0]
        if not exp_df.empty:
            fig_pie = px.pie(exp_df, values='expense', names='category', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลรายจ่ายเพื่อแสดงกราฟแยกหมวดหมู่")
    else:
        st.info("บันทึกข้อมูลก่อนเพื่อดูการวิเคราะห์นะเมี๊ยวว!")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        st.dataframe(df.sort_values(by=['date', 'id'], ascending=[False, False]), use_container_width=True)
    else:
        st.write("ยังไม่มีข้อมูล")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.rerun()
