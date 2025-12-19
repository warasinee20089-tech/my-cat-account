import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ Meow Wallet Ultimate (Add Savings Mode) ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; padding: 10px; }
    div[data-testid="stMetric"] { background: white; border-radius: 15px; border: 1px solid #FFD1DC; padding: 15px; }
    .stProgress > div > div > div > div { background-color: #FF69B4; }
    .report-card { background-color: white; padding: 20px; border-radius: 15px; border-top: 5px solid #FF69B4; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_ultimate_v8.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. Sidebar & Login ---
st.sidebar.markdown("<h2 style='text-align: center;'>🐱 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", placeholder="กรอกชื่อเพื่อเริ่มจ้า...")

if not user_name:
    st.markdown("<div class='main-title'>🐾 Meow Wallet Ultimate</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>💰✨</h1>", unsafe_allow_html=True)
    st.stop()

# --- 4. ดึงข้อมูลพื้นฐาน ---
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0
net_balance = total_in - total_out - total_save

# --- 5. เมนู Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึกรายวัน", "🏦 กระเป๋าเงิน", "📊 วิเคราะห์นิสัย", "🎯 แผนการออม", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกรายการ (คุณ {user_name})")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        # เพิ่มประเภท "เงินออม" ให้เลือกได้โดยตรง
        type_in = st.radio("🏷️ ประเภทรายการ", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
    with col2:
        main_cats = ["ค่าอาหาร 🍱", "ค่าเครื่องดื่ม ☕", "ค่าของใช้ส่วนตัว 🧼", "ค่าสาธารณูปโภค ⚡", "ค่าเดินทาง 🚗", "ค่าท่องเที่ยว ✈️", "ค่าสันทนาการ 🎮", "ช้อปปิ้ง 🛍️", "ที่อยู่อาศัย 🏠", "เงินออมเป้าหมาย 🎯"]
        cat_in = st.selectbox("📁 หมวดหมู่", main_cats)
        sub_cat_in = st.text_input("📝 รายละเอียดเพิ่มเติม", placeholder="ระบุรายละเอียดที่นี่...")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!"):
        if amt_in > 0:
            inc, exp, sav = 0, 0, 0
            if type_in == "รายรับ 💰": inc = amt_in
            elif type_in == "รายจ่าย 💸": exp = amt_in
            else: sav = amt_in # ถ้าเลือกเงินออม
            
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, cat_in, sub_cat_in, inc, exp, sav))
            conn.commit()
            st.balloons()
            st.rerun()

with tab4:
    st.markdown("### 🎯 สรุปแผนการออมเงิน")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("💰 เงินออมสะสมทั้งหมด", f"{total_save:,.2f} ฿")
    col_s2.metric("🍦 เงินเหลือใช้สุทธิ", f"{net_balance:,.2f} ฿")

    st.markdown("---")
    st.markdown("#### 📏 การจัดสรรตามกฎ 50/30/20")
    if total_in > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("จำเป็น (50%)", f"{total_in*0.5:,.2f}")
        c2.metric("ส่วนตัว (30%)", f"{total_in*0.3:,.2f}")
        c3.metric("เงินออม (20%)", f"{total_in*0.2:,.2f}")

with tab3:
    st.markdown("### 📊 Reports & Analytics")
    if not df.empty:
        st.markdown("<div class='report-card'><h4>🥧 สัดส่วนรายจ่าย vs เงินออม</h4>", unsafe_allow_html=True)
        # สร้าง Pie Chart ที่รวมทั้งรายจ่ายและเงินออม
        labels = ['รายจ่าย', 'เงินออม']
        values = [total_out, total_save]
        fig = px.pie(names=labels, values=values, hole=0.5, color_discrete_sequence=['#EF553B', '#FF69B4'])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 🏦 ยอดเงินในแต่ละช่องทาง")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp, SUM(savings) as sav FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    cols = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        row = df_w[df_w['wallet'] == w_name]
        # ยอดคงเหลือในกระเป๋า = รายรับ - (รายจ่าย + เงินออมที่ดึงออกไปเก็บ)
        bal = row['inc'].sum() - row['exp'].sum() - row['sav'].sum() if not row.empty else 0.0
        cols[i].metric(w_name, f"{bal:,.2f} ฿")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_display = df.sort_values(by=['date', 'id'], ascending=[False, False])
        st.dataframe(df_display[['date', 'wallet', 'category', 'sub_category', 'income', 'expense', 'savings']], use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("🐱 *Meow Wallet v8.0 (Savings Mode)*")
