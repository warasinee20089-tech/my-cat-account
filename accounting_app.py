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
    # === หน้าหลัก
