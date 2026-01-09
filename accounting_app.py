import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Meow Wallet", layout="wide", page_icon="🐾")

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฐานข้อมูล ---
def get_db():
    conn = sqlite3.connect('meow_wallet_v19.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. ระบบ Session ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", key="login_name")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. ดึงข้อมูล ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

# --- 5. Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
    with col2:
        cat_map = {
            "รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"],
            "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"],
            "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]
        }
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        final_cat = st.text_input("✍️ ระบุหมวดหมู่เอง") if selected_cat == "อื่นๆ ➕" else selected_cat
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0 and final_cat:
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_cat, sub_cat, inc, exp, sav))
            conn.commit()
            st.success("บันทึกสำเร็จ!")
            st.rerun()

with tab5:
    st.markdown("### 📖 ประวัติและจัดการรายการ")
    if not df.empty:
        df_display = df.sort_values(by='id', ascending=False)
        st.dataframe(df_display.drop(columns=['user_id']), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🛠️ แก้ไขหรือลบรายการ")
        selected_id = st.selectbox("เลือก ID รายการที่ต้องการจัดการ:", df_display['id'].tolist())
        
        if selected_id:
            row = df[df['id'] == selected_id].iloc[0]
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                new_date = st.date_input("แก้ไขวันที่", datetime.strptime(row['date'], '%Y-%m-%d'))
                new_amt = st.number_input("แก้ไขจำนวนเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
            with col_e2:
                new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
                
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("✅ ยืนยันการแก้ไข", use_container_width=True):
                # ตรวจสอบประเภทข้อมูลดั้งเดิมเพื่ออัปเดตค่าให้ถูกช่อง
                if row['income'] > 0:
                    new_vals = (new_amt, 0, 0)
                elif row['expense'] > 0:
                    new_vals = (0, new_amt, 0)
                else:
                    new_vals = (0, 0, new_amt)
                
                c.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                          (new_date.strftime('%Y-%m-%d'), new_vals[0], new_vals[1], new_vals[2], new_sub, selected_id))
                conn.commit()
                st.success("แก้ไขข้อมูลเรียบร้อย!")
                st.rerun()
                
            if c_btn2.button("🗑️ ลบรายการนี้", use_container_width=True):
                c.execute("DELETE FROM records WHERE id=?", (selected_id,))
                conn.commit()
                st.warning("ลบรายการแล้ว!")
                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลเมี๊ยวว")

# คำนวณยอดรวม
total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    c_w1, c_w2, c_w3 = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w in enumerate(wallets):
        w_df = df[df['wallet'] == w]
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        cols = [c_w1, c_w2, c_w3]
        cols[i].metric(w, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์")
    if not df.empty and (total_out > 0 or total_save > 0):
        fig = px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.4, color_discrete_sequence=['#FF5252', '#FF69B4'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("บันทึกรายจ่ายหรือเงินออมเพื่อดูแผนภูมิ")

with tab4:
    st.markdown("### 🎯 การออม")
    st.metric("เงินออมสะสม", f"{total_save:,.2f} ฿")
    if total_in > 0:
        progress_val = min(total_save/total_in, 1.0)
        st.progress(progress_val)
        st.write(f"{(total_save/total_in)*100:.1f}% ของรายรับ")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
