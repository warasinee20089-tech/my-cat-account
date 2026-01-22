import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Meow Wallet Pro", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; height: 45px; }
    .budget-box { background: white; border-radius: 15px; padding: 15px; border: 1px solid #FFE4E1; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('meow_pro_v54.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                  wallet TEXT, category TEXT, sub_category TEXT,
                  income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                  receipt_img BLOB)''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, goal_name TEXT, goal_amount REAL)''')
    conn.commit()
    return conn

conn = init_db()

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

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
raw_df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
if not raw_df.empty:
    raw_df['date'] = pd.to_datetime(raw_df['date'], errors='coerce')
    df = raw_df.dropna(subset=['date']).copy()
else:
    df = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. UI HEADER ---
face, msg = ("😸", "ออมเงินเก่งมากทาส!") if total_save > 0 else ("😺", "ยินดีต้อนรับทาสแมว!")
st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h1 style='margin:0;'>{face}</h1><p style='color:#FF69B4;'>\"{msg}\"</p></div>", unsafe_allow_html=True)

# --- 6. TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 เป้าหมาย", "📖 ประวัติและแก้ไข"])

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
        final_cat = st.text_input("📝 ระบุหมวดหมู่ใหม่") if s_cat == "ระบุเอง ✍️" else s_cat
        s_detail = st.text_input("🔍 รายละเอียด")
        s_amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    
    if st.button("💖 บันทึกรายการ"):
        if s_amt > 0 and final_cat:
            img = up_file.getvalue() if up_file else None
            inc, exp, sav = (s_amt,0,0) if t_in == "รายรับ 💰" else (0,s_amt,0) if t_in == "รายจ่าย 💸" else (0,0,s_amt)
            conn.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                         (user_name, d_in.strftime('%Y-%m-%d'), w_in, final_cat, s_detail, inc, exp, sav, img))
            conn.commit(); st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    w_cols = st.columns(3)
    for i, w_n in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        bal = df[df['wallet'] == w_n].apply(lambda x: x['income'] - x['expense'] - x['savings'], axis=1).sum() if not df.empty else 0
        w_cols[i].metric(w_n, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 สรุปและวิเคราะห์")
    if not df.empty:
        # Budget Gauge 1,000.-
        m_exp = df[df['date'].dt.strftime('%m/%Y') == datetime.now().strftime('%m/%Y')]['expense'].sum()
        st.markdown(f"<div class='budget-box'>💰 งบเดือนนี้: {m_exp:,.2f} / 1,000.00 ฿</div>", unsafe_allow_html=True)
        st.progress(min(m_exp/1000.0, 1.0))
        
        # กราฟแท่งเปรียบเทียบ
        df['เดือน/ปี'] = df['date'].dt.strftime('%m/%Y')
        m_df = df.groupby('เดือน/ปี')[['income', 'expense']].sum().reset_index()
        fig_bar = px.bar(m_df, x='เดือน/ปี', y=['income', 'expense'], barmode='group', 
                         title="📈 รายรับ vs รายจ่ายรายเดือน",
                         color_discrete_map={'income':'#FFB7CE','expense':'#B2E2F2'})
        st.plotly_chart(fig_bar, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 💰 รายรับ")
            if total_in > 0: st.plotly_chart(px.pie(df[df['income']>0], values='income', names='category', hole=0.4), use_container_width=True)
        with c2:
            st.markdown("#### 🍱 รายจ่าย")
            if total_out > 0: st.plotly_chart(px.pie(df[df['expense']>0], values='expense', names='category', hole=0.4), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

with tab4:
    st.markdown("### 🎯 เป้าหมายการออม")
    g_col1, g_col2 = st.columns([1, 1.5])
    with g_col1:
        gn = st.text_input("ชื่อเป้าหมายใหม่")
        ga = st.number_input("ยอดเงินเป้าหมาย", min_value=0.0)
        if st.button("➕ เพิ่มเป้าหมาย"):
            conn.execute("INSERT INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, gn, ga))
            conn.commit(); st.rerun()
    with g_col2:
        g_df = pd.read_sql(f"SELECT * FROM goals WHERE user_id='{user_name}'", conn)
        for _, r in g_df.iterrows():
            with st.expander(f"📌 {r['goal_name']}"):
                p = min(total_save / r['goal_amount'], 1.0) if r['goal_amount'] > 0 else 0
                st.progress(p)
                st.write(f"สำเร็จ {p*100:.1f}% ({total_save:,.0f}/{r['goal_amount']:,.0f} ฿)")
                if st.button("🗑️ ลบเป้าหมาย", key=f"dg_{r['id']}"):
                    conn.execute("DELETE FROM goals WHERE id=?", (r['id'],))
                    conn.commit(); st.rerun()

with tab5:
    st.markdown("### 📖 ประวัติและแก้ไข")
    if not df.empty:
        df_sh = df.sort_values(by='id', ascending=False)
        st.dataframe(df_sh.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        st.markdown("---")
        sid = st.selectbox("เลือก ID เพื่อแก้ไข/ลบ:", df_sh['id'].tolist())
        row = df[df['id'] == sid].iloc[0]
        
        ce1, ce2 = st.columns(2)
        with ce1:
            ed = st.date_input("แก้ไขวัน", row['date'])
            ev = st.number_input("แก้ไขเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
            ei = st.file_uploader("เปลี่ยนใบเสร็จ", type=['jpg', 'png'])
        with ce2:
            ec = st.text_input("แก้ไขหมวดหมู่", value=row['category'])
            es = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
            if row['receipt_img']: st.image(row['receipt_img'], width=200, caption="ใบเสร็จเดิม")

        b1, b2 = st.columns(2)
        if b1.button("✅ ยืนยันการแก้ไข"):
            img = ei.getvalue() if ei else row['receipt_img']
            ni, ne, ns = (ev,0,0) if row['income']>0 else (0,ev,0) if row['expense']>0 else (0,0,ev)
            conn.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, category=?, sub_category=?, receipt_img=? WHERE id=?", 
                         (ed.strftime('%Y-%m-%d'), ni, ne, ns, ec, es, img, sid))
            conn.commit(); st.success("แก้ไขสำเร็จ!"); st.rerun()
        
        if b2.button("🗑️ ลบรายการนี้"):
            conn.execute("DELETE FROM records WHERE id=?", (sid,)) # แก้ไขจาก co เป็น conn เรียบร้อย
            conn.commit(); st.warning("ลบรายการแล้ว!"); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
