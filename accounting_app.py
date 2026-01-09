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
    .stApp { background-color: #FFF5F7 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #2D2D2D !important;
    }
    .main-title { color: #FF69B4; text-align: center; font-size: 40px; font-weight: bold; padding: 15px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 15px; }
    .stButton>button { border-radius: 10px; background-color: #FF69B4; color: white; border: none; }
    .badge-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFD1DC; margin-bottom: 20px; height: 180px;
    }
    .badge-icon { font-size: 50px; margin-bottom: 10px; }
    .badge-title { font-weight: bold; color: #FF69B4; font-size: 18px; }
    .badge-desc { font-size: 14px; color: #666; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE (WITH AUTO-MIGRATION) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_ultimate_v38.db', check_same_thread=False)
    c = conn.cursor()
    # สร้างตารางหลักถ้ายังไม่มี
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                  wallet TEXT, category TEXT, sub_category TEXT,
                  income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                  receipt_img BLOB)''')
    # สร้างตารางเป้าหมาย
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (user_id TEXT PRIMARY KEY, goal_name TEXT, goal_amount REAL)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. LOGIN PAGE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>ยินดีต้อนรับทาสแมวเมี๊ยวว</h3>", unsafe_allow_html=True)
        name_in = st.text_input("กรอกชื่อของคุณ:", placeholder="พิมพ์ชื่อตรงนี้เมี๊ยว...")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
              "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{months[date_obj.month]} {date_obj.year + 543}"

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['เดือน'] = df['date'].apply(get_thai_month)

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. MAIN UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        uploaded_file = st.file_uploader("📸 อัปโหลดใบเสร็จ (ถ้ามี)", type=['jpg', 'jpeg', 'png'])
    with col2:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        final_cat = st.text_input("✍️ ระบุเอง") if selected_cat == "อื่นๆ ➕" else selected_cat
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0:
            img_byte = uploaded_file.getvalue() if uploaded_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c = conn.cursor()
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_cat, sub_cat, inc, exp, sav, img_byte))
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
        # Badge Logic
        if not exp_df.empty:
            t_cat = exp_df.groupby('category')['expense'].sum().idxmax()
            t_amt = exp_df.groupby('category')['expense'].sum().max()
            e_icon, e_title, e_desc = ("🍛", "นักชิมอันดับหนึ่ง", f"เปย์หนักไปกับของอร่อย\n{t_amt:,.0f} ฿") if "อาหาร" in t_cat else ("🛍️", "นักช้อปมือไว", f"หมดไปกับของต้องมี!\n{t_amt:,.0f} ฿") if "ช้อปปิ้ง" in t_cat else ("📦", "นักจัดการทั่วไป", f"เน้นจ่ายหมวด {t_cat}\n{t_amt:,.0f} ฿")
        else: e_icon, e_title, e_desc = "💤", "ทาสสายจำศีล", "ยังไม่มีรายจ่าย"
        
        inc_df = df[df['income'] > 0]
        i_cat = inc_df.groupby('category')['income'].sum().idxmax() if not inc_df.empty else None
        i_icon, i_title, i_desc = ("💵", "มนุษย์เงินเดือน", "รับจากงานประจำ") if i_cat and "เงินเดือน" in i_cat else ("💎", "ขุมทรัพย์มหาศาล", f"รับจาก {i_cat}") if i_cat else ("🐱", "ทาสรอความหวัง", "รอเงินเข้าเมี๊ยว")

        s_pct = (total_save / total_in * 100) if total_in > 0 else 0
        s_icon, s_title, s_desc = ("👑", "ราชา/ราชินีนักออม", "ออมโหดเหมือนโกรธใครมา!") if s_pct >= 50 else ("🙀", "ไหแตกแล้วเมี๊ยว", "ยังไม่ได้ออมเลย!") if total_save == 0 else ("🛡️", "ป้อมปราการ", f"วินัยดี {s_pct:.1f}%")

        ca1.markdown(f"<div class='badge-card'><div class='badge-icon'>{e_icon}</div><div class='badge-title'>{e_title}</div><p class='badge-desc'>{e_desc}</p></div>", unsafe_allow_html=True)
        ca2.markdown(f"<div class='badge-card'><div class='badge-icon'>{i_icon}</div><div class='badge-title'>{i_title}</div><p class='badge-desc'>{i_desc}</p></div>", unsafe_allow_html=True)
        ca3.markdown(f"<div class='badge-card'><div class='badge-icon'>{s_icon}</div><div class='badge-title'>{s_title}</div><p class='badge-desc'>{s_desc}</p></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 🥧 สัดส่วนรายจ่าย vs เงินออม")
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FF9AA2', '#B2E2F2']), use_container_width=True)
        
        st.markdown("#### 🍱 รายจ่ายตามหมวดหมู่")
        if not exp_df.empty: st.plotly_chart(px.pie(exp_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        
        st.markdown("#### 💰 รายรับตามหมวดหมู่")
        if not inc_df.empty: st.plotly_chart(px.pie(inc_df.groupby('category')['income'].sum().reset_index(), names='category', values='income', color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

with tab4:
    st.markdown("### 🎯 ตั้งเป้าหมายการออม")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        g_name = st.text_input("ออมเงินเพื่ออะไรเมี๊ยว?")
        g_amt = st.number_input("เป้าหมายยอดเงิน (฿)", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_amt))
            conn.commit(); st.rerun()
    with g_col2:
        c = conn.cursor()
        goal = c.execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal:
            prog = min(total_save / goal[2], 1.0) if goal[2] > 0 else 0
            st.markdown(f"#### เป้าหมาย: **{goal[1]}**")
            st.metric("เงินออมที่มี", f"{total_save:,.2f} / {goal[2]:,.2f}")
            st.progress(prog)

with tab5:
    st.markdown("### 📖 ประวัติและแก้ไข")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sel_id = st.selectbox("เลือก ID รายการเพื่อจัดการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        if row['receipt_img']: st.image(row['receipt_img'], width=300)
        
        col_e1, col_e2 = st.columns(2)
        if col_e1.button("✅ ยืนยันแก้ไข (ฟังก์ชันเสริม)"): st.info("ระบบแก้ไขกำลังเชื่อมต่อ...")
        if col_e2.button("🗑️ ลบรายการนี้", use_container_width=True):
            c = conn.cursor()
            c.execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
