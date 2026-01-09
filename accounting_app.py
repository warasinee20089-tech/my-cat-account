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
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; height: 45px; }
    .stButton>button:hover { background-color: #FFC0CB; color: white; }
    .budget-red { color: #FF4B4B; font-weight: bold; font-size: 18px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE (SAFE CONNECT) ---
def get_db_connection():
    # ใช้ชื่อไฟล์ใหม่เพื่อเลี่ยงปัญหาโครงสร้างเก่าขัดแย้ง
    conn = sqlite3.connect('meow_ultimate_v42.db', check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
              receipt_img BLOB)''')
c.execute('''CREATE TABLE IF NOT EXISTS goals 
             (user_id TEXT PRIMARY KEY, goal_name TEXT, goal_amount REAL)''')
conn.commit()

# --- 3. SESSION STATE & LOGIN ---
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

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
query = "SELECT * FROM records WHERE user_id=?"
df = pd.read_sql(query, conn, params=(user_name,))

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{months[date_obj.month]} {date_obj.year + 543}"

# เตรียมข้อมูลสำหรับเดือนปัจจุบัน
current_month_str = datetime.now().strftime('%Y-%m')
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df_current = df[df['date'].dt.strftime('%Y-%m') == current_month_str]
else:
    df_current = pd.DataFrame()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. SMART LOGIC: EMOTION & BUDGET ---
# งบประมาณรายเดือนคงที่ 1,000 บาท
budget_limit = 1000.0
current_month_expense = df_current['expense'].sum() if not df_current.empty else 0
budget_usage = (current_month_expense / budget_limit) if budget_limit > 0 else 0

# อารมณ์แมวเปลี่ยนตามสภาวะการเงิน
if total_in > 0 and (total_save / total_in >= 0.3):
    meow_face, meow_msg = "😸", "วันนี้ออมเก่งมากทาส ยิ้มแก้มปริเลยเมี๊ยวว!"
elif total_out > total_in:
    meow_face, meow_msg = "🙀", "ว้าย! ใช้เงินเกินตัวแล้วนะทาส ติดลบแบบนี้เค้าตกใจนะ!"
else:
    meow_face, meow_msg = "😺", "วันนี้ก็ใช้ชีวิตได้ดีนะทาส ตั้งใจเก็บเงินต่อไปล่ะเมี๊ยวว"

# --- 6. MAIN UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

# Dashboard Summary
col_info, col_gauge = st.columns([1, 2])
with col_info:
    st.markdown(f"<div class='meow-card'><h1 style='font-size:65px; margin:0;'>{meow_face}</h1><p>{meow_msg}</p></div>", unsafe_allow_html=True)

with col_gauge:
    st.markdown("<div class='meow-card'>", unsafe_allow_html=True)
    st.write(f"**งบประมาณรายเดือน (ต.ค.): {current_month_expense:,.2f} / {budget_limit:,.2f} ฿**")
    st.progress(min(budget_usage, 1.0))
    if budget_usage >= 0.9:
        st.markdown("<p class='budget-red'>🙀ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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
            cursor = conn.cursor()
            cursor.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                           (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, selected_cat, sub_cat, inc, exp, sav, img_byte))
            conn.commit()
            st.success("บันทึกสำเร็จ!")
            st.rerun()

# --- TAB 2: กระเป๋าเงิน ---
with tab2:
    st.markdown("### 🏦 ยอดคงเหลือในแต่ละช่องทาง")
    w1, w2, w3 = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w in enumerate(wallets):
        temp_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = temp_df['income'].sum() - (temp_df['expense'].sum() + temp_df['savings'].sum()) if not temp_df.empty else 0.0
        [w1, w2, w3][i].metric(w, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ ---
with tab3:
    st.markdown("### 📊 วิเคราะห์การเงิน")
    if not df.empty:
        df['ไทยเดือน'] = df['date'].apply(get_thai_month)
        m_df = df.groupby('ไทยเดือน')[['income', 'expense']].sum().reset_index()
        fig_bar = px.bar(m_df, x='ไทยเดือน', y=['income', 'expense'], barmode='group', color_discrete_map={'income':'#FFB7CE','expense':'#B2E2F2'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🥧 สัดส่วนรายจ่าย")
            if df['expense'].sum() > 0:
                st.plotly_chart(px.pie(df[df['expense']>0], names='category', values='expense', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        with c2:
            st.markdown("#### 🥧 สัดส่วนรายรับ")
            if df['income'].sum() > 0:
                st.plotly_chart(px.pie(df[df['income']>0], names='category', values='income', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

# --- TAB 4: การออม ---
with tab4:
    st.markdown("### 🎯 เป้าหมายของทาสแมว")
    g1, g2 = st.columns(2)
    with g1:
        g_name = st.text_input("ชื่อสิ่งที่อยากได้", placeholder="เช่น ซื้อคอนโดแมว...")
        g_amt = st.number_input("ต้องใช้เงินกี่บาท", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_amt))
            conn.commit()
            st.rerun()
    with g2:
        cursor = conn.cursor()
        goal = cursor.execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal and goal[2] > 0:
            prog = min(total_save / goal[2], 1.0)
            st.markdown(f"<div class='meow-card'><h4>{goal[1]}</h4><h1 style='color:#FFB7CE;'>{prog*100:.1f}%</h1></div>", unsafe_allow_html=True)
            st.progress(prog)
            st.write(f"เก็บได้แล้ว {total_save:,.2f} / {goal[2]:,.2f} ฿")

# --- TAB 5: ประวัติและแก้ไข ---
with tab5:
    st.markdown("### 📖 ประวัติการทำรายการ")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        st.markdown("---")
        sel_id = st.selectbox("เลือก ID รายการเพื่อจัดการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        
        # แสดงใบเสร็จ
        if row['receipt_img']:
            st.image(row['receipt_img'], width=250, caption="ใบเสร็จรายการนี้")
        
        ce1, ce2 = st.columns(2)
        with ce1:
            e_date = st.date_input("แก้ไขวัน", pd.to_datetime(row['date']))
            # ดึงค่าเงินที่บันทึกไว้ (ค่าใดค่าหนึ่งที่ไม่เป็น 0)
            e_amt = float(max(row['income'], row['expense'], row['savings']))
            new_val = st.number_input("แก้ไขจำนวนเงิน", value=e_amt)
        with ce2:
            e_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
        
        if st.button("✅ ยืนยันการแก้ไข"):
            n_inc, n_exp, n_sav = (new_val,0,0) if row['income']>0 else (0,new_val,0) if row['expense']>0 else (0,0,new_val)
            cursor = conn.cursor()
            cursor.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                          (e_date.strftime('%Y-%m-%d'), n_inc, n_exp, n_sav, e_sub, sel_id))
            conn.commit()
            st.success("แก้ไขเรียบร้อย!")
            st.rerun()
            
        if st.button("🗑️ ลบรายการนี้"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit()
            st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
