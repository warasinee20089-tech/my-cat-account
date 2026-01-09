import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ตั้งค่าหน้าเว็บและ CSS ธีมสีชมพู ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐾", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .stButton>button { background-color: #DB7093; color: white; border-radius: 10px; border: none; }
    .stButton>button:hover { background-color: #C71585; color: white; }
    h1, h2, h3 { color: #4B0082; font-family: 'Sarabun', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 2. ส่วนจัดการฐานข้อมูล ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v19.db', check_same_thread=False)
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

# --- 3. ระบบล็อกอิน ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login(): st.session_state.logged_in = True
def logout(): st.session_state.logged_in = False

# --- 4. หน้าจอแสดงผล ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 50px;'>🐱</div>", unsafe_allow_html=True)
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

    # ---------------- TAB 1: บันทึก ----------------
    with tab1:
        st.header("✨ เพิ่มรายการใหม่")
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            date_val = col1.date_input("📅 วันที่", datetime.now())
            category = col2.selectbox("📂 หมวดหมู่", ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "อื่นๆ"])
            
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
                st.success("บันทึกสำเร็จ!")

    # ---------------- TAB 2: กระเป๋า ----------------
    with tab2:
        st.header("🏛️ ยอดคงเหลือ")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        def get_balance(source_name):
            d = df[df['source'] == source_name]
            return d[d['type'] == 'รายรับ 💰']['amount'].sum() - d[d['type'] == 'รายจ่าย 💸']['amount'].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("เงินสด 💵", f"{get_balance('เงินสด 💵'):,.2f} ฿")
        c2.metric("ธนาคาร 🏦", f"{get_balance('เงินฝากธนาคาร 🏦'):,.2f} ฿")
        c3.metric("บัตรเครดิต 💳", f"{get_balance('บัตรเครดิต 💳'):,.2f} ฿")

    # ---------------- TAB 3: วิเคราะห์ ----------------
    with tab3:
        st.header("📊 วิเคราะห์")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            fig = px.pie(df, values='amount', names='type', title='สัดส่วนการใช้เงิน')
            st.plotly_chart(fig)
        else:
            st.info("ยังไม่มีข้อมูล")

    # ---------------- TAB 4: การออม ----------------
    with tab4:
        st.header("🎯 การออม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
        st.metric("เงินออมสะสม", f"{savings:,.2f} ฿")

    # ---------------- TAB 5: ประวัติและแก้ไข (แก้ Error + เพิ่มฟีเจอร์) ----------------
    with tab5:
        st.header("📖 ประวัติรายการ")
        
        # โหลดข้อมูล
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        
        # ส่วนที่ 1: ตารางแก้ไขข้อมูล (Edit Table)
        st.info("💡 วิธีแก้: คลิกที่ช่องในตารางเพื่อแก้ตัวเลข แล้วกดปุ่ม 'บันทึกการแก้ไข' ด้านล่าง")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor")

        if st.button("💾 บันทึกการแก้ไข (Save Changes)"):
            try:
                # เทคนิค: ลบข้อมูลเก่าแล้วเขียนทับด้วยข้อมูลใหม่จากตาราง
                # หมายเหตุ: วิธีนี้ง่ายที่สุดสำหรับแอปขนาดเล็ก
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions") # ลบของเก่า
                edited_df.to_sql('transactions', conn, if_exists='append', index=False) # ใส่ของใหม่
                conn.commit()
                st.success("อัปเดตข้อมูลเรียบร้อยแล้ว!")
                st.rerun() # ใช้ st.rerun() แทน experimental_rerun
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

        st.divider()

        # ส่วนที่ 2: ลบรายการด้วย ID (เผื่อตารางมีปัญหา)
        st.subheader("🗑️ ลบรายการด้วย ID")
        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            id_to_delete = st.number_input("ใส่เลข ID ที่ต้องการลบ (ดูจากตาราง)", min_value=0, step=1)
        with col_del2:
            st.write("") # เว้นบรรทัด
            st.write("")
            if st.button("ยืนยันลบ ❌", type="primary"):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ?", (id_to_delete,))
                conn.commit()
                st.warning(f"ลบรายการ ID {id_to_delete} แล้ว")
                st.rerun()

    # ปุ่มออกจากระบบ
    st.markdown("---")
    if st.button("🚪 ออกจากระบบ"):
        logout()
        st.rerun()
