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
    
    .main-title { color: #FF69B4; text-align: center; font-size: 50px; font-weight: bold; padding: 10px; margin-top: 20px; }
    
    /* ปรับแต่งปุ่มให้ดูสวยงาม */
    .stButton>button { 
        border-radius: 20px; background-color: white; color: #FF69B4; 
        border: 2px solid #FFB7CE; font-weight: bold; width: 100%; height: 45px;
    }
    .stButton>button:hover { background-color: #FFB7CE; color: white; border: 2px solid #FFB7CE; }
    
    /* ลบ padding ส่วนเกินเพื่อให้ดูสะอาด */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect('meow_stable_v59.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                 wallet TEXT, category TEXT, sub_category TEXT,
                 income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                 receipt_img BLOB)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. LOGIN SYSTEM (แก้ไขให้ขยับมาตรงกลางแล้วครับ) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    # ส่วนหัวหน้า Login
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    
    # ใช้ columns เพื่อขยับเนื้อหามาไว้ตรงกลาง [ซ้าย, กลาง, ขวา]
    _, col_login, _ = st.columns([1.2, 1, 1.2]) 
    
    with col_login:
        st.markdown("<h1 style='text-align: center; font-size: 80px; margin-bottom: 0;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="ระบุชื่อของคุณที่นี่...", label_visibility="visible")
        
        # จัดปุ่มให้อยู่กึ่งกลางในคอลัมน์ตัวเอง
        if st.button("เข้าสู่ระบบ 🐾"):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
raw_df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
if not raw_df.empty:
    raw_df['date'] = pd.to_datetime(raw_df['date'], errors='coerce')
    df = raw_df.dropna(subset=['date']).copy()
else:
    df = pd.DataFrame()

# --- 5. HEADER (แก้ไข Syntax Error บรรทัด 76 เรียบร้อย) ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

# --- 6. NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    ca, cb = st.columns(2)
    with ca:
        d_in = st.date_input("📅 วันที่", datetime.now())
        w_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        t_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        up_file = st.file_uploader("📸 แนบใบเสร็จ", type=['jpg', 'jpeg', 'png'])
    with cb:
        c_map = {
            "รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "ระบุเอง ✍️"],
            "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛒", "ระบุเอง ✍️"],
            "เงินออม 🐷": ["ออมทั่วไป 🏦", "ออมฉุกเฉิน 🚑", "ระบุเอง ✍️"]
        }
        s_cat = st.selectbox("📁 หมวดหมู่", c_map[t_in])
        f_cat = st.text_input("📝 ระบุหมวดหมู่เอง") if s_cat == "ระบุเอง ✍️" else s_cat
        s_det = st.text_input("🔍 รายละเอียด")
        s_amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    
    if st.button("💖 บันทึกรายการ"):
        if s_amt > 0 and f_cat:
            img = up_file.getvalue() if up_file else None
            inc, exp, sav = (s_amt,0,0) if t_in=="รายรับ 💰" else (0,s_amt,0) if t_in=="รายจ่าย 💸" else (0,0,s_amt)
            conn.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                         (user_name, d_in.strftime('%Y-%m-%d'), w_in, f_cat, s_det, inc, exp, sav, img))
            conn.commit(); st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดเงินคงเหลือ")
    w_cols = st.columns(3)
    wallets_list = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets_list):
        bal = 0.0
        if not df.empty:
            w_df = df[df['wallet'] == w_name]
            bal = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum())
        w_cols[i].metric(w_name, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์และกราฟ")
    if not df.empty:
        df_sorted = df.sort_values('date')
        df_sorted['เดือน/ปี'] = df_sorted['date'].dt.strftime('%m/%Y')
        m_stats = df_sorted.groupby('เดือน/ปี')[['income', 'expense']].sum().reset_index().rename(columns={'income':'รายรับ','expense':'รายจ่าย'})
        
        # กราฟแกน Y ห่าง 1,000 เริ่มที่ 0
        fig_bar = px.bar(m_stats, x='เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                         barmode='group', 
                         color_discrete_map={'รายรับ':'#FFB7CE','รายจ่าย':'#B2E2F2'},
                         labels={'value': 'ยอดเงิน (บาท)', 'variable': 'ประเภท'})
        
        fig_bar.update_layout(
            yaxis=dict(tick0=0, dtick=1000, gridcolor='rgba(200, 200, 200, 0.3)'),
            bargap=0.15,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลสำหรับวิเคราะห์เมี๊ยว")

with tab4:
    st.markdown("### 📖 ประวัติและแก้ไข")
    if not df.empty:
        df_sh = df.sort_values(by='id', ascending=False)
        st.dataframe(df_sh.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sid = st.selectbox("เลือก ID รายการ:", df_sh['id'].tolist())
        row = df[df['id'] == sid].iloc[0]
        
        ce1, ce2 = st.columns(2)
        with ce1:
            ed = st.date_input("แก้ไขวัน", row['date'])
            ev = st.number_input("แก้ไขยอดเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
        with ce2:
            ec = st.text_input("แก้ไขหมวดหมู่", value=row['category'])
            es = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])

        if st.button("✅ ยืนยันแก้ไข"):
            ni, ne, ns = (ev,0,0) if row['income']>0 else (0,ev,0) if row['expense']>0 else (0,0,ev)
            conn.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, category=?, sub_category=? WHERE id=?", 
                         (ed.strftime('%Y-%m-%d'), ni, ne, ns, ec, es, sid))
            conn.commit(); st.rerun()

# --- 7. FOOTER (ปุ่มออกจากระบบขยับมาตรงกลาง) ---
st.markdown("---")
_, mid_col, _ = st.columns([1.5, 1, 1.5]) 
with mid_col:
    if st.button("🚪 ออกจากระบบ"): 
        st.session_state.logged_in = False
        st.rerun()
