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
    .main-title { color: #FFB7CE; text-align: center; font-size: 35px; font-weight: bold; padding: 5px; }
    .meow-header-card { 
        background: white; border-radius: 20px; padding: 15px; border: 2px solid #FFE4E1; 
        text-align: center; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 20px;
    }
    .meow-face { font-size: 50px; margin: 0; }
    .meow-speech { font-size: 16px; margin: 0; font-style: italic; color: #FF69B4; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; }
    .budget-box { background: #ffffff; border-radius: 15px; padding: 15px; border: 1px solid #FFE4E1; margin-bottom: 20px; }
    .budget-red-text { color: #FF4B4B; font-weight: bold; font-size: 16px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def get_db():
    conn = sqlite3.connect('meow_ultimate_v43.db', check_same_thread=False)
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

# --- 3. LOGIN SYSTEM ---
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

# --- 4. DATA PROCESSING ---
user_name = st.session_state.user_name
df = pd.read_sql("SELECT * FROM records WHERE user_id=?", conn, params=(user_name,))

# คำนวณภาพรวม
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. SMART EMOTION LOGIC ---
if total_in > 0 and (total_save / total_in >= 0.3):
    meow_face, meow_msg = "😸", "วันนี้ทาสออมเงินเก่งจัง เค้ายิ้มแก้มปริเลยเมี๊ยวว!"
elif total_out > total_in:
    meow_face, meow_msg = "🙀", "ว้าย! ทาสใช้เงินเกินตัวแล้วนะ ติดลบแบบนี้เค้าตกใจเมี๊ยว!"
else:
    meow_face, meow_msg = "😺", "บริหารเงินได้ดีนะทาส ตั้งใจเก็บเงินต่อไปล่ะเมี๊ยวว"

# --- 6. HEADER SECTION (อารมณ์แมวในกรอบ) ---
st.markdown(f"""
    <div class='meow-header-card'>
        <div class='meow-face'>{meow_face}</div>
        <div class='meow-speech'>"{meow_msg}"</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

# --- 7. TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

# --- TAB 1: บันทึก ---
with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    ca, cb = st.columns(2)
    with ca:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        uploaded_file = st.file_uploader("📸 แนบใบเสร็จ", type=['jpg', 'jpeg', 'png'])
    with cb:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0, step=10.0)
    
    if st.button("💖 บันทึกรายการ"):
        if amt > 0:
            img_byte = uploaded_file.getvalue() if uploaded_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            conn.cursor().execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                           (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, selected_cat, sub_cat, inc, exp, sav, img_byte))
            conn.commit(); st.rerun()

# --- TAB 2: กระเป๋าเงิน ---
with tab2:
    st.markdown("### 🏦 ยอดคงเหลือรายกระเป๋า")
    w1, w2, w3 = st.columns(3)
    for i, w in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum())
        [w1, w2, w3][i].metric(w, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ (ย้ายงบประมาณมาไว้ที่นี่) ---
with tab3:
    st.markdown("### 📊 วิเคราะห์และงบประมาณ")
    
    # ส่วนงบประมาณ (1,000.-)
    current_month = datetime.now().strftime('%Y-%m')
    if not df.empty:
        df['date_dt'] = pd.to_datetime(df['date'])
        month_exp = df[df['date_dt'].dt.strftime('%Y-%m') == current_month]['expense'].sum()
    else: month_exp = 0
    
    budget_limit = 1000.0
    usage_pct = (month_exp / budget_limit) if budget_limit > 0 else 0
    
    st.markdown("<div class='budget-box'>", unsafe_allow_html=True)
    st.write(f"**💰 งบประมาณรายเดือน: {month_exp:,.2f} / {budget_limit:,.2f} ฿**")
    st.progress(min(usage_pct, 1.0))
    if usage_pct >= 0.9:
        st.markdown("<p class='budget-red-text'>🙀ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not df.empty:
        st.markdown("#### 🥧 สัดส่วนการใช้เงิน")
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FFB7CE', '#B2E2F2']), use_container_width=True)
        
        st.markdown("#### 📈 รายจ่ายแยกตามหมวดหมู่")
        exp_df = df[df['expense'] > 0]
        if not exp_df.empty:
            st.plotly_chart(px.pie(exp_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลให้วิเคราะห์เมี๊ยว")

# --- TAB 4: การออม ---
with tab4:
    st.markdown("### 🎯 เป้าหมายของทาสแมว")
    g1, g2 = st.columns(2)
    with g1:
        g_name = st.text_input("ชื่อเป้าหมาย", placeholder="เช่น ซื้อคอนโดแมว...")
        g_amt = st.number_input("จำนวนเงินที่ต้องการ", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            conn.cursor().execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_amt))
            conn.commit(); st.rerun()
    with g2:
        goal = conn.cursor().execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal and goal[2] > 0:
            prog = min(total_save / goal[2], 1.0)
            st.markdown(f"<div style='background:white; border-radius:15px; padding:20px; text-align:center; border:1px solid #FFE4E1;'><h4>{goal[1]}</h4><h1 style='color:#FFB7CE;'>{prog*100:.1f}%</h1></div>", unsafe_allow_html=True)
            st.progress(prog)
            st.write(f"เก็บได้ {total_save:,.2f} / {goal[2]:,.2f} ฿")

# --- TAB 5: ประวัติและแก้ไข ---
with tab5:
    st.markdown("### 📖 ประวัติและแก้ไขรายการ")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sel_id = st.selectbox("เลือก ID รายการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        
        if row['receipt_img']: st.image(row['receipt_img'], width=250)
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            new_date = st.date_input("แก้ไขวันที่", pd.to_datetime(row['date']))
            curr_val = float(max(row['income'], row['expense'], row['savings']))
            new_val = st.number_input("แก้ไขยอดเงิน", value=curr_val)
        with col_e2:
            new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
        
        c_btn1, c_btn2 = st.columns(2)
        if c_btn1.button("✅ ยืนยันการแก้ไข"):
            n_inc, n_exp, n_sav = (new_val,0,0) if row['income']>0 else (0,new_val,0) if row['expense']>0 else (0,0,new_val)
            conn.cursor().execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                                  (new_date.strftime('%Y-%m-%d'), n_inc, n_exp, n_sav, new_sub, sel_id))
            conn.commit(); st.rerun()
        if c_btn2.button("🗑️ ลบรายการนี้"):
            conn.cursor().execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
