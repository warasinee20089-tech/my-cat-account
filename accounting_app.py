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
        font-family: 'Kanit', sans-serif !important; 
        color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 15px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFE4E1 !important; padding: 15px; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #FFC0CB; color: white; border: none; }
    .badge-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFE4E1; margin-bottom: 20px; height: 180px;
    }
    .badge-title { font-weight: bold; color: #FFB7CE; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def get_db():
    conn = sqlite3.connect('meow_wallet_v40.db', check_same_thread=False)
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

# --- 3. LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="พิมพ์ชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กุมภาพันธ์", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    try:
        return f"{months[date_obj.month]} {date_obj.year + 543}"
    except:
        return "ไม่ระบุเดือน"

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['เดือน'] = df['date'].apply(get_thai_month)

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. UI TABS ---
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
        uploaded_file = st.file_uploader("📸 ใบเสร็จ", type=['jpg', 'jpeg', 'png'])
    with col2:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0:
            img_byte = uploaded_file.getvalue() if uploaded_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            conn.cursor().execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                                  (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, selected_cat, sub_cat, inc, exp, sav, img_byte))
            conn.commit(); st.rerun()

# --- TAB 2: กระเป๋า ---
with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    cw1, cw2, cw3 = st.columns(3)
    for i, w in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum()) if not w_df.empty else 0.0
        [cw1, cw2, cw3][i].metric(w, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ (RESTORED GRAPH) ---
with tab3:
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        # กราฟแท่งเปรียบเทียบ (Restored)
        st.markdown("#### 📈 รายรับและรายจ่ายรายเดือน")
        monthly_df = df.groupby('เดือน')[['income', 'expense']].sum().reset_index()
        monthly_df = monthly_df.rename(columns={'income': 'รายรับ', 'expense': 'รายจ่าย'})
        fig_bar = px.bar(monthly_df, x='เดือน', y=['รายรับ', 'รายจ่าย'], barmode='group', color_discrete_map={'รายรับ': '#FFB7CE', 'รายจ่าย': '#94E1E1'})
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### 🥧 สัดส่วนภาพรวม")
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FFB7CE', '#B2E2F2']), use_container_width=True)
        
        st.markdown("#### 🍱 รายจ่ายแยกตามหมวดหมู่")
        exp_df = df[df['expense'] > 0]
        if not exp_df.empty: st.plotly_chart(px.pie(exp_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูล")

# --- TAB 4: การออม (เป้าหมาย) ---
with tab4:
    st.markdown("### 🎯 เป้าหมายการออม")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        g_name = st.text_input("ออมเพื่อ?")
        g_amt = st.number_input("เป้าหมายยอดเงิน (฿)", min_value=0.0)
        if st.button("🚩 บันทึกเป้าหมาย"):
            conn.cursor().execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, g_name, g_amt))
            conn.commit(); st.rerun()
    with g_col2:
        goal = conn.cursor().execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()
        if goal and goal[2] > 0:
            prog = min(total_save / goal[2], 1.0)
            st.markdown(f"#### เป้าหมาย: **{goal[1]}**")
            st.metric("ความสำเร็จ", f"{prog*100:.1f} %")
            st.progress(prog)

# --- TAB 5: ประวัติและแก้ไข (RESTORED EDIT FORM) ---
with tab5:
    st.markdown("### 📖 ประวัติและแก้ไขรายการ")
    if not df.empty:
        df_show = df.sort_values(by='id', ascending=False)
        st.dataframe(df_show.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### ✏️ จัดการรายการ")
        sel_id = st.selectbox("เลือก ID รายการที่ต้องการจัดการ:", df_show['id'].tolist())
        row = df[df['id'] == sel_id].iloc[0]
        
        if row['receipt_img']: st.image(row['receipt_img'], width=300, caption="ใบเสร็จรายการนี้")
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            new_date = st.date_input("แก้ไขวันที่", pd.to_datetime(row['date']))
            curr_amt = float(row['income'] if row['income'] > 0 else row['expense'] if row['expense'] > 0 else row['savings'])
            new_amt = st.number_input("แก้ไขจำนวนเงิน", value=curr_amt)
        with col_e2:
            new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
            new_wallet = st.selectbox("แก้ไขช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"], index=["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"].index(row['wallet']))
        
        ce1, ce2 = st.columns(2)
        if ce1.button("✅ ยืนยันการแก้ไข", use_container_width=True):
            n_inc, n_exp, n_sav = (new_amt,0,0) if row['income']>0 else (0,new_amt,0) if row['expense']>0 else (0,0,new_amt)
            conn.cursor().execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=?, wallet=? WHERE id=?", 
                                  (new_date.strftime('%Y-%m-%d'), n_inc, n_exp, n_sav, new_sub, new_wallet, sel_id))
            conn.commit(); st.success("อัปเดตเรียบร้อย!"); st.rerun()
        if ce2.button("🗑️ ลบรายการนี้", use_container_width=True):
            conn.cursor().execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
