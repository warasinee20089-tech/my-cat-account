import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Meow Wallet Stable", layout="wide", page_icon="🐾")

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('meow_stable_v52.db', check_same_thread=False)
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

# --- 3. LOGIN SYSTEM ---
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
raw_df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

if not raw_df.empty:
    # แปลงวันที่ให้เป็น Datetime Object เสมอเพื่อป้องกัน Error ในกราฟ
    raw_df['date'] = pd.to_datetime(raw_df['date'], errors='coerce')
    df = raw_df.dropna(subset=['date']).copy()
else:
    df = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. UI HEADER ---
if total_out > total_in:
    face, msg = "🙀", "ทาสใช้เงินเกินตัวแล้วนะ! เค้านิ้วกุมขมับเลยเมี๊ยว"
elif total_save > 0:
    face, msg = "😸", "เก่งมากทาส มีเงินออมแบบนี้เค้าภูมิใจเมี๊ยว"
else:
    face, msg = "😺", "ยินดีต้อนรับกลับมานะเมี๊ยวว"

st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
st.markdown(f"<div class='meow-header-simple'><div class='meow-face'>{face}</div><div class='meow-speech'>\"{msg}\"</div></div>", unsafe_allow_html=True)

# --- 6. TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึกรายวัน", "👛 กระเป๋าเงิน", "📊 สรุปและกราฟ", "🎯 เป้าหมาย", "📖 ประวัติ/แก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        d_in = st.date_input("📅 วันที่", datetime.now())
        w_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        t_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        up_file = st.file_uploader("📸 แนบใบเสร็จ (Optional)", type=['jpg', 'jpeg', 'png'])
    with col2:
        c_map = {
            "รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"],
            "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ที่พัก 🏠", "ช้อปปิ้ง 🛒", "อื่นๆ ➕"],
            "เงินออม 🐷": ["ออมทั่วไป 🏦", "ออมฉุกเฉิน 🚑"]
        }
        s_cat = st.selectbox("📁 หมวดหมู่", c_map[t_in])
        s_detail = st.text_input("📝 รายละเอียดเพิ่มเติม")
        s_amt = st.number_input("💵 จำนวนเงิน", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการลงกระเป๋า"):
        if s_amt > 0:
            img_data = up_file.getvalue() if up_file else None
            inc = s_amt if t_in == "รายรับ 💰" else 0
            exp = s_amt if t_in == "รายจ่าย 💸" else 0
            sav = s_amt if t_in == "เงินออม 🐷" else 0
            
            conn.execute("""INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) 
                         VALUES (?,?,?,?,?,?,?,?,?)""", 
                         (user_name, d_in.strftime('%Y-%m-%d'), w_in, s_cat, s_detail, inc, exp, sav, img_data))
            conn.commit()
            st.success("บันทึกเรียบร้อยเมี๊ยว!")
            st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดเงินคงเหลือ")
    w_cols = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        if not df.empty:
            w_df = df[df['wallet'] == w_name]
            balance = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum())
        else: balance = 0
        w_cols[i].metric(w_name, f"{balance:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์การเงิน")
    if not df.empty:
        # 1. กราฟแท่งเปรียบเทียบรายเดือน
        st.markdown("#### 📅 รายรับ vs รายจ่าย (แยกรายเดือน)")
        df['Month-Year'] = df['date'].dt.strftime('%m/%Y')
        monthly_data = df.groupby('Month-Year')[['income', 'expense']].sum().reset_index()
        fig_bar = px.bar(monthly_data, x='Month-Year', y=['income', 'expense'], 
                         barmode='group', color_discrete_map={'income':'#FFB7CE','expense':'#B2E2F2'},
                         labels={'value':'จำนวนเงิน (บาท)', 'variable':'ประเภท'})
        st.plotly_chart(fig_bar, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            # 2. วงกลมรายรับแยกหมวดหมู่
            st.markdown("#### 💰 สัดส่วนรายรับ")
            inc_df = df[df['income'] > 0]
            if not inc_df.empty:
                fig_inc = px.pie(inc_df, values='income', names='category', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_inc, use_container_width=True)
            else: st.write("ไม่มีข้อมูลรายรับ")
            
        with c2:
            # 3. วงกลมรายจ่ายแยกหมวดหมู่
            st.markdown("#### 🍱 สัดส่วนรายจ่าย")
            exp_df = df[df['expense'] > 0]
            if not exp_df.empty:
                fig_exp = px.pie(exp_df, values='expense', names='category', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_exp, use_container_width=True)
            else: st.write("ไม่มีข้อมูลรายจ่าย")
    else:
        st.info("เพิ่มข้อมูลก่อนเพื่อดูผลวิเคราะห์นะเมี๊ยว")

with tab4:
    st.markdown("### 🎯 เป้าหมายการออมเงิน")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        g_name = st.text_input("ชื่อเป้าหมาย (เช่น ซื้อคอนโดแมว)")
        g_target = st.number_input("ยอดเงินที่ต้องการ", min_value=0.0)
        if st.button("🚩 ตั้งเป้าหมาย"):
            conn.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_target))
            conn.commit(); st.rerun()
    with g_col2:
        goal_data = conn.execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal_data and goal_data[2] > 0:
            progress = min(total_save / goal_data[2], 1.0)
            st.markdown(f"<div class='budget-box' style='text-align:center;'><h4>{goal_data[1]}</h4><h2 style='color:#FFB7CE;'>{progress*100:.1f}%</h2></div>", unsafe_allow_html=True)
            st.progress(progress)

with tab5:
    st.markdown("### 📖 ประวัติรายการและใบเสร็จ")
    if not df.empty:
        df_display = df.sort_values(by='id', ascending=False)
        st.dataframe(df_display.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🔍 ดูใบเสร็จหรือลบรายการ")
        selected_id = st.selectbox("เลือก ID รายการที่ต้องการ:", df_display['id'].tolist())
        target_row = df[df['id'] == selected_id].iloc[0]
        
        if target_row['receipt_img']:
            st.image(target_row['receipt_img'], caption="ใบเสร็จที่บันทึกไว้", width=300)
        else:
            st.write("รายการนี้ไม่มีใบเสร็จ")
            
        if st.button("🗑️ ลบรายการนี้"):
            conn.execute("DELETE FROM records WHERE id=?", (selected_id,))
            conn.commit()
            st.warning(f"ลบรายการ ID {selected_id} แล้ว")
            st.rerun()
    else:
        st.write("ยังไม่มีประวัติเมี๊ยว")

# --- FOOTER ---
st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
