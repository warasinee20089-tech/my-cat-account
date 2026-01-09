import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ฟังก์ชันพิเศษ แก้ปัญหา Error เวลาบันทึก (ใช้ได้ทุกเวอร์ชัน) ---
def safe_rerun():
    try:
        if hasattr(st, 'rerun'):
            st.rerun()
        elif hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
        else:
            st.write("✅ บันทึกแล้ว! (กดปุ่ม R ที่คีย์บอร์ดเพื่อรีเฟรชถ้าหน้าจอไม่เปลี่ยน)")
    except:
        st.write("✅ บันทึกเรียบร้อย")

# --- 2. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐾", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .stButton>button { background-color: #DB7093; color: white; border-radius: 10px; border: none; }
    .stButton>button:hover { background-color: #C71585; color: white; }
    h1, h2, h3, h4 { color: #4B0082; font-family: 'Sarabun', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 3. ฐานข้อมูล (เปลี่ยนชื่อไฟล์ใหม่ v2 เพื่อหนีปัญหาเก่า) ---
def init_db():
    # เปลี่ยนชื่อไฟล์เป็น meow_wallet_v2.db เพื่อเริ่มสมุดใหม่ที่ช่องครบ
    conn = sqlite3.connect('meow_wallet_v2.db', check_same_thread=False)
    c = conn.cursor()
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

conn = init_db()

# --- ฟังก์ชันดึงหมวดหมู่ทั้งหมด (แบบไม่ Error) ---
def get_all_categories():
    default_cats = ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "เงินออม 🐷"]
    try:
        # เช็คก่อนว่ามีข้อมูลไหม
        df = pd.read_sql("SELECT * FROM transactions LIMIT 1", conn)
        # ถ้ามี ดึงหมวดหมู่มา
        df_cats = pd.read_sql("SELECT DISTINCT category FROM transactions", conn)
        db_cats = df_cats['category'].dropna().unique().tolist()
        all_cats = list(set(default_cats + db_cats))
        all_cats.sort()
        return all_cats
    except:
        return default_cats

# --- 4. ระบบล็อกอิน ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

def login():
    st.session_state.logged_in = True
    st.session_state.username = st.session_state.login_name_input

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- 5. หน้าจอแสดงผล ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 50px;'>🐱</div>", unsafe_allow_html=True)
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อตรงนี้เลย...")
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    st.markdown(f"<div style='text-align: right; color: #DB7093;'>👤 สวัสดี: <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 แก้ไขข้อมูล"])

    # ---------------- TAB 1: บันทึก ----------------
    with tab1:
        st.header(f"✨ จดรายการใหม่")
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            date_val = col1.date_input("📅 วันที่", datetime.now())
            
            existing_cats = get_all_categories()
            cat_options = existing_cats + ["➕ พิมพ์หมวดใหม่..."]
            cat_choice = col2.selectbox("📂 หมวดหมู่", cat_options)
            
            if cat_choice == "➕ พิมพ์หมวดใหม่...":
                custom_cat = col2.text_input("✍️ พิมพ์ชื่อหมวดที่ต้องการ", placeholder="เช่น ค่าวัคซีน, ใส่ซอง")
                category = custom_cat if custom_cat else "อื่นๆ"
            else:
                category = cat_choice
            
            col3, col4 = st.columns(2)
            source = col3.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
            description = col4.text_input("📝 รายละเอียด", placeholder="เช่น ข้าวมันไก่")

            col5, col6 = st.columns(2)
            trans_type = col5.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
            amount = col6.number_input("💵 จำนวนเงิน", min_value=0.0, format="%.2f")

            if st.form_submit_button("💖 บันทึกรายการ", use_container_width=True):
                c = conn.cursor()
                c.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                          (date_val, category, source, description, trans_type, amount))
                conn.commit()
                st.success(f"บันทึกหมวด '{category}' แล้ว!")

    # ---------------- TAB 2: กระเป๋า (แก้บั๊ก Source แล้ว) ----------------
    with tab2:
        st.header("🏛️ ยอดคงเหลือ")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        # ป้องกัน Error ถ้าข้อมูลยังไม่มา
        if df.empty or 'source' not in df.columns:
            st.info("เริ่มบันทึกรายการแรกกันเลย! (ตอนนี้กระเป๋ายังว่างอยู่)")
        else:
            def get_balance(source_name):
                d = df[df['source'] == source_name]
                inc = d[d['type'] == 'รายรับ 💰']['amount'].sum()
                exp = d[d['type'] == 'รายจ่าย 💸']['amount'].sum()
                sav = d[d['type'] == 'เงินออม 🐷']['amount'].sum()
                return inc - exp - sav 

            c1, c2, c3 = st.columns(3)
            c1.metric("เงินสด 💵", f"{get_balance('เงินสด 💵'):,.2f} ฿")
            c2.metric("ธนาคาร 🏦", f"{get_balance('เงินฝากธนาคาร 🏦'):,.2f} ฿")
            c3.metric("บัตรเครดิต 💳", f"{get_balance('บัตรเครดิต 💳'):,.2f} ฿")

    # ---------------- TAB 3: วิเคราะห์ ----------------
    with tab3:
        st.header("📊 วิเคราะห์รายจ่าย")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        if not df.empty and 'type' in df.columns:
            expense_df = df[df['type'] == "รายจ่าย 💸"]
            if not expense_df.empty:
                fig = px.pie(expense_df, values='amount', names='category', title='สัดส่วนค่าใช้จ่ายจริง', hole=0.4)
                st.plotly_chart(fig)
            else:
                st.info("ยังไม่มีข้อมูลรายจ่าย")
        else:
            st.info("ยังไม่มีข้อมูล")

    # ---------------- TAB 4: การออม ----------------
    with tab4:
        st.header("🎯 เงินออม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        if not df.empty and 'type' in df.columns:
            savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
            st.metric("ยอดเงินออมสะสม",
