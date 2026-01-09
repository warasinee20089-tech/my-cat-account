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
    except: pass

# --- 3. CSS (ผสมผสาน: Login เดิม + ข้างในทันสมัย) ---
st.markdown("""
<style>
    /* พื้นหลังสีชมพูพาสเทล */
    .stApp { background-color: #FFF0F5; }
    
    /* กล่อง Card สีขาวโค้งมน (สำหรับข้างใน) */
    .css-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* ปุ่มกด */
    .stButton>button { 
        background-color: #DB7093; 
        color: white; 
        border-radius: 12px; 
        border: none;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #C71585; transform: scale(1.02); }
    
    /* กล่องตัวเลข */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    h1, h2, h3 { color: #800080; font-family: 'Sarabun', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 4. ฐานข้อมูล (V9 Final) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v9.db', check_same_thread=False)
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
    # === หน้า Login (แบบเดิมที่คุ้นเคย จัดเรียงใหม่ให้สวย) ===
    st.write("") 
    st.write("") 
    
    # โลโก้และชื่อแอปตรงกลาง
    st.markdown("<h1 style='text-align: center; font-size: 48px;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 80px;'>🐱</div>", unsafe_allow_html=True)
    
    st.write("")
    
    # ช่องกรอกชื่อ (จัดให้กึ่งกลาง ไม่กว้างเกินไป)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อตรงนี้เลย...")
        st.write("")
        st.button("🚀 เข้าสู่ระบบ", on_click=login, use_container_width=True)

else:
    # === หน้าหลัก (ข้างในทันสมัย Clean & Cute) ===
    
    # Sidebar
    with st.sidebar:
        st.title("เมนูหลัก")
        st.write(f"สวัสดีคุณ: **{st.session_state.username}**")
        if st.button("🚪 ออกจากระบบ"):
            logout()
            safe_rerun()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 จดบันทึก", "💰 กระเป๋าเงิน", "📊 กราฟสวยๆ", "⚙️ แก้ไขข้อมูล"])

    # === TAB 1: จดบันทึก (Design Card) ===
    with tab1:
        st.markdown("<div class='css-card'>", unsafe_allow_html=True) # เริ่ม Card ขาว
        with st.form("add_form", clear_on_submit=True):
            st.markdown("### ✨ เพิ่มรายการ")
            
            # แถว 1: วันที่ | ประเภท (Radio)
            c1, c2 = st.columns([1, 1
