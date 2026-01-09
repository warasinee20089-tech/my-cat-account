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
        if hasattr(st, 'rerun'):
            st.rerun()
        elif hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
    except:
        pass

# --- 3. CSS (ธีมสีชมพูเดิมที่คุ้นเคย) ---
st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .stButton>button { 
        background-color: #DB7093; 
        color: white; 
        border-radius: 10px; 
        border: none;
        height: 45px;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #C71585; color: white; }
    
    /* ปรับแต่งการ์ดแสดงตัวเลขข้างในให้ดูดี */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    
    h1, h2, h3 { color: #4B0082; font-family: 'Sarabun', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 4. ฐานข้อมูล (V7 เพื่อความสะอาดใหม่หมดจด) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v7.db', check_same_thread=False)
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
    default_cats = ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "เงินออม 🐷"]
    try:
        df = pd.read_sql("SELECT DISTINCT category FROM transactions", conn)
        if not df.empty:
            db_cats = df['category'].dropna().unique().tolist()
            all_cats = list(set(default_cats + db_cats))
            all_cats.sort()
            return all_cats
    except:
        pass
    return default_cats

# --- 5. ระบบล็อกอิน ---
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

# --- 6. ส่วนแสดงผล ---
if not st.session_state.logged_in:
    # === หน้า Login แบบเดิม (Original Style) ===
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # กลับมาใช้ Layout เดิมที่เรียบง่าย
        st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 60px;'>🐱</div>", unsafe_allow_html=True)
        st.write("")
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อตรงนี้เลย...")
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    # === หน้าหลัก (จัดเรียงใหม่ให้น่าใช้) ===
    
    # Sidebar เมนูด้านซ้าย
    with st.sidebar:
        st.title("🐱 เมนูหลัก")
        st.write(f"ผู้ใช้งาน: **{st.session_state.username}**")
        st.markdown("---")
        if st.button("🚪 ออกจากระบบ"):
            logout()
            safe_rerun()

    # หัวข้อหลักขวาบน
    st.markdown(f"<div style='text-align: right; color: #DB7093;'>ยินดีต้อนรับกลับมานะ เมี๊ยว! 🐱</div>", unsafe_allow_html=True)
    
    # Tabs เมนูหลัก
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 จดบันทึก", "💰 กระเป๋าตังค์", "📊 กราฟสรุป", "🐷 กระปุกหมู", "⚙️ แก้ไขประวัติ"])

    # === TAB 1: จดบันทึก (จัดเรียงสวยงาม + หมวดหมู่เสถียร) ===
    with tab1:
        st.markdown("### ✨ เพิ่มรายการใหม่")
        
        # ใช้ container ครอบเพื่อให้ดูเป็นสัดส่วน
        with st.container():
            with st.form("transaction_form", clear_on_submit=True):
                
                # แถว 1: วันที่ | ประเภท | จำนวนเงิน
                c1, c2, c3 = st.columns(3)
                date_val = c1.date_input("📅 วันที่", datetime.now())
                trans_type = c2.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
                amount = c3.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, format="%.2f")

                st.markdown("---")

                # แถว 2: หมวดหมู่ (แยกส่วนชัดเจน ไม่ error)
                st.info("📂 **หมวดหมู่**")
                mc1, mc2 = st.columns([1, 2])
                with mc1:
                    # ปุ่มเลือกวิธีระบุหมวด
                    cat_mode = st.radio("วิธีเลือก:", ["ใช้หมวดเดิมที่มี", "➕ พิมพ์ใหม่เอง"], horizontal=False)
                with mc2:
                    if cat_mode == "ใช้หมวดเดิมที่มี":
                        all_cats = get_categories()
                        category = st.selectbox("เลือกรายการ:", all_cats)
                    else:
                        category = st.text_input("พิมพ์ชื่อหมวดใหม่:", placeholder="เช่น ค่าวัคซีน, ค่าขนมแมวเลีย")
                        if category == "": category = "อื่นๆ" # กันเหนียว

                st.markdown("---")

                # แถว 3: ช่องทาง | รายละเอียด
                rc1, rc2 = st.columns([1, 2])
                source = rc1.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
                description = rc2.text_input("📝 รายละเอียดเพิ่มเติม", placeholder="เช่น ข้าวมันไก่")

                st.write("")
                # ปุ่มบันทึกใหญ่
                if st.form_submit_button("💖 บันทึกรายการ", use_container_width=True):
                    c = conn.cursor()
                    c.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                              (date_val, category, source, description, trans_type, amount))
                    conn.commit()
                    st.success(f"บันทึกหมวด '{category}' เรียบร้อยแล้ว!")

    # === TAB 2: กระเป๋าตังค์ (Dashboard) ===
    with tab2:
        st.markdown("### 🏛️ สรุปยอดเงินในกระเป๋า")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        # คำนวณยอดรวม
        if not df.empty:
            net = df[df['type']=='รายรับ 💰']['amount'].sum() - df[df['type']=='รายจ่าย 💸']['amount'].sum() - df[df['type']=='เงินออม 🐷']['amount'].sum()
        else:
            net = 0.0

        st.metric("💰 ยอดเงินสุทธิทั้งหมด", f"{net:,.2f} ฿")
        st.markdown("---")
        
        # แยกตามช่องทาง
        def get_bal(src):
            if df.empty: return 0.0
            d = df[df['source'] == src]
            return d[d['type']=='รายรับ 💰']['amount'].sum() - d[d['type']=='รายจ่าย 💸']['amount'].sum() - d[d['type']=='เงินออม 🐷']['amount'].sum()

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("💵 เงินสด", f"{get_bal('เงินสด 💵'):,.2f} ฿")
        col_b.metric("🏦 ธนาคาร", f"{get_bal('เงินฝากธนาคาร 🏦'):,.2f} ฿")
        col_c.metric("💳 บัตรเครดิต", f"{get_bal('บัตรเครดิต 💳'):,.2f} ฿")

    # === TAB 3: กราฟ ===
    with tab3:
        st.markdown("### 📊 วิเคราะห์การใช้จ่าย")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            exp_df = df[df['type'] == "รายจ่าย 💸"]
            if not exp_df.empty:
                fig = px.pie(exp_df, values='amount', names='category', title='สัดส่วนรายจ่าย', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ยังไม่มีรายจ่ายจ้า")
        else:
            st.info("ไม่มีข้อมูล")

    # === TAB 4: เงินออม ===
    with tab4:
        st.markdown("### 🐷 เงินออมสะสม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
            st.metric("ยอดเงินออม", f"{savings:,.2f} ฿")
            st.progress(min(savings/10000, 1.0))
        else:
            st.metric("ยอดเงินออม", "0.00 ฿")

    # === TAB 5: แก้ไข (ตาราง) ===
    with tab5:
        st.markdown("### ⚙️ แก้ไขรายการย้อนหลัง")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['ลบ'] = False
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "ลบ": st.column_config.CheckboxColumn("ลบ?", width="small"),
                    "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                    "category": st.column_config.TextColumn("หมวดหมู่"),
                    "amount": st.column_config.NumberColumn("จำนวนเงิน", format="%.2f"),
                },
                disabled=["id"],
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic"
            )

            c1, c2 = st.columns(2)
            if c1.button("🗑️ ลบรายการที่ติ๊ก", type="primary", use_container_width=True):
                ids = edited_df[edited_df['ลบ'] == True]['id'].tolist()
                if ids:
                    cur = conn.cursor()
                    for i in ids: cur.execute("DELETE FROM transactions WHERE id=?", (i,))
                    conn.commit()
                    safe_rerun()
            
            if c2.button("💾 บันทึกการแก้ไข", use_container_width=True):
                save_df = edited_df.drop(columns=['ลบ'])
                save_df['date'] = save_df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else x)
                cur = conn.cursor()
                cur.execute("DELETE FROM transactions")
                save_df.to_sql('transactions', conn, if_exists='append', index=False)
                conn.commit()
                st.success("บันทึกแล้ว!")
                safe_rerun()
        else:
            st.info("ยังไม่มีข้อมูล")
