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
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; }
    .meow-card { background: white; border-radius: 20px; padding: 20px; border: 2px solid #FFE4E1; text-align: center; margin-bottom: 15px; }
    .badge-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFE4E1; height: 220px; display: flex; flex-direction: column; justify-content: center;
    }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; height: 45px; }
    .budget-red { color: #FF4B4B; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
def get_db():
    # ใช้ชื่อไฟล์ใหม่เพื่อป้องกัน Error จากโครงสร้างเดิมที่ทับซ้อน
    conn = sqlite3.connect('meow_wallet_master_v42.db', check_same_thread=False)
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
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="กรอกชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾"):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA PROCESSING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{months[date_obj.month]} {date_obj.year + 543}"

current_month_str = datetime.now().strftime('%Y-%m')
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df_current = df[df['date'].dt.strftime('%Y-%m') == current_month_str]
else:
    df_current = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. SMART EMOTION & BUDGET LOGIC ---
budget_limit = 1000.0
current_month_expense = df_current['expense'].sum() if not df_current.empty else 0
budget_usage = (current_month_expense / budget_limit)

# Emotion Logic
if total_in > 0 and (total_save / total_in >= 0.3):
    meow_face, meow_msg = "😸", "(ทาสออมเก่งมาก ยิ้มแก้มปริ!)"
elif total_out > total_in:
    meow_face, meow_msg = "🙀", "(ทาสใช้เงินเกินงบแล้ว! ตกใจล้าวว)"
else:
    meow_face, meow_msg = "😺", "(วันนี้ทำดีแล้วเมี๊ยวว)"

# --- 6. MAIN UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

# Status Bar
col_status, col_gauge = st.columns([1, 2])
with col_status:
    st.markdown(f"<div class='meow-card'><h1 style='font-size:50px; margin:0;'>{meow_face}</h1><p>{meow_msg}</p></div>", unsafe_allow_html=True)
with col_gauge:
    st.markdown("<div class='meow-card'>", unsafe_allow_html=True)
    st.write(f"**งบประมาณเดือนนี้: {current_month_expense:,.2f} / {budget_limit:,.2f} ฿**")
    st.progress(min(budget_usage, 1.0))
    if budget_usage >= 0.9:
        st.markdown("<p class='budget-red'>🙀ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

# --- TAB 1: บันทึก ---
with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col_a, col_b = st.columns(2)
    with col_a:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
    with col_b:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ"):
        if amt > 0:
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            conn.cursor().execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                                  (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, selected_cat, sub_cat, inc, exp, sav))
            conn.commit(); st.success("บันทึกสำเร็จ!"); st.rerun()

# --- TAB 3: วิเคราะห์ (ตามภาพตัวอย่าง) ---
with tab3:
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        # เหรียญตรา
        c_a1, c_a2, c_a3 = st.columns(3)
        exp_df = df[df['expense'] > 0]
        
        # 1. เหรียญรายจ่าย
        with c_a1:
            if not exp_df.empty:
                top_cat = exp_df.groupby('category')['expense'].sum().idxmax()
                top_amt = exp_df.groupby('category')['expense'].sum().max()
                icon = "🍛" if "อาหาร" in top_cat else "🛍️"
                title = "นักชิมอันดับหนึ่ง" if "อาหาร" in top_cat else "นักช้อปมือไว"
                st.markdown(f"<div class='badge-card'><h1 style='margin:0;'>{icon}</h1><p class='badge-title'>{title}</p><p>เน้นจ่ายหนักที่ <b>{top_cat}</b><br>รวม {top_amt:,.0f} ฿</p></div>", unsafe_allow_html=True)
            else: st.markdown("<div class='badge-card'>ยังไม่มีรายจ่าย</div>", unsafe_allow_html=True)

        # 2. เหรียญรายรับ
        with c_a2:
            inc_df = df[df['income'] > 0]
            if not inc_df.empty:
                top_inc = inc_df.groupby('category')['income'].sum().idxmax()
                st.markdown(f"<div class='badge-card'><h1 style='margin:0;'>💎</h1><p class='badge-title'>แหล่งเงินถุงเงินถัง</p><p>รายรับหลักมาจาก <b>{top_inc}</b><br>ยอดเยี่ยมมากเมี๊ยว!</p></div>", unsafe_allow_html=True)
            else: st.markdown("<div class='badge-card'>รอเงินเข้าเมี๊ยว</div>", unsafe_allow_html=True)

        # 3. เหรียญเงินออม
        with c_a3:
            s_pct = (total_save / total_in * 100) if total_in > 0 else 0
            icon_s = "👑" if s_pct >= 50 else "🛡️"
            title_s = "ราชา/ราชินีนักออม" if s_pct >= 50 else "ป้อมปราการเงินออม"
            st.markdown(f"<div class='badge-card'><h1 style='margin:0;'>{icon_s}</h1><p class='badge-title'>{title_s}</p><p>ออมไปแล้ว <b>{s_pct:.1f}%</b><br>จากรายรับทั้งหมด</p></div>", unsafe_allow_html=True)

        st.markdown("---")
        # กราฟแท่งเปรียบเทียบ
        st.markdown("#### 📈 เปรียบเทียบรายรับและรายจ่ายรายเดือน")
        df['ไทยเดือน'] = df['date'].apply(get_thai_month)
        m_df = df.groupby('ไทยเดือน')[['income', 'expense']].sum().reset_index()
        fig_bar = px.bar(m_df, x='ไทยเดือน', y=['income', 'expense'], barmode='group', 
                         color_discrete_map={'income':'#FFB7CE','expense':'#B2E2F2'},
                         labels={'value': 'จำนวนเงิน (บาท)', 'variable': 'ประเภท'})
        st.plotly_chart(fig_bar, use_container_width=True)

        # กราฟวงกลม
        st.markdown("#### 🍰 1. สัดส่วนการใช้จ่ายและเงินออม")
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FF9AA2', '#B2E2F2']), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

# --- TAB 5: ประวัติและแก้ไข ---
with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        sel_id = st.selectbox("เลือก ID รายการเพื่อจัดการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        
        ce1, ce2 = st.columns(2)
        with ce1:
            e_date = st.date_input("แก้ไขวันที่", pd.to_datetime(row['date']))
            e_amt = st.number_input("แก้ไขยอดเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
        with ce2:
            e_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
            if st.button("✅ ยืนยันการแก้ไข"):
                n_inc, n_exp, n_sav = (e_amt,0,0) if row['income']>0 else (0,e_amt,0) if row['expense']>0 else (0,0,e_amt)
                conn.cursor().execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                                      (e_date.strftime('%Y-%m-%d'), n_inc, n_exp, n_sav, e_sub, sel_id))
                conn.commit(); st.success("แก้ไขข้อมูลแล้ว!"); st.rerun()
        if st.button("🗑️ ลบรายการนี้"):
            conn.cursor().execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
