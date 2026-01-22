import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES (คุมโทนพาสเทลตามรูป) ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; margin-bottom: 0; }
    .meow-card { 
        background: white; border-radius: 20px; padding: 20px; 
        border: 2px solid #FFE4E1; text-align: center; margin-bottom: 15px; 
        min-height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; height: 45px; }
    .stButton>button:hover { background-color: #FFC0CB; color: white; }
    /* ปรับแต่ง Tab ให้เหมือนในรูป */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 10px 10px 0 0; padding: 10px 20px; border: 1px solid #FFE4E1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
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
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="พิมพ์ชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾"):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING & PROCESSING ---
user_name = st.session_state.user_name
raw_df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

if not raw_df.empty:
    raw_df['date'] = pd.to_datetime(raw_df['date'])
    df = raw_df.dropna(subset=['date']).copy()
    current_month = datetime.now().strftime('%Y-%m')
    df_current = df[df['date'].dt.strftime('%Y-%m') == current_month]
else:
    df = pd.DataFrame()
    df_current = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. SMART EMOTION & BUDGET LOGIC ---
budget_limit = 1000.0
current_exp = df_current['expense'].sum() if not df_current.empty else 0
budget_usage = (current_exp / budget_limit)

# เลือกหน้าแมวตามสถานะการเงิน
if total_in > 0 and (total_save / total_in >= 0.3):
    face, msg = "😸", "วันนี้ออมเงินเก่งจัง เค้ายิ้มแก้มปริเลยเมี๊ยวว!"
elif total_out > total_in:
    face, msg = "🙀", "ว้าย! ทาสใช้เงินเกินตัวแล้วนะ ติดลบแบบนี้เค้าตกใจเมี๊ยว!"
else:
    face, msg = "😺", "วันนี้ก็ใช้ชีวิตได้ดีนะทาส ตั้งใจเก็บเงินต่อไปล่ะเมี๊ยวว"

# --- 6. TOP SECTION (เหมือนในรูปเป๊ะ) ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown(f"""
        <div class='meow-card'>
            <h1 style='font-size:80px; margin:0;'>{face}</h1>
            <p style='font-size:16px; margin-top:10px;'>{msg}</p>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True) # เว้นระยะ
    st.write(f"**งบประมาณรายเดือน (ต.ค.): {current_exp:,.2f} / {budget_limit:,.2f} ฿**")
    st.progress(min(budget_usage, 1.0))
    if budget_usage >= 0.9:
        st.markdown("<p style='color:red; font-weight:bold;'>🙀 ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!</p>", unsafe_allow_html=True)

# --- 7. NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

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
    st.markdown("### 🏦 ยอดคงเหลือรายกระเป๋า")
    w_cols = st.columns(3)
    for i, w_n in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        bal = df[df['wallet'] == w_n].apply(lambda x: x['income'] - x['expense'] - x['savings'], axis=1).sum() if not df.empty else 0
        w_cols[i].metric(w_name, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์และกราฟ")
    if not df.empty:
        # กราฟแท่งเปรียบเทียบ
        df_sorted = df.sort_values('date')
        df_sorted['เดือน/ปี'] = df_sorted['date'].dt.strftime('%m/%Y')
        m_stats = df_sorted.groupby('เดือน/ปี')[['income', 'expense']].sum().reset_index().rename(columns={'income':'รายรับ','expense':'รายจ่าย'})
        
        # ปรับสเกลกราฟให้เห็นชัดแม้เงินน้อย
        max_v = max(m_stats['รายรับ'].max(), m_stats['รายจ่าย'].max())
        fig_bar = px.bar(m_stats, x='เดือน/ปี', y=['รายรับ', 'รายจ่าย'], barmode='group', color_discrete_map={'รายรับ':'#FFB7CE','รายจ่าย':'#B2E2F2'})
        fig_bar.update_layout(yaxis=dict(range=[0, max_v * 1.2 if max_v > 0 else 1000]))
        st.plotly_chart(fig_bar, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.pie(df[df['income']>0], values='income', names='category', title="💰 รายรับ"), use_container_width=True)
        with c2: st.plotly_chart(px.pie(df[df['expense']>0], values='expense', names='category', title="🍱 รายจ่าย"), use_container_width=True)

with tab4:
    st.markdown("### 🎯 เป้าหมายการออม")
    g_df = pd.read_sql(f"SELECT * FROM goals WHERE user_id='{user_name}'", conn)
    col_a, col_b = st.columns([1, 1.5])
    with col_a:
        gn = st.text_input("ออมเพื่ออะไร?")
        ga = st.number_input("เป้าหมายยอดเงิน", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            conn.execute("INSERT INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, gn, ga))
            conn.commit(); st.rerun()
    with col_b:
        for _, r in g_df.iterrows():
            with st.expander(f"📌 {r['goal_name']}"):
                p = min(total_save / r['goal_amount'], 1.0) if r['goal_amount'] > 0 else 0
                st.progress(p)
                st.write(f"เก็บได้แล้ว {total_save:,.0f} / {r['goal_amount']:,.0f} ฿")
                if st.button("🗑️ ลบเป้าหมาย", key=f"dg_{r['id']}"):
                    conn.execute("DELETE FROM goals WHERE id=?", (r['id'],))
                    conn.commit(); st.rerun()

with tab5:
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
            if row['receipt_img']: st.image(row['receipt_img'], width=200)
        with ce2:
            ec = st.text_input("แก้ไขหมวดหมู่", value=row['category'])
            es = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
            nu = st.file_uploader("เปลี่ยนใบเสร็จ", type=['jpg', 'png'])

        if st.button("✅ ยืนยันแก้ไข"):
            ni, ne, ns = (ev,0,0) if row['income']>0 else (0,ev,0) if row['expense']>0 else (0,0,ev)
            n_img = nu.getvalue() if nu else row['receipt_img']
            conn.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, category=?, sub_category=?, receipt_img=? WHERE id=?", 
                         (ed.strftime('%Y-%m-%d'), ni, ne, ns, ec, es, n_img, sid))
            conn.commit(); st.rerun()
        
        if st.button("🗑️ ลบรายการนี้"):
            conn.execute("DELETE FROM records WHERE id=?", (sid,))
            conn.commit(); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
