import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐾", layout="wide")

# --- 2. ฟังก์ชันแก้ปัญหา Rerun ---
def safe_rerun():
    try:
        if hasattr(st, 'rerun'): st.rerun()
        elif hasattr(st, 'experimental_rerun'): st.experimental_rerun()
    except: pass

# --- 3. CSS (ธีมสีชมพู) ---
st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .stButton>button { 
        background-color: #DB7093; 
        color: white; 
        border-radius: 8px; 
        height: 45px;
        font-weight: bold;
        border: none;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #C71585; }
    h1, h2, h3 { color: #800080; font-family: 'Sarabun', sans-serif; }
    
    /* ปรับช่องกรอกข้อมูล */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #F0F2F6;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. ฐานข้อมูล (V14) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v14.db', check_same_thread=False)
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
def get_all_categories():
    default_cats = ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "ของใช้ 🧻", "ค่าน้ำ/ไฟ 💡", "เงินเดือน 💰", "เงินออม 🐷"]
    try:
        df = pd.read_sql("SELECT DISTINCT category FROM transactions", conn)
        if not df.empty:
            db_cats = df['category'].dropna().unique().tolist()
            all_cats = list(set(default_cats + db_cats))
            all_cats.sort()
            return all_cats
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
    # === หน้า Login (แบบเดิมที่คุณชอบ) ===
    st.write("")
    st.write("")
    st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 80px;'>🐱</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อตรงนี้เลย...")
        st.write("")
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    # === หน้าหลัก ===
    st.markdown(f"<div style='text-align: right; color: #DB7093;'>👤 สวัสดี: <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 บันทึก", "💰 กระเป๋าเงิน", "📊 กราฟ", "⚙️ แก้ไข"])

    # === TAB 1: บันทึก (เพิ่มปุ่มเลือกพิมพ์เองให้ชัดๆ) ===
    with tab1:
        st.header("✨ เพิ่มรายการใหม่")
        
        with st.form("entry_form", clear_on_submit=True):
            # แถว 1: วันที่ | หมวดหมู่
            c1, c2 = st.columns(2)
            with c1:
                date_val = st.date_input("📅 วันที่", datetime.now())
            with c2:
                # ปุ่มเลือกวิธีระบุหมวด (อยู่เหนือช่องเลือกเลย)
                cat_mode = st.radio("รูปแบบหมวดหมู่:", ["เลือกจากรายการ", "✏️ พิมพ์เอง"], horizontal=True)
                
                if cat_mode == "เลือกจากรายการ":
                    all_cats = get_all_categories()
                    category = st.selectbox("📂 เลือกหมวด:", all_cats)
                else:
                    # ช่องพิมพ์เอง (โผล่มาเมื่อกดเลือกพิมพ์เอง)
                    category = st.text_input("✍️ พิมพ์ชื่อหมวดใหม่:", placeholder="เช่น ค่าวัคซีน, ค่ากาแฟ")
                    if category == "": category = "อื่นๆ" # กันเหนียว

            # แถว 2: ช่องทาง | รายละเอียด
            c3, c4 = st.columns(2)
            with c3:
                source = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳", "TrueWallet"])
            with c4:
                description = st.text_input("📝 รายละเอียด", placeholder="เช่น ข้าวมันไก่")

            # แถว 3: ประเภท | จำนวนเงิน
            c5, c6 = st.columns(2)
            with c5:
                trans_type = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
            with c6:
                amount = st.number_input("💵 จำนวนเงิน", min_value=0.0, format="%.2f")

            st.write("")
            
            # ปุ่มบันทึก
            submitted = st.form_submit_button("💖 บันทึกรายการ", use_container_width=True)

            if submitted:
                c = conn.cursor()
                c.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                          (date_val, category, source, description, trans_type, amount))
                conn.commit()
                st.success(f"บันทึกหมวด '{category}' เรียบร้อยแล้ว!")

    # === TAB 2: กระเป๋าเงิน ===
    with tab2:
        st.header("🏛️ ยอดคงเหลือ")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        def get_bal(src):
            if df.empty: return 0.0
            d = df[df['source'] == src]
            return d[d['type']=='รายรับ 💰']['amount'].sum() - d[d['type']=='รายจ่าย 💸']['amount'].sum() - d[d['type']=='เงินออม 🐷']['amount'].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("💵 เงินสด", f"{get_bal('เงินสด 💵'):,.2f} ฿")
        c2.metric("🏦 ธนาคาร", f"{get_bal('เงินฝากธนาคาร 🏦'):,.2f} ฿")
        c3.metric("💳 บัตรเครดิต", f"{get_bal('บัตรเครดิต 💳'):,.2f} ฿")

    # === TAB 3: กราฟ ===
    with tab3:
        st.header("📊 สรุปผล")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            exp = df[df['type'] == "รายจ่าย 💸"]
            if not exp.empty:
                fig = px.pie(exp, values='amount', names='category', hole=0.5, title="สัดส่วนรายจ่าย")
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("ยังไม่มีรายจ่าย")
        else: st.info("ไม่มีข้อมูล")

    # === TAB 4: แก้ไข ===
    with tab4:
        st.header("⚙️ จัดการข้อมูล")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        if not df.empty:
            df['ลบ'] = False
            edited_df = st.data_editor(df, column_config={"ลบ": st.column_config.CheckboxColumn(width="small")}, disabled=["id"], hide_index=True, use_container_width=True)
            
            col_del, col_save = st.columns(2)
            if col_del.button("🗑️ ลบที่เลือก"):
                ids = edited_df[edited_df['ลบ']]['id'].tolist()
                for i in ids: conn.cursor().execute("DELETE FROM transactions WHERE id=?", (i,))
                conn.commit()
                safe_rerun()
            
            if col_save.button("💾 บันทึกการแก้ไข"):
                save_df = edited_df.drop(columns=['ลบ'])
                conn.cursor().execute("DELETE FROM transactions")
                save_df.to_sql('transactions', conn, if_exists='append', index=False)
                conn.commit()
                safe_rerun()
        else: st.info("ไม่มีข้อมูล")

    # ปุ่มออกจากระบบ
    st.markdown("---")
    if st.button("🚪 ออกจากระบบ"):
        logout()
        safe_rerun()
