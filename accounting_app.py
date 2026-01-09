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

# --- 3. CSS แต่งหน้าเว็บ (Modern Cute Style) ---
st.markdown("""
<style>
    /* พื้นหลังสีชมพูพาสเทล */
    .stApp { background-color: #FFF0F5; }
    
    /* กล่อง Card สีขาวโค้งมน */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* ปุ่มกด */
    .stButton>button { 
        background-color: #FF69B4; 
        color: white; 
        border-radius: 15px; 
        border: none;
        height: 50px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #DB7093; transform: scale(1.02); }
    
    /* กล่องตัวเลข (Metric) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* ซ่อน Header รกๆ */
    header {visibility: hidden;}
    
    h1, h2, h3 { color: #8B008B; font-family: 'Sarabun', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 4. ฐานข้อมูล (V8 Clean Start) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v8.db', check_same_thread=False)
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
    # === หน้า Login (Minimal Clean) ===
    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin-top: 50px;'>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/616/616430.png", width=100)
        st.markdown("<h1>Meow Wallet</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.text_input("ชื่อของคุณ", key="login_name_input", placeholder="พิมพ์ชื่อเล่น...")
        st.button("เข้าใช้งาน 🚀", on_click=login, use_container_width=True)

else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        if st.button("ออกจากระบบ"):
            logout()
            safe_rerun()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["✏️ จดบันทึก", "👛 กระเป๋าตังค์", "📊 สรุปผล", "⚙️ แก้ไข"])

    # === TAB 1: จดบันทึก (Compact Design) ===
    with tab1:
        st.markdown("<div class='css-card'>", unsafe_allow_html=True) # เริ่ม Card
        with st.form("add_form", clear_on_submit=True):
            st.markdown("### ✨ เพิ่มรายการ")
            
            # แถว 1: วันที่ | ประเภท
            c1, c2 = st.columns(2)
            date_val = c1.date_input("วันที่", datetime.now())
            trans_type = c2.radio("ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True, label_visibility="collapsed")

            # แถว 2: หมวดหมู่ (Clean Logic)
            st.markdown("---")
            c3, c4 = st.columns([1, 1])
            with c3:
                cat_mode = st.radio("หมวดหมู่", ["เลือกเดิม", "พิมพ์ใหม่"], horizontal=True, label_visibility="collapsed")
            with c4:
                if cat_mode == "เลือกเดิม":
                    category = st.selectbox("เลือกรายการ", get_categories(), label_visibility="collapsed")
                else:
                    category = st.text_input("พิมพ์ชื่อหมวด", placeholder="เช่น ค่ากาแฟ")
                    if not category: category = "อื่นๆ"

            # แถว 3: จำนวนเงิน | ช่องทาง | รายละเอียด
            st.markdown("---")
            c5, c6, c7 = st.columns([1, 1, 2])
            amount = c5.number_input("จำนวน (บาท)", min_value=0.0, format="%.2f")
            source = c6.selectbox("ช่องทาง", ["เงินสด", "K-Bank", "SCB", "TrueWallet", "บัตรเครดิต"])
            description = c7.text_input("โน้ตช่วยจำ", placeholder="รายละเอียดสั้นๆ")

            st.write("")
            if st.form_submit_button("บันทึก ✅", use_container_width=True):
                c = conn.cursor()
                c.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                          (date_val, category, source, description, trans_type, amount))
                conn.commit()
                st.toast(f"บันทึก {amount} บาท แล้ว!", icon="🎉")
        st.markdown("</div>", unsafe_allow_html=True) # จบ Card

    # === TAB 2: กระเป๋า (Dashboard Card) ===
    with tab2:
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        # ยอดรวม
        total = 0
        if not df.empty:
            total = df[df['type']=='รายรับ 💰']['amount'].sum() - df[df['type']=='รายจ่าย 💸']['amount'].sum() - df[df['type']=='เงินออม 🐷']['amount'].sum()

        st.markdown(f"""
        <div class='css-card' style='text-align: center;'>
            <h3 style='color: gray; margin: 0;'>ยอดเงินสุทธิ</h3>
            <h1 style='color: #FF1493; font-size: 50px; margin: 0;'>{total:,.2f} ฿</h1>
        </div>
        """, unsafe_allow_html=True)

        # แยกบัญชี
        st.markdown("##### แยกตามบัญชี")
        def get_bal(src):
            if df.empty: return 0.0
            d = df[df['source'] == src]
            return d[d['type']=='รายรับ 💰']['amount'].sum() - d[d['type']=='รายจ่าย 💸']['amount'].sum() - d[d['type']=='เงินออม 🐷']['amount'].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("เงินสด", f"{get_bal('เงินสด'):,.0f}")
        c2.metric("ธนาคาร (รวม)", f"{get_bal('K-Bank')+get_bal('SCB'):,.0f}")
        c3.metric("บัตรเครดิต", f"{get_bal('บัตรเครดิต'):,.0f}")

    # === TAB 3: สรุปผล (Clean Graph) ===
    with tab3:
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            # 1. เงินออม
            savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
            st.markdown(f"<div class='css-card'>🐷 เงินออมสะสม: <b>{savings:,.2f} บาท</b></div>", unsafe_allow_html=True)

            # 2. กราฟวงกลม
            exp_df = df[df['type'] == "รายจ่าย 💸"]
            if not exp_df.empty:
                st.markdown("##### 💸 หมดเงินไปกับอะไร?")
                fig = px.pie(exp_df, values='amount', names='category', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ยังไม่มีรายจ่าย")
        else:
            st.info("ยังไม่มีข้อมูล")

    # === TAB 4: แก้ไข (Table) ===
    with tab4:
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        if not df.empty:
            df['ลบ'] = False
            edited_df = st.data_editor(df, column_config={
                "ลบ": st.column_config.CheckboxColumn("ลบ", width="small"),
                "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                "amount": st.column_config.NumberColumn("บาท", format="%.2f")
            }, disabled=["id"], hide_index=True, use_container_width=True)

            c1, c2 = st.columns(2)
            if c1.button("ลบที่เลือก 🗑️"):
                ids = edited_df[edited_df['ลบ']]['id'].tolist()
                if ids:
                    for i in ids: conn.cursor().execute("DELETE FROM transactions WHERE id=?", (i,))
                    conn.commit()
                    safe_rerun()
            
            if c2.button("บันทึกแก้ไข 💾"):
                save_df = edited_df.drop(columns=['ลบ'])
                conn.cursor().execute("DELETE FROM transactions")
                save_df.to_sql('transactions', conn, if_exists='append', index=False)
                conn.commit()
                safe_rerun()
