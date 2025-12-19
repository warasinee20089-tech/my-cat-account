import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ Meow Wallet Ultimate ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; }
    div[data-testid="stMetric"] { background: white; border-radius: 15px; border: 1px solid #FFD1DC; padding: 15px; }
    .stProgress > div > div > div > div { background-color: #FF69B4; }
    .save-card { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border-left: 5px solid #FF69B4; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล (เพิ่มตารางเป้าหมายการออม) ---
conn = sqlite3.connect('meow_ultimate_v1.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS goals 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, goal_name TEXT, target_amount REAL, current_saved REAL DEFAULT 0)''')
conn.commit()

# --- 3. Sidebar & User ---
st.sidebar.markdown("<h2 style='text-align: center;'>🐱 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", placeholder="กรอกชื่อเพื่อเริ่มจ้า...")

if not user_name:
    st.markdown("<div class='main-title'>🐾 Meow Wallet Ultimate</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>💰✨</h1>", unsafe_allow_html=True)
    st.info("กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเปิดระบบบริหารเงินออมอัจฉริยะเมี๊ยวว!")
    st.stop()

# --- 4. ฟังก์ชันคำนวณข้อมูลการเงิน ---
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
net_balance = total_in - total_out

# --- 5. เมนู Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋าเงิน", "🎯 การออมเงิน", "📊 วิเคราะห์ & ลงทุน", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกรายวัน (คุณ {user_name})")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
    with col2:
        main_cats = ["ค่าอาหาร 🍱", "ค่าเครื่องดื่ม ☕", "ค่าของใช้ส่วนตัว 🧼", "ค่าสาธารณูปโภค ⚡", "ค่าเดินทาง 🚗", "ค่าท่องเที่ยว ✈️", "ค่าสันทนาการ 🎮", "ช้อปปิ้ง 🛍️", "ที่อยู่อาศัย 🏠"]
        cat_in = st.selectbox("📁 หมวดหมู่หลัก", main_cats)
        sub_cat_in = st.text_input("📝 รายละเอียด", placeholder="พิมพ์รายละเอียดเองได้ที่นี่...")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!"):
        if amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense) VALUES (?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, cat_in, sub_cat_in, inc, exp))
            conn.commit()
            st.balloons()
            st.success("บันทึกเรียบร้อย! ข้อมูลถูกนำไปวิเคราะห์การออมแล้วจ้า")
            st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดเงินในกระเป๋า")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    cols = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        row = df_w[df_w['wallet'] == w_name]
        bal = row['inc'].sum() - row['exp'].sum() if not row.empty else 0.0
        cols[i].metric(w_name, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 🎯 ระบบบริหารจัดการเงินออม")
    
    # 1. กฎการจัดสรรเงิน 50/30/20
    st.markdown("#### 📏 การจัดสรรตามกฎ 50/30/20 (จากรายรับทั้งหมด)")
    if total_in > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("จำเป็น (50%)", f"{total_in*0.5:,.2f} ฿")
        c2.metric("ส่วนตัว (30%)", f"{total_in*0.3:,.2f} ฿")
        c3.metric("เงินออม (20%)", f"{total_in*0.2:,.2f} ฿")
        if total_out > (total_in * 0.8):
            st.warning("⚠️ คำเตือน: ตอนนี้คุณใช้จ่ายเกิน 80% ของรายได้แล้ว รีบออมด่วนเมี๊ยวว!")

    # 2. Saving Goals
    st.markdown("---")
    st.markdown("#### 🚩 เป้าหมายการออมเงิน")
    with st.expander("➕ เพิ่มเป้าหมายใหม่"):
        g_name = st.text_input("ชื่อเป้าหมาย", placeholder="เช่น ซื้อแล็ปท็อป, เที่ยวญี่ปุ่น")
        g_target = st.number_input("จำนวนเงินที่ต้องการ", min_value=0.0)
        if st.button("ตั้งเป้าหมาย!"):
            c.execute("INSERT INTO goals (user_id, goal_name, target_amount) VALUES (?,?,?)", (user_name, g_name, g_target))
            conn.commit()
            st.rerun()

    df_g = pd.read_sql(f"SELECT * FROM goals WHERE user_id='{user_name}'", conn)
    for index, row in df_g.iterrows():
        st.markdown(f"<div class='save-card'><b>{row['goal_name']}</b></div>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns([3, 1])
        # จำลองการคำนวณ: ใช้ net_balance กระจายเข้าเป้าหมาย (ในแอปจริงสามารถระบุจำนวนเงินที่จะโอนเข้าเป้าหมายได้)
        # ตัวอย่างนี้แสดง Progress เทียบกับยอดคงเหลือปัจจุบัน
        current_val = min(net_balance, row['target_amount']) if net_balance > 0 else 0
        progress = (current_val / row['target_amount']) if row['target_amount'] > 0 else 0
        col_g1.progress(progress)
        col_g2.write(f"{progress*100:.1f}% ({current_val:,.0f}/{row['target_amount']:,.0f})")

    # 3. Emergency Fund
    st.markdown("---")
    st.markdown("#### 🚑 เงินสำรองฉุกเฉิน (เป้าหมาย 6 เท่าของรายจ่ายเฉลี่ย)")
    avg_expense = total_out / (len(df['date'].unique())) if not df.empty and len(df['date'].unique()) > 0 else 0
    emergency_target = avg_expense * 6
    st.write(f"เป้าหมายเงินสำรองที่ควรมี: **{emergency_target:,.2f} ฿**")
    em_progress = min(net_balance / emergency_target, 1.0) if emergency_target > 0 else 0
    st.progress(em_progress)
    st.write(f"ปัจจุบันคุณมีเงินสำรองแล้ว {em_progress*100:.1f}% ของเป้าหมาย")

with tab4:
    st.markdown("### 📊 วิเคราะห์ & แนะนำการลงทุน")
    if not df.empty:
        # กราฟวงกลมสัดส่วนรายจ่าย
        fig_pie = px.pie(df[df['expense']>0], values='expense', names='category', hole=0.4, title="สัดส่วนการใช้จ่าย", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # ระบบแนะนำการลงทุน (เหมือนเวอร์ชันก่อนหน้า)
        st.markdown("#### 🤖 Meow Advisor")
        risk = st.select_slider("ระดับความเสี่ยง", options=["ต่ำ", "กลาง", "สูง"])
        if net_balance > total_in * 0.2:
            st.success("🌟 คุณมียอดออมที่ดี! แนะนำให้ลงทุนในกองทุนดัชนีหรือหุ้นพื้นฐานดีเมี๊ยวว")
        else:
            st.info("แนะนำให้ออมในบัญชีดอกเบี้ยสูงไปก่อนจนกว่าจะครบเงินสำรองฉุกเฉินครับ")

with tab5:
    st.markdown("### 📖 ประวัติและยอดคงเหลือสะสม")
    df_h = pd.read_sql(f"SELECT date as วันที่, wallet as กระเป๋า, category as หมวดหมู่, sub_category as รายละเอียด, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC, id DESC", conn)
    if not df_h.empty:
        df_rev = df_h.iloc[::-1].copy()
        df_rev['ยอดคงเหลือสะสม'] = df_rev['รายรับ'].cumsum() - df_rev['รายจ่าย'].cumsum()
        st.dataframe(df_rev.iloc[::-1], use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("🐱 *Meow Wallet Ultimate v3.0*")
