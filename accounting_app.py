import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

# ฟังก์ชันใส่เสียงคลิก
def add_click_sound():
    sound_url = "https://www.soundjay.com/buttons/button-16.mp3" 
    st.markdown(f"""
        <audio id="clickSound" preload="auto"><source src="{sound_url}" type="audio/mpeg"></audio>
        <script>
            const playMeowSound = () => {{
                const audio = window.parent.document.getElementById('clickSound');
                if (audio) {{ audio.currentTime = 0; audio.play().catch(e => {{}}); }}
            }};
            window.parent.document.addEventListener('click', (e) => {{
                if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {{ playMeowSound(); }}
            }}, true);
        </script>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; margin-bottom: 0; }
    .meow-header-simple { text-align: center; margin-bottom: 25px; }
    .meow-face { font-size: 70px; margin: 0; }
    .meow-speech { font-size: 18px; color: #FF69B4; font-weight: 500; margin-top: -10px; }
    .budget-box { background: white; border-radius: 15px; padding: 15px; border: 1px solid #FFE4E1; margin-bottom: 20px; }
    .budget-red-text { color: #FF4B4B; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

add_click_sound()

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('meow_final_v51.db', check_same_thread=False)
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

# --- 4. DATA LOADING & SAFE CONVERSION ---
user_name = st.session_state.user_name
try:
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    if not df.empty:
        # ป้องกัน AttributeError โดยการแปลงเป็น Datetime ให้ชัวร์ก่อนใช้ .dt
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']) 
except:
    df = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. SMART LOGIC (EMOTION) ---
if total_in > 0 and (total_save / total_in >= 0.3):
    face, msg = "😸", "วันนี้ออมเงินเก่งจัง เค้ายิ้มแก้มปริเลยเมี๊ยวว!"
elif total_out > total_in:
    face, msg = "🙀", "ว้าย! ทาสใช้เงินเกินตัวแล้วนะ ติดลบแบบนี้เค้าตกใจเมี๊ยว!"
else:
    face, msg = "😺", "บริหารเงินได้ดีนะทาส ตั้งใจเก็บเงินต่อไปล่ะเมี๊ยวว"

# HEADER
st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
st.markdown(f"<div class='meow-header-simple'><div class='meow-face'>{face}</div><div class='meow-speech'>\"{msg}\"</div></div>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.button("🔊 คลิกเพื่อเปิดระบบเสียง")
    st.markdown("### ✨ เพิ่มรายการใหม่")
    ca, cb = st.columns(2)
    with ca:
        d_in = st.date_input("📅 วันที่", datetime.now())
        w_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        t_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        up_file = st.file_uploader("📸 ใบเสร็จ", type=['jpg', 'jpeg', 'png'])
    with cb:
        c_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑"]}
        s_cat = st.selectbox("📁 หมวดหมู่", c_map[t_in])
        s_detail = st.text_input("📝 รายละเอียด")
        s_amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ"):
        if s_amt > 0:
            img = up_file.getvalue() if up_file else None
            inc, exp, sav = (s_amt,0,0) if t_in=="รายรับ 💰" else (0,s_amt,0) if t_in=="รายจ่าย 💸" else (0,0,s_amt)
            conn.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                         (user_name, d_in.strftime('%Y-%m-%d'), w_in, s_cat, s_detail, inc, exp, sav, img))
            conn.commit(); st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือรายกระเป๋า")
    w_cols = st.columns(3)
    wallets_list = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_n in enumerate(wallets_list):
        bal = 0.0
        if not df.empty:
            curr_w = df[df['wallet'] == w_n]
            bal = curr_w['income'].sum() - (curr_w['expense'].sum() + curr_w['savings'].sum())
        w_cols[i].metric(w_n, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์และงบประมาณ")
    # Budget Gauge 1,000.-
    curr_m_str = datetime.now().strftime('%Y-%m')
    m_exp = 0.0
    if not df.empty:
        m_exp = df[df['date'].dt.strftime('%Y-%m') == curr_m_str]['expense'].sum()
    
    st.markdown("<div class='budget-box'>", unsafe_allow_html=True)
    st.write(f"**💰 งบประมาณเดือนนี้: {m_exp:,.2f} / 1,000.00 ฿**")
    st.progress(min(m_exp/1000.0, 1.0))
    if m_exp >= 900:
        st.markdown("<p class='budget-red-text'>🙀ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not df.empty:
        # 1. กราฟแท่งเปรียบเทียบ
        df_sorted = df.sort_values('date')
        df_sorted['ไทยเดือน'] = df_sorted['date'].dt.strftime('%m/%Y')
        m_stats = df_sorted.groupby('ไทยเดือน')[['income', 'expense']].sum().reset_index()
        st.plotly_chart(px.bar(m_stats, x='ไทยเดือน', y=['income', 'expense'], barmode='group', 
                               title="📊 รายรับ vs รายจ่ายรายเดือน",
                               color_discrete_map={'income':'#FFB7CE','expense':'#B2E2F2'}), use_container_width=True)
        
        # 2. วงกลมภาพรวม
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, 
                               title="🍰 ภาพรวมการใช้เงิน",
                               color_discrete_sequence=['#FFB7CE', '#B2E2F2']), use_container_width=True)
        
        # 3. วงกลมรายรับ
        i_df = df[df['income'] > 0]
        if not i_df.empty:
            st.plotly_chart(px.pie(i_df.groupby('category')['income'].sum().reset_index(), names='category', values='income', 
                                   title="💰 รายรับแยกตามหมวดหมู่",
                                   color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
        
        # 4. วงกลมรายจ่าย
        e_df = df[df['expense'] > 0]
        if not e_df.empty:
            st.plotly_chart(px.pie(e_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', 
                                   title="🍱 รายจ่ายแยกตามหมวดหมู่",
                                   color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลสำหรับวิเคราะห์เมี๊ยว")

with tab4:
    st.markdown("### 🎯 เป้าหมายการออม")
    g1, g2 = st.columns(2)
    with g1:
        gn = st.text_input("ออมเพื่ออะไร?")
        ga = st.number_input("จำนวนเงินเป้าหมาย", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            conn.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, gn, ga))
            conn.commit(); st.rerun()
    with g2:
        goal = conn.execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal and goal[2] > 0:
            p = min(total_save / goal[2], 1.0)
            st.markdown(f"<div style='background:white; border-radius:15px; padding:20px; text-align:center; border:1px solid #FFE4E1;'><h4>{goal[1]}</h4><h1 style='color:#FFB7CE;'>{p*100:.1f}%</h1></div>", unsafe_allow_html=True)
            st.progress(p)

with tab5:
    st.markdown("### 📖 ประวัติและแก้ไข")
    if not df.empty:
        df_sh = df.sort_values(by='id', ascending=False)
        st.dataframe(df_sh.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sid = st.selectbox("เลือก ID:", df_sh['id'].tolist())
        row = df[df['id'] == sid].iloc[0]
        if row['receipt_img']: st.image(row['receipt_img'], width=200)
        
        c_e1, c_e2 = st.columns(2)
        with c_e1:
            ed = st.date_input("แก้ไขวัน", row['date'])
            ev = st.number_input("แก้ไขยอดเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
        with c_e2:
            es = st.text_input("รายละเอียด", value=row['sub_category'])
        
        b1, b2 = st.columns(2)
        if b1.button("✅ ยืนยันแก้ไข"):
            ni, ne, ns = (ev,0,0) if row['income']>0 else (0,ev,0) if row['expense']>0 else (0,0,ev)
            conn.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", (ed.strftime('%Y-%m-%d'), ni, ne, ns, es, sid))
            conn.commit(); st.rerun()
        if b2.button("🗑️ ลบรายการ"):
            conn.execute("DELETE FROM records WHERE id=?", (sid,))
            conn.commit(); st.rerun()
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
