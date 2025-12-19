import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ Meow Wallet Ultimate v11.0 ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Kanit', sans-serif; 
        color: #000000 !important;
    }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; padding: 10px; }
    div[data-testid="stMetric"] { background: white; border-radius: 15px; border: 1px solid #FFD1DC; padding: 15px; }
    .stProgress > div > div > div > div { background-color: #FF69B4; }
    .report-card { background-color: white; padding: 20px; border-radius: 15px; border-top: 5px solid #FF69B4; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_ultimate_v11.db', check_same_thread=False)
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
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>💰✨</h1>")
    st.stop()

# --- 4. ดึงข้อมูล ---
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
        type_in = st.radio("🏷️ ประเภทรายการ", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
    
    with col2:
        # กำหนดหมวดหมู่ตามประเภทที่เลือก
        if type_in == "รายรับ 💰":
            cat_list = ["เงินเดือน 💸", "โบนัส 🎁", "ขายของออนไลน์ 🛍️", "ค่าจ้างพิเศษ 🛠️", "เงินขวัญถุง 🧧", "อื่นๆ ➕"]
        elif type_in == "รายจ่าย 💸":
            cat_list = ["ค่าอาหาร 🍱", "ค่าเครื่องดื่ม ☕", "ค่าเดินทาง 🚗", "ช้อปปิ้ง 🛍️", "ค่าที่พัก 🏠", "ค่าสาธารณูปโภค ⚡", "อื่นๆ ➕"]
        else: # เงินออม
            cat_list = ["เงินออมระยะยาว 🏦", "เงินออมฉุกเฉิน 🚑", "ออมเพื่อของอยากได้ 🎁", "อื่นๆ ➕"]
            
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_list)
        
        # ถ้าเลือก "อื่นๆ ➕" ให้ขึ้นช่องพิมพ์เอง
        final_category = selected_cat
        if selected_cat == "อื่นๆ ➕":
            final_category = st.text_input("✍️ ระบุหมวดหมู่ใหม่", placeholder="พิมพ์ชื่อหมวดหมู่ที่นี่...")
            
        sub_cat_in = st.text_input("📝 รายละเอียดเพิ่มเติม (เช่น ชื่อร้าน/รายการ)", placeholder="ระบุรายละเอียดที่นี่...")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!"):
        if amt_in > 0 and final_category != "":
            inc, exp, sav = 0, 0, 0
            if type_in == "รายรับ 💰": inc = amt_in
            elif type_in == "รายจ่าย 💸": exp = amt_in
            else: sav = amt_in
            
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_category, sub_cat_in, inc, exp, sav))
            conn.commit()
            st.balloons()
            st.rerun()

# --- ส่วนอื่นๆ ของแอป (กระเป๋าเงิน, วิเคราะห์, การออม, ประวัติ) ยังคงเดิมเพื่อให้ระบบทำงานได้เสมือนเวอร์ชัน 9.0 ---
with tab2:
    st.markdown("### 🏦 ยอดเงินคงเหลือ")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp, SUM(savings) as sav FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    cols = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        row = df_w[df_w['wallet'] == w_name]
        bal = row['inc'].sum() - row['exp'].sum() - row['sav'].sum() if not row.empty else 0.0
        cols[i].metric(w_name, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 Reports & Analytics")
    if not df.empty:
        st.markdown("<div class='report-card'><h4>🥧 สัดส่วนรายจ่าย vs เงินออม</h4>", unsafe_allow_html=True)
        labels = ['รายจ่าย', 'เงินออม']
        values = [total_out, total_save]
        fig = px.pie(names=labels, values=values, hole=0.5, color_discrete_sequence=['#EF553B', '#FF69B4'])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>")

with tab4:
    st.markdown("### 🎯 แผนการออม")
    st.metric("💰 เงินออมสะสมทั้งหมด", f"{total_save:,.2f} ฿")
    if total_in > 0:
        st.write(f"ออมไปแล้ว {(total_save/total_in)*100:.1f}% ของรายได้ทั้งหมด")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_display = df.sort_values(by=['date', 'id'], ascending=[False, False])
        st.dataframe(df_display[['date', 'wallet', 'category', 'sub_category', 'income', 'expense', 'savings']], use_container_width=True)
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 ดาวน์โหลดประวัติเป็น CSV", data=csv, file_name=f'meow_backup_{user_name}.csv', mime='text/csv')

st.sidebar.markdown("---")
st.sidebar.write("🐱 *Meow Wallet v11.0 (Smart Category)*")
