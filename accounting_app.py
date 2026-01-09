import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ตั้งค่าหน้าเว็บและ CSS ธีมสีชมพู ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐾", layout="wide")

# ใส่ CSS แต่งหน้าเว็บให้เป็นสีชมพู
st.markdown("""
<style>
    /* เปลี่ยนสีพื้นหลังทั้งหน้า */
    .stApp {
        background-color: #FFF0F5;
    }
    /* ปรับแต่งปุ่มกด */
    .stButton>button {
        background-color: #DB7093;
        color: white;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #C71585;
        color: white;
    }
    /* ปรับแต่งหัวข้อ */
    h1, h2, h3 {
        color: #4B0082;
        font-family: 'Sarabun', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ส่วนจัดการฐานข้อมูล (Database) ---
def init_db():
    # เชื่อมต่อฐานข้อมูล (แก้ปัญหา check_same_thread=False ให้แล้ว)
    conn = sqlite3.connect('meow_wallet_v19.db', check_same_thread=False)
    c = conn.cursor()
    # สร้างตารางถ้ายังไม่มี
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            source TEXT,
            description TEXT,
            type TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    return conn

# เรียกใช้ฟังก์ชันเชื่อมต่อฐานข้อมูล
conn = init_db()

# --- 3. ระบบล็อกอิน (จำลอง) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

def login():
    st.session_state.logged_in = True

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- 4. หน้าจอแสดงผล ---

if not st.session_state.logged_in:
    # === หน้า Login ===
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 50px;'>🐱</div>", unsafe_allow_html=True)
        st.text_input("ชื่อทาสแมว:", key="user_input")
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    # === หน้าหลักหลัง Login ===
    
    # สร้าง Tabs เมนู
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

    # ---------------- TAB 1: บันทึกรายการ ----------------
    with tab1:
        st.header("✨ เพิ่มรายการใหม่")
        
        with st.form("transaction_form", clear_on_submit=True):
            col_date, col_cat = st.columns(2)
            with col_date:
                date_val = st.date_input("📅 วันที่", datetime.now())
            with col_cat:
                category = st.selectbox("📂 หมวดหมู่", ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "อื่นๆ"])
            
            col_source, col_desc = st.columns(2)
            with col_source:
                source = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
            with col_desc:
                description = st.text_input("📝 รายละเอียด", placeholder="เช่น ข้าวมันไก่")

            col_type, col_amount = st.columns(2)
            with col_type:
                trans_type = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
            with col_amount:
                amount = st.number_input("💵 จำนวนเงิน", min_value=0.0, format="%.2f")

            submitted = st.form_submit_button("💖 บันทึกรายการ", use_container_width=True)
            
            if submitted:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                               (date_val, category, source, description, trans_type, amount))
                conn.commit()
                st.success("บันทึกข้อมูลสำเร็จแล้ว เมี๊ยว! 🐱")

    # ---------------- TAB 2: กระเป๋า (สรุปยอด) ----------------
    with tab2:
        st.header("🏛️ ยอดคงเหลือ")
        
        # ดึงข้อมูลมาคำนวณ
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        # คำนวณแยกตามช่องทาง (ตัวอย่างเบื้องต้น)
        # หมายเหตุ: ในโค้ดจริงต้องคำนวณ รายรับ - รายจ่าย ของแต่ละช่องทาง
        # อันนี้ทำแบบง่ายให้เห็นภาพรวม
        cash = df[df['source'] == "เงินสด 💵"]
        cash_total = cash[cash['type'] == 'รายรับ 💰']['amount'].sum() - cash[cash['type'] == 'รายจ่าย 💸']['amount'].sum()

        bank = df[df['source'] == "เงินฝากธนาคาร 🏦"]
        bank_total = bank[bank['type'] == 'รายรับ 💰']['amount'].sum() - bank[bank['type'] == 'รายจ่าย 💸']['amount'].sum()

        credit = df[df['source'] == "บัตรเครดิต 💳"]
        credit_total = credit[credit['type'] == 'รายรับ 💰']['amount'].sum() - credit[credit['type'] == 'รายจ่าย 💸']['amount'].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("เงินสด 💵", f"{cash_total:,.2f} ฿")
        c2.metric("เงินฝากธนาคาร 🏦", f"{bank_total:,.2f} ฿")
        c3.metric("บัตรเครดิต 💳", f"{credit_total:,.2f} ฿")

    # ---------------- TAB 3: วิเคราะห์ ----------------
    with tab3:
        st.header("📊 วิเคราะห์")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        if not df.empty:
            # กราฟวงกลมแยก รายรับ/รายจ่าย/เงินออม
            fig = px.pie(df, values='amount', names='type', title='สัดส่วนการใช้เงิน', color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig)
        else:
            st.info("ยังไม่มีข้อมูลให้วิเคราะห์")

    # ---------------- TAB 4: การออม ----------------
    with tab4:
        st.header("🎯 การออม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        if not df.empty:
            savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
            income = df[df['type'] == "รายรับ 💰"]['amount'].sum()
            
            st.metric("เงินออมสะสม", f"{savings:,.2f} ฿")
            
            if income > 0:
                percent = (savings / income) * 100
                st.progress(min(percent / 100, 1.0))
                st.caption(f"ออมไปแล้ว {percent:.1f}% ของรายรับ")
        else:
            st.metric("เงินออมสะสม", "0.00 ฿")

    # ---------------- TAB 5: ประวัติ ----------------
    with tab5:
        st.header("📖 ประวัติและแก้ไข")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)
        
        # ปุ่มลบข้อมูลล่าสุด (ตัวอย่าง)
        if st.button("ลบรายการล่าสุด"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = (SELECT MAX(id) FROM transactions)")
            conn.commit()
            st.experimental_rerun()

    # ปุ่มออกจากระบบด้านล่าง
    st.markdown("---")
    if st.button("🚪 ออกจากระบบ"):
        logout()
        st.experimental_rerun()
