import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ Meow Wallet Ultimate PRO ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; padding: 10px; }
    div[data-testid="stMetric"] { background: white; border-radius: 15px; border: 1px solid #FFD1DC; padding: 15px; }
    .stProgress > div > div > div > div { background-color: #FF69B4; }
    .report-card { background-color: white; padding: 20px; border-radius: 15px; border-top: 5px solid #FF69B4; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_ultimate_pro_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, is_tax_deductible INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS goals 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, goal_name TEXT, target_amount REAL)''')
conn.commit()

# --- 3. Sidebar & Login ---
st.sidebar.markdown("<h2 style='text-align: center;'>🐱 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", placeholder="กรอกชื่อตรงนี้จ้า...")

if not user_name:
    st.markdown("<div class='main-title'>🐾 Meow Wallet Ultimate</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>💰✨</h1>", unsafe_allow_html=True)
    st.info("กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเปิดระบบวิเคราะห์การเงินเมี๊ยวว!")
    st.stop()

# --- 4. ดึงข้อมูลพื้นฐาน ---
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
net_balance = total_in - total_out

# --- 5. เมนู Tabs (เพิ่ม Tab วิเคราะห์และรายงาน) ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์ & รายงาน", "🎯 การออม", "🤖 ลงทุน", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกรายการ (คุณ {user_name})")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
        tax_in = st.checkbox("🧾 รายการนี้ลดหย่อนภาษีได้ (เช่น ช้อปดีมีคืน, ประกัน)")
    with col2:
        main_cats = ["ค่าอาหาร 🍱", "ค่าเครื่องดื่ม ☕", "ค่าของใช้ส่วนตัว 🧼", "ค่าสาธารณูปโภค ⚡", "ค่าเดินทาง 🚗", "ค่าท่องเที่ยว ✈️", "ค่าสันทนาการ 🎮", "ช้อปปิ้ง 🛍️", "ที่อยู่อาศัย 🏠"]
        cat_in = st.selectbox("📁 หมวดหมู่หลัก", main_cats)
        sub_cat_in = st.text_input("📝 รายละเอียด", placeholder="พิมพ์รายละเอียดเองได้ที่นี่...")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!"):
        if amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, is_tax_deductible) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, cat_in, sub_cat_in, inc, exp, 1 if tax_in else 0))
            conn.commit()
            st.balloons()
            st.rerun()

with tab3:
    st.markdown("### 📊 Reports & Analytics (วิเคราะห์นิสัยการเงิน)")
    if not df.empty:
        # 1. แยกตามหมวดหมู่ (Pie Chart)
        st.markdown("<div class='report-card'><h4>🥧 เงินส่วนใหญ่หมดไปกับอะไร?</h4>", unsafe_allow_html=True)
        df_exp = df[df['expense'] > 0]
        if not df_exp.empty:
            fig_pie = px.pie(df_exp, values='expense', names='category', hole=0.5,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.write("ยังไม่มีข้อมูลรายจ่าย")
        st.markdown("</div>", unsafe_allow_html=True)

        # 2. แนวโน้มรายเดือน (Line Chart)
        st.markdown("<div class='report-card'><h4>📈 แนวโน้มรายรับ-รายจ่าย</h4>", unsafe_allow_html=True)
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
        df_monthly = df.groupby('month')[['income', 'expense']].sum().reset_index()
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df_monthly['month'], y=df_monthly['income'], name='รายรับ', line=dict(color='#00CC96', width=4)))
        fig_line.add_trace(go.Scatter(x=df_monthly['month'], y=df_monthly['expense'], name='รายจ่าย', line=dict(color='#EF553B', width=4)))
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 3. สรุปภาษี
        st.markdown("<div class='report-card'><h4>🧾 สรุปยอดลดหย่อนภาษี</h4>", unsafe_allow_html=True)
        tax_deduct = df[df['is_tax_deductible'] == 1]['expense'].sum()
        st.write(f"ยอดรวมรายการที่นำไปลดหย่อนภาษีได้: **{tax_deduct:,.2f} บาท**")
        if tax_deduct > 0:
            st.info("💡 อย่าลืมเก็บใบเสร็จหรือ e-Receipt ของรายการเหล่านี้ไว้เพื่อยื่นภาษีนะเมี๊ยวว!")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("บันทึกข้อมูลก่อนเพื่อดูการวิเคราะห์นะเมี๊ยวว")

# --- Tab อื่นๆ (คงเดิม) ---
with tab2:
    st.markdown("### 🏦 ยอดเงินในกระเป๋า")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    cols = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        row = df_w[df_w['wallet'] == w_name]
        bal = row['inc'].sum() - row['exp'].sum() if not row.empty else 0.0
        cols[i].metric(w_name, f"{bal:,.2f} ฿")

with tab4:
    st.markdown("### 🎯 ระบบเป้าหมายการออม")
    # ส่วนเป้าหมายและการคำนวณเงินสำรองฉุกเฉิน (คงเดิมจากเวอร์ชันที่แล้ว)
    avg_exp = total_out / (len(df['date'].unique())) if not df.empty and len(df['date'].unique()) > 0 else 0
    em_target = avg_exp * 6
    st.metric("🚑 เป้าหมายเงินสำรองฉุกเฉิน (6 เท่า)", f"{em_target:,.2f} ฿")
    em_p = min(net_balance/em_target, 1.0) if em_target > 0 else 0
    st.progress(em_p)
    st.write(f"ออมได้แล้ว {em_p*100:.1f}%")

with tab5:
    st.markdown("### 🤖 ลงทุน & Meow Advisor")
    st.write(f"สุขภาพการเงิน: คุณออมเงินได้ **{(net_balance/total_in*100 if total_in > 0 else 0):.1f}%**")
    if net_balance > total_in * 0.2:
        st.success("🌟 ออมเก่งมาก! แบ่งเงินไปลงทุนในกองทุนดัชนี (Index Fund) ได้เลย")

with tab6:
    st.markdown("### 📖 ประวัติและยอดคงเหลือสะสม")
    if not df.empty:
        df_history = df.sort_values(by=['date', 'id'], ascending=[False, False])
        df_rev = df_history.iloc[::-1].copy()
        df_rev['ยอดคงเหลือ'] = df_rev['income'].cumsum() - df_rev['expense'].cumsum()
        st.dataframe(df_rev.iloc[::-1][['date', 'wallet', 'category', 'sub_category', 'income', 'expense', 'ยอดคงเหลือ']], use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("🐱 *Meow Wallet Ultimate v5.0*")
