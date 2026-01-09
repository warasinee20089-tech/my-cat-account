import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Meow Wallet", page_icon="🐾", layout="wide")

# --- 2. ฟังก์ชันแก้ปัญหา Rerun ---
def safe_rerun():
    try:
        if hasattr(st, 'rerun'): st.rerun()
        elif hasattr(st, 'experimental_rerun'): st.experimental_rerun()
    except:
        st.write("บันทึกแล้ว! (กดปุ่ม R เพื่อรีเฟรช)")

# --- 3. ตกแต่ง CSS (ธีมชมพู) ---
st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stButton>button { 
        background-color: #DB7093; 
        color: white; 
        border-radius: 10px; 
        height: 45px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #C71585; }
    h1, h2, h3 { color: #800080; }
</style>
""", unsafe_allow_html=True)

# --- 4. ฐานข้อมูล (V11) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v11.db', check_same_thread=False)
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

# --- ฟังก์ชันดึงหมวดหมู่ ---
def get_categories():
    default_cats = ["อาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ของใช้ 🧻", "เงินออม 🐷"]
    try:
        df = pd.read_sql("SELECT DISTINCT category FROM transactions", conn)
        if not df.empty:
            db_cats = df['category'].dropna().unique().tolist()
            return list(set(default_cats + db_cats))
    except: pass
    return default_cats

# --- 5. ระบบล็อกอิน ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""

def login():
    st.session_state.logged_in = True
    st.session_state.username = st.session_state.login_name_input

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- 6. ส่วนแสดงผล ---
if not st.session_state.logged_in:
    # หน้า Login
    st.write("")
    st.write("")
    st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 80px;'>🐱</div>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อ...")
        st.button("🚀 เข้าสู่ระบบ", on_click=login, use_container_width=True)

else:
    # หน้าหลัก
    with st.sidebar:
        st.header("เมนูหลัก")
        st.write(f"ผู้ใช้: **{st.session_state.username}**")
        if st.button("🚪 ออกจากระบบ"):
            logout()
            safe_rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 จดบันทึก", "💰 กระเป๋าเงิน", "📊 กราฟ", "⚙️ แก้ไข"])

    # === TAB 1: จดบันทึก ===
    with tab1:
        st.markdown("<div class='css-card'>", unsafe_allow_html=True)
        with st.form("add_form", clear_on_submit=True):
            st.markdown("### ✨ เพิ่มรายการ")
            
            # ใช้ st.columns(2) แทนแบบ list เพื่อป้องกัน error
            c1, c2 = st.columns(2)
            date_val = c1.date_input("วันที่", datetime.now())
            trans_type = c2.radio("ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)

            st.markdown("---")
            
            # ส่วนหมวดหมู่
            c_cat1, c_cat2 = st.columns([1, 2])
            with c_cat1:
                cat_mode = st.radio("หมวดหมู่", ["เลือกเดิม", "พิมพ์ใหม่"])
            with c_cat2:
                if cat_mode == "เลือกเดิม":
                    category = st.selectbox("เลือกรายการ:", get_categories())
                else:
                    category = st.text_input("ระบุชื่อหมวด:", placeholder="เช่น ค่ากาแฟ")
                    if not category: category = "อื่นๆ"

            st.markdown("---")

            # ส่วนจำนวนเงินและช่องทาง
            c3, c4 = st.columns(2)
            amount = c3.number_input("จำนวนเงิน (บาท)", min_value=0.0, format="%.2f")
            source = c4.selectbox("ช่องทาง", ["เงินสด", "ธนาคาร", "บัตรเครดิต", "อื่นๆ"])
            description = st.text_input("หมายเหตุ/รายละเอียด")

            st.write("")
            if st.form_submit_button("✅ บันทึกรายการ", use_container_width=True):
                c = conn.cursor()
                c.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                          (date_val, category, source, description, trans_type, amount))
                conn.commit()
                st.success(f"บันทึก {amount} บาท เรียบร้อย!")
        st.markdown("</div>", unsafe_allow_html=True)

    # === TAB 2: กระเป๋าเงิน ===
    with tab2:
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        total = 0
        if not df.empty:
            total = df[df['type']=='รายรับ 💰']['amount'].sum() - df[df['type']=='รายจ่าย 💸']['amount'].sum() - df[df['type']=='เงินออม 🐷']['amount'].sum()

        st.markdown(f"""
        <div class='css-card' style='text-align: center;'>
            <h2 style='color: gray;'>ยอดคงเหลือ</h2>
            <h1 style='color: #C71585; font-size: 50px;'>{total:,.2f} ฿</h1>
        </div>
        """, unsafe_allow_html=True)

    # === TAB 3: กราฟ ===
    with tab3:
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            exp_df = df[df['type'] == "รายจ่าย 💸"]
            if not exp_df.empty:
                fig = px.pie(exp_df, values='amount', names='category', hole=0.5)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ยังไม่มีรายจ่าย")
        else:
            st.info("ไม่มีข้อมูล")

    # === TAB 4: แก้ไข ===
    with tab4:
        st.markdown("### ⚙️ จัดการข้อมูล")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        if not df.empty:
            df['ลบ'] = False
            edited_df = st.data_editor(df, column_config={
                "ลบ": st.column_config.CheckboxColumn("ลบ", width="small"),
                "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
            }, disabled=["id"], hide_index=True, use_container_width=True)

            if st.button("🗑️ ลบรายการที่ติ๊ก"):
                ids = edited_df[edited_df['ลบ']]['id'].tolist()
                if ids:
                    for i in ids: conn.cursor().execute("DELETE FROM transactions WHERE id=?", (i,))
                    conn.commit()
                    safe_rerun()
            
            if st.button("💾 บันทึกการแก้ไข"):
                save_df = edited_df.drop(columns=['ลบ'])
                conn.cursor().execute("DELETE FROM transactions")
                save_df.to_sql('transactions', conn, if_exists='append', index=False)
                conn.commit()
                safe_rerun()
        else:
            st.info("ยังไม่มีข้อมูล")
