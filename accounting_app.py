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
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 10px; }
    .stButton>button { border-radius: 10px; border: none; background-color: #FF69B4; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #FF1493; }
    
    .badge-card {
        background: white; border-radius: 20px; padding: 15px; text-align: center;
        border: 2px solid #FFD1DC; margin-bottom: 10px; height: 160px;
    }
    .badge-icon { font-size: 45px; margin-bottom: 5px; }
    .badge-title { font-weight: bold; color: #FF69B4; font-size: 16px; }
    .badge-desc { font-size: 13px; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
def get_db():
    # เปลี่ยนชื่อไฟล์ DB เล็กน้อยเพื่อสร้างใหม่ลดโอกาส Error
    conn = sqlite3.connect('meow_wallet_stable.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
              receipt_img BLOB)''')
c.execute('''CREATE TABLE IF NOT EXISTS goals 
             (user_id TEXT PRIMARY KEY, goal_name TEXT, goal_amount REAL)''')
conn.commit()

# --- 3. LOGIN PAGE (แมวใหญ่กลับมาเฝ้าหน้าบ้าน) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        st.markdown("<h1 style='text-align: center; font-size: 120px; margin-bottom: 0;'>🐱</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #FF69B4;'>ยินดีต้อนรับทาสแมวเมี๊ยวว</h3>", unsafe_allow_html=True)
        u_name = st.text_input("ชื่อของคุณ:", placeholder="กรอกชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if u_name.strip():
                st.session_state.user_name = u_name.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOAD ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{months[date_obj.month]} {date_obj.year + 543}"

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. TABS ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

# --- TAB 1: บันทึก ---
with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        up_file = st.file_uploader("📸 ใบเสร็จ", type=['jpg','png','jpeg'])
    with col2:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0:
            img = up_file.getvalue() if up_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, selected_cat, sub_cat, inc, exp, sav, img))
            conn.commit(); st.rerun()

# --- TAB 2: กระเป๋า (คำนวณแยกช่องทาง) ---
with tab2:
    st.markdown("### 🏦 ยอดคงเหลือในกระเป๋า")
    cw1, cw2, cw3 = st.columns(3)
    for i, w in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum())
        [cw1, cw2, cw3][i].metric(w, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ (RESTORED CHARTS) ---
with tab3:
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        ca1, ca2, ca3 = st.columns(3)
        exp_df = df[df['expense'] > 0]
        # เหรียญตรา logic
        t_cat = exp_df.groupby('category')['expense'].sum().idxmax() if not exp_df.empty else "ไม่มี"
        ca1.markdown(f"<div class='badge-card'><div class='badge-icon'>🍱</div><div class='badge-title'>นักชิม/นักช้อป</div><p class='badge-desc'>เน้นหนักหมวด {t_cat}</p></div>", unsafe_allow_html=True)
        
        s_icon, s_title, s_desc = ("👑", "ราชา/ราชินีนักออม", "ออมโหดเหมือนโกรธใครมา!") if (total_in > 0 and (total_save/total_in >= 0.5)) else ("🙀", "ไหแตกแล้วเมี๊ยว", "ยังไม่ได้ออมเลย!") if total_save == 0 else ("🌱", "ต้นกล้า", "วินัยดีเริ่มสะสม")
        ca3.markdown(f"<div class='badge-card'><div class='badge-icon'>{s_icon}</div><div class='badge-title'>{s_title}</div><p class='badge-desc'>{s_desc}</p></div>", unsafe_allow_html=True)

        st.markdown("#### 🥧 สัดส่วนภาพรวม")
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FF9AA2', '#B2E2F2']), use_container_width=True)
        
        st.markdown("#### 🍱 รายจ่ายแยกตามหมวดหมู่")
        if not exp_df.empty:
            st.plotly_chart(px.pie(exp_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        
        st.markdown("#### 💰 รายรับแยกตามหมวดหมู่")
        inc_df = df[df['income'] > 0]
        if not inc_df.empty:
            st.plotly_chart(px.pie(inc_df.groupby('category')['income'].sum().reset_index(), names='category', values='income', color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลบันทึกเมี๊ยวว")

# --- TAB 4: การออม (ตั้งเป้าหมาย) ---
with tab4:
    st.markdown("### 🎯 ตั้งเป้าหมายการออม")
    gc1, gc2 = st.columns(2)
    with gc1:
        gn = st.text_input("ออมเงินเพื่ออะไร?")
        ga = st.number_input("ยอดเงินเป้าหมาย (฿)", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            c.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, gn, ga))
            conn.commit(); st.rerun()
    with gc2:
        goal = c.execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal:
            st.markdown(f"#### เป้าหมาย: **{goal['goal_name']}**")
            p = min(total_save / goal['goal_amount'], 1.0) if goal['goal_amount'] > 0 else 0
            st.progress(p)
            st.metric("เงินออมปัจจุบัน", f"{total_save:,.2f} / {goal['goal_amount']:,.2f}")

# --- TAB 5: ประวัติ ---
with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_sh = df.sort_values(by='id', ascending=False)
        st.dataframe(df_sh.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sid = st.selectbox("เลือก ID รายการเพื่อดูใบเสร็จหรือลบ:", df_sh['id'].tolist())
        row = df[df['id'] == sid].iloc[0]
        if row['receipt_img']: st.image(row['receipt_img'], width=300)
        if st.button("🗑️ ลบรายการนี้", use_container_width=True):
            c.execute("DELETE FROM records WHERE id=?", (sid,))
            conn.commit(); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
