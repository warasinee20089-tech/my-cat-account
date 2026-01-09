import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import io
from PIL import Image

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
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 15px; }
    .stButton>button { border-radius: 10px; }
    .badge-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFD1DC; margin-bottom: 20px; transition: 0.3s; height: 180px;
    }
    .badge-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(255,182,193,0.3); }
    .badge-icon { font-size: 50px; margin-bottom: 10px; }
    .badge-title { font-weight: bold; color: #FF69B4; font-size: 18px; }
    .badge-desc { font-size: 14px; color: #666; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE (เพิ่ม Column สำหรับเก็บรูปภาพ) ---
def get_db():
    conn = sqlite3.connect('meow_wallet_v33.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
              receipt_img BLOB)''')
# ตารางสำหรับเป้าหมายการออม
c.execute('''CREATE TABLE IF NOT EXISTS goals 
             (user_id TEXT PRIMARY KEY, goal_name TEXT, goal_amount REAL)''')
conn.commit()

# --- 3. LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_l2, _ = st.columns([1, 2, 1])
    with col_l2:
        name_in = st.text_input("ชื่อทาสแมว:", key="login_name")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
goal_data = c.execute("SELECT * FROM goals WHERE user_id=?", (user_name,)).fetchone()

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

# --- TAB 1: บันทึก (เพิ่ม Upload ใบเสร็จ) ---
with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        uploaded_file = st.file_uploader("📸 อัปโหลดใบเสร็จ (ถ้ามี)", type=['jpg', 'jpeg', 'png'])
    with col2:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        final_cat = st.text_input("✍️ ระบุเอง") if selected_cat == "อื่นๆ ➕" else selected_cat
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)

    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0:
            img_byte = uploaded_file.getvalue() if uploaded_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_cat, sub_cat, inc, exp, sav, img_byte))
            conn.commit(); st.success("บันทึกสำเร็จเมี๊ยวว!"); st.rerun()

# --- TAB 2 & 3 (คงเดิมแต่เพิ่ม Badge Logic ที่เสถียร) ---
with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    cw1, cw2, cw3 = st.columns(3)
    for i, w in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        [cw1, cw2, cw3][i].metric(w, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        ca1, ca2, ca3 = st.columns(3)
        # เหรียญตรา logic (v.32)
        exp_df = df[df['expense'] > 0]
        t_cat = exp_df.groupby('category')['expense'].sum().idxmax() if not exp_df.empty else "ไม่มี"
        t_amt = exp_df.groupby('category')['expense'].sum().max() if not exp_df.empty else 0
        e_icon, e_title = ("🛍️", "นักช้อปมือไว") if "ช้อปปิ้ง" in t_cat else ("🍛", "นักชิมอันดับหนึ่ง") if "อาหาร" in t_cat else ("📦", "นักจัดการ")
        
        ca1.markdown(f"<div class='badge-card'><div class='badge-icon'>{e_icon}</div><div class='badge-title'>{e_title}</div><p class='badge-desc'>หมวด {t_cat}\n{t_amt:,.0f} ฿</p></div>", unsafe_allow_html=True)
        # (ca2, ca3 คง logic เหรียญรายรับ/ออม ตาม v.32)
        st.plotly_chart(px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FF9AA2', '#B2E2F2']), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

# --- TAB 4: เป้าหมายการออม (NEW!) ---
with tab4:
    st.markdown("### 🎯 ตั้งเป้าหมายของทาสแมว")
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        new_g_name = st.text_input("ชื่อเป้าหมาย (เช่น ซื้อคอนโดแมว)", value=goal_data['goal_name'] if goal_data else "")
        new_g_amt = st.number_input("จำนวนเงินที่ต้องใช้ (฿)", value=float(goal_data['goal_amount'] if goal_data else 0.0))
        if st.button("🚩 บันทึกเป้าหมาย", use_container_width=True):
            c.execute("INSERT OR REPLACE INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, new_g_name, new_g_amt))
            conn.commit(); st.success("ตั้งเป้าหมายสำเร็จ!"); st.rerun()
    
    with col_g2:
        if goal_data and goal_data['goal_amount'] > 0:
            progress = min(total_save / goal_data['goal_amount'], 1.0)
            st.markdown(f"#### กำลังเก็บเงินเพื่อ: **{goal_data['goal_name']}**")
            st.metric("เงินออมที่มีตอนนี้", f"{total_save:,.2f} ฿")
            st.write(f"เป้าหมายคือ {goal_data['goal_amount']:,.2f} ฿")
            st.progress(progress)
            st.write(f"สำเร็จแล้ว {progress*100:.1f}%")
            if total_save < goal_data['goal_amount']:
                st.warning(f"ขาดอีกแค่ {goal_data['goal_amount'] - total_save:,.2f} ฿ เท่านั้น สู้ๆ เมี๊ยว!")
            else:
                st.balloons(); st.success("🎉 ยินดีด้วย! คุณเก็บเงินถึงเป้าหมายแล้ว!")

# --- TAB 5: ประวัติ (เพิ่มการดูใบเสร็จ) ---
with tab5:
    st.markdown("### 📖 ประวัติและใบเสร็จ")
    if not df.empty:
        df_display = df.sort_values(by='id', ascending=False)
        st.dataframe(df_display.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        sel_id = st.selectbox("เลือก ID รายการเพื่อดูใบเสร็จหรือจัดการ:", df_display['id'].tolist())
        if sel_id:
            row = df[df['id'] == sel_id].iloc[0]
            if row['receipt_img']:
                st.image(row['receipt_img'], caption=f"ใบเสร็จรายการที่ {sel_id}", width=300)
            else: st.write("ไม่มีรูปใบเสร็จแนบไว้เมี๊ยว")
            
            # ฟังก์ชันแก้ไข/ลบเดิม
            ce1, ce2 = st.columns(2)
            if ce1.button("🗑️ ลบรายการนี้", use_container_width=True):
                c.execute("DELETE FROM records WHERE id=?", (sel_id,))
                conn.commit(); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
