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
    h1, h2, h3, h4 { color: #4B0082; font-family: 'Sarabun', sans-serif; }
    .big-font { font-size:20px !important; color: #C71585; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. ส่วนจัดการฐานข้อมูล ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v21.db', check_same_thread=False)
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
if 'username' not in st.session_state:
    st.session_state.username = ""

def login():
    st.session_state.logged_in = True
    st.session_state.username = st.session_state.login_name_input

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
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อตรงนี้เลย...")
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    # === หน้าหลักหลัง Login ===
    st.markdown(f"<div style='text-align: right; color: #DB7093;'>👤 สวัสดี: <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

    # ---------------- TAB 1: บันทึก (แก้ให้พิมพ์หมวดหมู่เองได้) ----------------
    with tab1:
        st.header(f"✨ จดรายการกันเถอะ {st.session_state.username}")
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            date_val = col1.date_input("📅 วันที่", datetime.now())
            
            # --- ส่วนแก้หมวดหมู่ ---
            # ให้เลือกก่อน หรือเลือก "ระบุเอง"
            cat_choice = col2.selectbox(
                "📂 หมวดหมู่", 
                ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "เงินออม 🐷", "➕ ระบุเอง (พิมพ์ใหม่)..."]
            )
            
            # ถ้าเลือก "ระบุเอง" ให้โชว์ช่องพิมพ์
            if cat_choice == "➕ ระบุเอง (พิมพ์ใหม่)...":
                custom_cat = col2.text_input("✍️ พิมพ์ชื่อหมวดหมู่ที่ต้องการ", placeholder="เช่น ค่าวัคซีนแมว, ค่ากาแฟ")
                # ถ้าลืมพิมพ์ จะให้เป็นค่าว่าง หรือ 'อื่นๆ'
                category = custom_cat if custom_cat else "อื่นๆ"
            else:
                category = cat_choice
            # -----------------------
            
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
                st.success(f"บันทึกหมวด '{category}' สำเร็จแล้ว เมี๊ยว! 🐱")

    # ---------------- TAB 2: กระเป๋า ----------------
    with tab2:
        st.header("🏛️ ยอดคงเหลือ")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
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
        expense_df = df[df['type'] == "รายจ่าย 💸"]
        
        if not expense_df.empty:
            # กราฟจะโชว์หมวดหมู่ที่คุณพิมพ์เองด้วยอัตโนมัติ
            fig = px.pie(expense_df, values='amount', names='category', title='หมดเงินไปกับอะไรบ้าง?', hole=0.4)
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)
        else:
            st.info("ยังไม่มีรายจ่าย")

    # ---------------- TAB 4: การออม ----------------
    with tab4:
        st.header("🎯 กระปุกหมูออมสิน")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
        
        col_pig1, col_pig2 = st.columns([1, 3])
        with col_pig1:
            st.markdown("<div style='font-size: 80px;'>🐷</div>", unsafe_allow_html=True)
        with col_pig2:
            st.metric("เงินออมสะสมทั้งหมด", f"{savings:,.2f} ฿")
            st.progress(min(savings/10000, 1.0))

    # ---------------- TAB 5: ประวัติ (เอาคำว่าลบง่ายๆ ออก) ----------------
    with tab5:
        st.header("📖 จัดการรายการ") # แก้ชื่อหัวข้อแล้ว
        
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        
        if not df.empty:
            df['ลบ?'] = False
            st.info("💡 วิธีลบ: ติ๊กถูก ✅ ในช่อง 'ลบ?' ท้ายรายการ แล้วกดปุ่มสีแดง")
            
            edited_df = st.data_editor(
                df, 
                column_config={
                    "ลบ?": st.column_config.CheckboxColumn("ติ๊กเพื่อลบ", default=False)
                },
                disabled=["id"],
                hide_index=True,
                use_container_width=True,
                key="editor"
            )

            if st.button("🗑️ ลบรายการที่เลือก", type="primary"):
                to_delete = edited_df[edited_df['ลบ?'] == True]['id'].tolist()
                if to_delete:
                    cursor = conn.cursor()
                    for item_id in to_delete:
                        cursor.execute("DELETE FROM transactions WHERE id=?", (item_id,))
                    conn.commit()
                    st.success(f"ลบไป {len(to_delete)} รายการเรียบร้อย!")
                    st.rerun()
                else:
                    st.warning("ยังไม่ได้ติ๊กเลือกรายการไหนเลยนะ")
            
            if st.button("💾 บันทึกการแก้ไขข้อมูล"):
                save_df = edited_df.drop(columns=['ลบ?'])
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions") 
                save_df.to_sql('transactions', conn, if_exists='append', index=False)
                conn.commit()
                st.success("บันทึกข้อมูลที่แก้ไขแล้ว!")
                st.rerun()
        else:
            st.info("ยังไม่มีรายการจ้า")

    st.markdown("---")
    if st.button("🚪 ออกจากระบบ"):
        logout()
        st.rerun()
