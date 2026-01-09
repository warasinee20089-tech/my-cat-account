import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; }
    .meow-card { background: white; border-radius: 20px; padding: 20px; border: 2px solid #FFE4E1; text-align: center; margin-bottom: 10px; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; }
    .budget-red { color: #FF4B4B; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def get_db():
    conn = sqlite3.connect('meow_wallet_v41.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                  wallet TEXT, category TEXT, sub_category TEXT,
                  income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                  receipt_img BLOB)''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (user_id TEXT PRIMARY KEY, goal_name TEXT, goal_amount REAL)''')
    conn.commit()
    return conn

conn = get_db()

# --- 3. LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="พิมพ์ชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾"):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA PROCESSING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{months[date_obj.month]} {date_obj.year + 543}"

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    current_month = datetime.now().strftime('%Y-%m')
    df_current = df[df['month_year'] == current_month]
else:
    df_current = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0
balance = total_in - total_out - total_save

# --- 5. EMOTION & BUDGET LOGIC ---
budget_limit = 1000.0
current_expense = df_current['expense'].sum() if not df_current.empty else 0
budget_usage = (current_expense / budget_limit)

# Emotion Logic
if total_in > 0 and (total_save / total_in >= 0.3):
    meow_face, meow_msg = "😸", "เก่งมากทาส! ออมเงินได้เยอะแบบนี้ รางวัลคือพุงนุ่มๆ ของเค้าเอง!"
elif total_out > total_in:
    meow_face, meow_msg = "🙀", "ว้ายย! ทาสใช้เงินเกินตัวแล้วนะ ติดลบแบบนี้จะเอาอะไรซื้อขนมเปียก!!"
else:
    meow_face, meow_msg = "😺", "วันนี้ก็ใช้ชีวิตได้ดีนะทาส ตั้งใจเก็บเงินต่อไปล่ะเมี๊ยวว"

# --- 6. MAIN UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

# Sidebar/Top Status
col_face, col_budget = st.columns([1, 2])
with col_face:
    st.markdown(f"<div class='meow-card'><h1 style='font-size:60px; margin:0;'>{meow_face}</h1><p>{meow_msg}</p></div>", unsafe_allow_html=True)
with col_budget:
    st.markdown("<div class='meow-card'>", unsafe_allow_html=True)
    st.write(f"**งบประมาณรายเดือน (ต.ค.): {current_expense:,.2f} / {budget_limit:,.2f} ฿**")
    b_color = "red" if budget_usage >= 0.9 else "green"
    st.progress(min(budget_usage, 1.0))
    if budget_usage >= 0.9:
        st.markdown("<p class='budget-red'>🙀ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        uploaded_file = st.file_uploader("📸 ใบเสร็จ", type=['jpg', 'jpeg', 'png'])
    with col2:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ"):
        if amt > 0:
            img_byte = uploaded_file.getvalue() if uploaded_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            conn.cursor().execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                                  (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, selected_cat, sub_cat, inc, exp, sav, img_byte))
            conn.commit(); st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือในกระเป๋า")
    cw1, cw2, cw3 = st.columns(3)
    for i, w in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum()) if not w_df.empty else 0.0
        [cw1, cw2, cw3][i].metric(w, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์ภาพรวม")
    if not df.empty:
        st.markdown("#### 📈 รายรับ vs รายจ่าย (รายเดือน)")
        df['ไทยเดือน'] = df['date'].apply(get_thai_month)
        m_df = df.groupby('ไทยเดือน')[['income', 'expense']].sum().reset_index()
        st.plotly_chart(px.bar(m_df, x='ไทยเดือน', y=['income', 'expense'], barmode='group', color_discrete_map={'income':'#FFB7CE','expense':'#B2E2F2'}), use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🥧 สัดส่วนรายจ่าย")
            st.plotly_chart(px.pie(df[df['expense']>0], names='category', values='expense', hole=0.4), use_container_width=True)
        with c2:
            st.markdown("#### 💰 สัดส่วนรายรับ")
            st.plotly_chart(px.pie(df[df['income']>0], names='category', values='income', hole=0.4), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

with tab4:
    st.markdown("### 🎯 เป้าหมายการออม")
    g1, g2 = st.columns(2)
    with g1:
        g_name = st.text_input("ออมเพื่ออะไร?")
        g_amt = st.number_input("เป้าหมายยอดเงิน", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            conn.cursor().execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_amt))
            conn.commit(); st.rerun()
    with g2:
        goal = conn.cursor().execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal and goal[2] > 0:
            prog = min(total_save / goal[2], 1.0)
            st.markdown(f"<div class='meow-card'><h4>{goal[1]}</h4><h1>{prog*100:.1f}%</h1></div>", unsafe_allow_html=True)
            st.progress(prog)
            st.write(f"เก็บได้แล้ว {total_save:,.2f} / {goal[2]:,.2f} ฿")

with tab5:
    st.markdown("### 📖 ประวัติและแก้ไข")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sel_id = st.selectbox("เลือก ID รายการเพื่อจัดการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        
        ce1, ce2 = st.columns(2)
        with ce1:
            e_date = st.date_input("แก้ไขวัน", pd.to_datetime(row['date']))
            e_amt = st.number_input("แก้ไขเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
        with ce2:
            e_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
            if row['receipt_img']: st.image(row['receipt_img'], width=150)
        
        if st.button("✅ ยืนยันแก้ไขรายการ"):
            n_inc, n_exp, n_sav = (e_amt,0,0) if row['income']>0 else (0,e_amt,0) if row['expense']>0 else (0,0,e_amt)
            conn.cursor().execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                                  (e_date.strftime('%Y-%m-%d'), n_inc, n_exp, n_sav, e_sub, sel_id))
            conn.commit(); st.success("แก้ไขแล้ว!"); st.rerun()
        if st.button("🗑️ ลบรายการนี้"):
            conn.cursor().execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
