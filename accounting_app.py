import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES (สีชมพูพาสเทลอ่อน) ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; } /* ชมพูพาสเทลอ่อนมาก */
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 15px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFE4E1 !important; padding: 15px; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; }
    .stButton>button:hover { background-color: #FFC0CB; color: white; border: none; }
    .badge-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFE4E1; margin-bottom: 20px; height: 180px;
    }
    .badge-icon { font-size: 50px; margin-bottom: 10px; }
    .badge-title { font-weight: bold; color: #FFB7CE; font-size: 18px; }
    .badge-desc { font-size: 14px; color: #777; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def get_db():
    conn = sqlite3.connect('meow_wallet_v39.db', check_same_thread=False)
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

# --- 3. LOGIN PAGE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>เข้าสู่ระบบทาสแมวพาสเทล</h3>", unsafe_allow_html=True)
        name_in = st.text_input("กรอกชื่อของคุณ:", placeholder="ชื่อทาสแมว...")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. APP UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติ"])

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
    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0:
            img_byte = uploaded_file.getvalue() if uploaded_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c = conn.cursor()
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
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
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        ca1, ca2, ca3 = st.columns(3)
        exp_df = df[df['expense'] > 0]
        inc_df = df[df['income'] > 0]
        # เหรียญตรา
        t_cat = exp_df.groupby('category')['expense'].sum().idxmax() if not exp_df.empty else "ไม่มี"
        ca1.markdown(f"<div class='badge-card'><div class='badge-icon'>🍱</div><div class='badge-title'>ทาสสายเปย์</div><p class='badge-desc'>เน้นหนักที่หมวด {t_cat}</p></div>", unsafe_allow_html=True)
        ca2.markdown(f"<div class='badge-card'><div class='badge-icon'>💰</div><div class='badge-title'>รับทรัพย์เมี๊ยว</div><p class='badge-desc'>รายรับรวม {total_in:,.0f} ฿</p></div>", unsafe_allow_html=True)
        s_title = "ราชา/ราชินีนักออม 👑" if (total_in > 0 and (total_save/total_in >= 0.5)) else "ต้นกล้าเมี๊ยว 🌱"
        ca3.markdown(f"<div class='badge-card'><div class='badge-icon'>🛡️</div><div class='badge-title'>{s_title}</div><p class='badge-desc'>ออมไปแล้ว {total_save:,.0f} ฿</p></div>", unsafe_allow_html=True)

        st.markdown("#### 🥧 สัดส่วนภาพรวม")
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FFB7CE', '#B2E2F2']), use_container_width=True)
        
        st.markdown("#### 🍱 รายจ่ายแยกตามหมวดหมู่")
        if not exp_df.empty: st.plotly_chart(px.pie(exp_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        
        st.markdown("#### 💰 รายรับแยกตามหมวดหมู่")
        if not inc_df.empty: st.plotly_chart(px.pie(inc_df.groupby('category')['income'].sum().reset_index(), names='category', values='income', color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูล")

with tab4:
    st.markdown("### 🎯 เป้าหมายการออม")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        g_name = st.text_input("ออมเพื่อ?")
        g_amt = st.number_input("เป้าหมาย (฿)", min_value=0.0)
        if st.button("🚩 บันทึก"):
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_amt))
            conn.commit(); st.rerun()
    with g_col2:
        goal = conn.cursor().execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal and goal[2] > 0:
            prog = min(total_save / goal[2], 1.0)
            st.markdown(f"#### เป้าหมาย: **{goal[1]}**")
            st.metric("ความสำเร็จ", f"{prog*100:.1f} %")
            st.progress(prog)
            st.write(f"เก็บได้ {total_save:,.2f} จาก {goal[2]:,.2f} ฿")

with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sel_id = st.selectbox("เลือก ID รายการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        if row['receipt_img']: st.image(row['receipt_img'], width=300)
        if st.button("🗑️ ลบรายการนี้"):
            conn.cursor().execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()
    else: st.info("ยังไม่มีข้อมูล")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
