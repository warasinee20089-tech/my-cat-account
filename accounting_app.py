import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐾", layout="wide")

# --- 2. ฟังก์ชันแก้ปัญหา Rerun (ใช้ได้ทุกเวอร์ชัน) ---
def safe_rerun():
    try:
        if hasattr(st, 'rerun'):
            st.rerun()
        elif hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
        else:
            st.warning("กดปุ่ม R เพื่อรีเฟรชหน้าจอ")
    except:
        pass

# --- 3. ตกแต่ง CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .stButton>button { background-color: #DB7093; color: white; border-radius: 10px; border: none; }
    .stButton>button:hover { background-color: #C71585; color: white; }
    h1, h2, h3, h4 { color: #4B0082; font-family: 'Sarabun', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 4. เชื่อมต่อฐานข้อมูล (V5 ล้างใหม่ แก้บั๊ก) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_v5.db', check_same_thread=False)
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

# --- ฟังก์ชันดึงหมวดหมู่ (ดึงจากที่เคยบันทึก + ค่าพื้นฐาน) ---
def get_categories():
    default_cats = ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "เงินออม 🐷"]
    try:
        df = pd.read_sql("SELECT DISTINCT category FROM transactions", conn)
        if not df.empty:
            db_cats = df['category'].dropna().unique().tolist()
            # เอาค่าใน DB มารวมกับค่าพื้นฐาน แล้วตัดตัวซ้ำ
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🐾 กระเป๋าเงินเหมียว 🐾</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 50px;'>🐱</div>", unsafe_allow_html=True)
        st.text_input("ชื่อทาสแมว:", key="login_name_input", placeholder="พิมพ์ชื่อตรงนี้เลย...")
        st.button("เข้าสู่ระบบ 🐾", on_click=login, use_container_width=True)

else:
    with st.sidebar:
        st.write(f"ผู้ใช้งาน: **{st.session_state.username}**")
        if st.button("🚪 ออกจากระบบ"):
            logout()
            safe_rerun()

    st.markdown(f"<div style='text-align: right; color: #DB7093;'>ยินดีต้อนรับกลับมา เมี๊ยว! 🐱</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

    # === TAB 1: บันทึก (แก้ระบบหมวดหมู่ให้เสถียร) ===
    with tab1:
        st.header(f"✨ เพิ่มรายการใหม่")
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            date_val = col1.date_input("📅 วันที่", datetime.now())
            
            # --- ส่วนเลือกหมวดหมู่แบบใหม่ (เสถียร) ---
            st.markdown("---")
            st.markdown("**:file_folder: หมวดหมู่**")
            
            # ให้เลือกเลยว่าจะเอาหมวดเดิม หรือ พิมพ์ใหม่ (แยกกันชัดเจน)
            cat_mode = st.radio("เลือกวิธีระบุหมวดหมู่:", ["เลือกจากรายการเดิม", "➕ พิมพ์เพิ่มใหม่เอง"], horizontal=True)
            
            if cat_mode == "เลือกจากรายการเดิม":
                # โหลดหมวดเก่ามาให้เลือก
                all_cats = get_categories()
                category = st.selectbox("เลือกหมวดหมู่:", all_cats)
            else:
                # ช่องพิมพ์ใหม่ (บังคับพิมพ์)
                category = st.text_input("พิมพ์ชื่อหมวดหมู่ที่ต้องการ:", placeholder="เช่น ค่าวัคซีน, ใส่ซองงานแต่ง")
                if category == "":
                    category = "อื่นๆ" # กันเหนียวถ้าลืมพิมพ์
            st.markdown("---")
            # ---------------------------------------

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
                st.success(f"บันทึกหมวด '{category}' เรียบร้อยแล้ว!")
                # ไม่ต้อง rerun ตรงนี้เพื่อให้เห็นข้อความ success

    # === TAB 2: กระเป๋า ===
    with tab2:
        st.header("🏛️ ยอดคงเหลือ")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        def get_balance(source_name):
            if df.empty: return 0.0
            d = df[df['source'] == source_name]
            inc = d[d['type'] == 'รายรับ 💰']['amount'].sum()
            exp = d[d['type'] == 'รายจ่าย 💸']['amount'].sum()
            sav = d[d['type'] == 'เงินออม 🐷']['amount'].sum()
            return inc - exp - sav 

        c1, c2, c3 = st.columns(3)
        c1.metric("เงินสด 💵", f"{get_balance('เงินสด 💵'):,.2f} ฿")
        c2.metric("ธนาคาร 🏦", f"{get_balance('เงินฝากธนาคาร 🏦'):,.2f} ฿")
        c3.metric("บัตรเครดิต 💳", f"{get_balance('บัตรเครดิต 💳'):,.2f} ฿")

    # === TAB 3: วิเคราะห์ ===
    with tab3:
        st.header("📊 วิเคราะห์รายจ่าย")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            expense_df = df[df['type'] == "รายจ่าย 💸"]
            if not expense_df.empty:
                fig = px.pie(expense_df, values='amount', names='category', title='สัดส่วนค่าใช้จ่าย', hole=0.4)
                st.plotly_chart(fig)
            else:
                st.info("ยังไม่มีข้อมูลรายจ่ายจ้า")
        else:
            st.info("ยังไม่มีข้อมูล")

    # === TAB 4: การออม ===
    with tab4:
        st.header("🎯 เงินออม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
            st.metric("ยอดเงินออมสะสม", f"{savings:,.2f} ฿")
            st.progress(min(savings/10000, 1.0))
        else:
            st.metric("ยอดเงินออมสะสม", "0.00 ฿")

    # === TAB 5: ประวัติและแก้ไข ===
    with tab5:
        st.header("📖 จัดการรายการ")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['ลบ?'] = False 
            
            st.info("💡 แก้ไขข้อมูลในตารางได้เลย / จะลบให้ติ๊กช่อง 'ลบ?' แล้วกดปุ่มแดงด้านล่าง")

            edited_df = st.data_editor(
                df, 
                column_config={
                    "ลบ?": st.column_config.CheckboxColumn("ลบ?", width="small"),
                    "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                    "category": st.column_config.TextColumn("หมวดหมู่"),
                    "source": st.column_config.SelectboxColumn("ช่องทาง", options=["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]),
                    "type": st.column_config.SelectboxColumn("ประเภท", options=["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"]),
                    "amount": st.column_config.NumberColumn("จำนวนเงิน", format="%.2f"),
                },
                disabled=["id"],
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                key="editor"
            )

            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🗑️ ลบรายการที่ติ๊ก ✅", type="primary", use_container_width=True):
                    to_delete = edited_df[edited_df['ลบ?'] == True]['id'].tolist()
                    if to_delete:
                        cursor = conn.cursor()
                        for item_id in to_delete:
                            cursor.execute("DELETE FROM transactions WHERE id=?", (item_id,))
                        conn.commit()
                        st.success("ลบเรียบร้อย!")
                        safe_rerun()
            
            with col_btn2:
                if st.button("💾 บันทึกการแก้ไข", use_container_width=True):
                    # แปลงวันที่กลับเป็น Text
                    save_df = edited_df.drop(columns=['ลบ?'])
                    save_df['date'] = save_df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else x)
                    
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transactions")
                    save_df.to_sql('transactions', conn, if_exists='append', index=False)
                    conn.commit()
                    st.success("บันทึกข้อมูลใหม่แล้ว!")
                    safe_rerun()
        else:
            st.info("ยังไม่มีข้อมูลให้แก้ไข")
