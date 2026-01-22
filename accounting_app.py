import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES (ปรับหน้า Login และ UI ให้เหมือนรูปเป๊ะ) ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    
    /* พื้นหลังสีชมพูพาสเทล */
    .stApp { background-color: #FFF0F5 !important; }
    
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    
    .main-title { color: #FF69B4; text-align: center; font-size: 50px; font-weight: bold; padding: 10px; margin-top: 20px; }
    
    /* ปรับแต่งปุ่มให้มนและสีพาสเทล */
    .stButton>button { 
        border-radius: 20px; background-color: white; color: #FF69B4; 
        border: 2px solid #FFB7CE; font-weight: bold; width: 100%; height: 45px;
    }
    .stButton>button:hover { background-color: #FFB7CE; color: white; border: 2px solid #FFB7CE; }
    
    /* ปรับแต่ง Progress Bar ให้เป็นสีเขียว */
    div[data-testid="stProgress"] > div > div > div > div { background-color: #98FB98 !important; }
    
    /* กล่องข้อความน้องแมว */
    .meow-speech-bubble {
        background-color: white; border-radius: 20px; padding: 15px;
        border: 2px solid #FFD1DC; text-align: center; margin-bottom: 20px;
    }
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
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, goal_name TEXT, goal_amount REAL)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. LOGIN SYSTEM (หน้า Login เหมือนรูปที่ 1) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="Warasinee", label_visibility="visible")
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

# --- 5. HEADER & EMOTION (ดึงแมวกลับมาตามรูปที่ 2) ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

# ตรรกะอารมณ์แมว
if total_out > total_in:
    face, msg = "🙀", "ว้าย! ทาสใช้เงินเกินตัวแล้วนะ ติดลบแบบนี้เค้าตกใจเมี๊ยว!"
elif total_save > 0:
    face, msg = "😸", "เก่งมากทาส มีเงินออมแบบนี้เค้ายิ้มแก้มปริเลยเมี๊ยวว!"
else:
    face, msg = "😺", "วันนี้ก็ใช้ชีวิตได้ดีนะทาส ตั้งใจเก็บเงินต่อไปล่ะเมี๊ยวว"

# แสดงผลแมวตรงกลางหน้า
st.markdown(f"""
    <div class='meow-speech-bubble'>
        <h1 style='font-size: 80px; margin: 0;'>{face}</h1>
        <p style='font-size: 18px; margin-top: 10px;'>"{msg}"</p>
    </div>
    """, unsafe_allow_html=True)

# --- 6. NAVIGATION TABS ---
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
        
        max_v = max(m_stats['รายรับ'].max(), m_stats['รายจ่าย'].max())
        fig_bar = px.bar(m_stats, x='เดือน/ปี', y=['รายรับ', 'รายจ่าย'], barmode='group', color_discrete_map={'รายรับ':'#FFB7CE','รายจ่าย':'#B2E2F2'})
        fig_bar.update_layout(yaxis=dict(range=[0, max_v * 1.2 if max_v > 0 else 1000]))
        st.plotly_chart(fig_bar, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.pie(df[df['income']>0], values='income', names='category', title="💰 รายรับแยกหมวดหมู่"), use_container_width=True)
        with c2: st.plotly_chart(px.pie(df[df['expense']>0], values='expense', names='category', title="🍱 รายจ่ายแยกหมวดหมู่"), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลสำหรับวิเคราะห์เมี๊ยว")

with tab4:
    # --- หน้าเป้าหมาย (แก้ปัญหาซ้อนกันและเปลี่ยนแถบเป็นสีเขียว ตามรูปที่ 3) ---
    st.markdown("### 🎯 เป้าหมายการออม")
    g_df = pd.read_sql(f"SELECT * FROM goals WHERE user_id='{user_name}'", conn)
    
    col_input, col_display = st.columns([1, 1.5]) # แยก Column ไม่ให้ข้อมูลซ้อนกัน
    
    with col_input:
        st.write("🚩 เพิ่มเป้าหมายใหม่")
        gn = st.text_input("ออมเพื่ออะไร?")
        ga = st.number_input("ยอดเงินเป้าหมาย", min_value=0.0, key="goal_amt_input")
        if st.button("🚩 เพิ่มเป้าหมาย"):
            conn.execute("INSERT INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, gn, ga))
            conn.commit(); st.rerun()
            
    with col_display:
        st.write("🏆 รายการเป้าหมายปัจจุบัน")
        for _, r in g_df.iterrows():
            with st.container():
                # จัด Layout ภายในเป้าหมายให้ดูสะอาด
                st.markdown(f"**📌 {r['goal_name']}**")
                p = min(total_save / r['goal_amount'], 1.0) if r['goal_amount'] > 0 else 0
                st.progress(p) # แถบจะเป็นสีเขียวตาม CSS ด้านบน
                st.write(f"สำเร็จ {p*100:.1f}% ({total_save:,.2f} / {r['goal_amount']:,.2f} ฿)")
                if st.button("🗑️ ลบเป้าหมาย", key=f"dg_{r['id']}"):
                    conn.execute("DELETE FROM goals WHERE id=?", (r['id'],))
                    conn.commit(); st.rerun()
                st.markdown("---")

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
            conn.commit(); st.rerun() # แก้ไขเป็น conn.commit() เรียบร้อยครับ

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
