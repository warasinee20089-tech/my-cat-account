import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. ฟังก์ชันพิเศษ แก้ปัญหา Rerun Error (ใช้ได้ทุกเวอร์ชัน) ---
def safe_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.write("กรุณากดปุ่ม R (Refresh) ที่คีย์บอร์ดเพื่อโหลดหน้าใหม่")

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

# --- 3. ฐานข้อมูล ---
def init_db():
    conn = sqlite3.connect('meow_wallet_pro.db', check_same_thread=False)
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

# --- ฟังก์ชันดึงหมวดหมู่ทั้งหมด ---
def get_all_categories():
    default_cats = ["ค่าอาหาร 🍲", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "เงินเดือน 💰", "ขายของ 📦", "เงินออม 🐷"]
    try:
        df = pd.read_sql("SELECT DISTINCT category FROM transactions", conn)
        db_cats = df['category'].dropna().unique().tolist()
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 แก้ไขข้อมูล (Pro)"])

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
            fig = px.pie(expense_df, values='amount', names='category', title='สัดส่วนค่าใช้จ่ายจริง', hole=0.4)
            st.plotly_chart(fig)
        else:
            st.info("ยังไม่มีข้อมูลรายจ่าย")

    # ---------------- TAB 4: การออม ----------------
    with tab4:
        st.header("🎯 เงินออม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
        st.metric("ยอดเงินออมสะสม", f"{savings:,.2f} ฿")
        st.progress(min(savings/10000, 1.0))

    # ---------------- TAB 5: แก้ไข (แบบแก้ในช่องได้เลย) ----------------
    with tab5:
        st.header("📖 ตารางจัดการข้อมูล (แก้ในช่องได้เลย)")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        
        if not df.empty:
            # แปลงวันที่ให้เป็น Format วันที่จริงๆ (จะได้มีปฏิทินเด้งตอนแก้)
            df['date'] = pd.to_datetime(df['date'])
            df['ลบ?'] = False # เพิ่มช่องสำหรับติ๊กลบ
            
            st.info("💡 คลิกแก้ในตารางได้เลย: วันที่(มีปฏิทิน), ประเภท(มีตัวเลือก), หมวดหมู่(พิมพ์แก้เองได้)")

            # ตั้งค่าตารางให้แก้ไขง่ายๆ
            edited_df = st.data_editor(
                df, 
                column_config={
                    "ลบ?": st.column_config.CheckboxColumn("ลบ?", width="small"),
                    "date": st.column_config.DateColumn("วันที่", format="YYYY-MM-DD"),
                    "category": st.column_config.TextColumn("หมวดหมู่ (แก้ตรงนี้)"),
                    "source": st.column_config.SelectboxColumn("ช่องทาง", options=["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]),
                    "type": st.column_config.SelectboxColumn("ประเภท", options=["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"]),
                    "amount": st.column_config.NumberColumn("จำนวนเงิน", format="%.2f"),
                },
                disabled=["id"],
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic", # อนุญาตให้เพิ่มแถวใหม่ได้ด้วย
                key="editor"
            )

            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                # ปุ่มลบ
                if st.button("🗑️ ลบรายการที่ติ๊ก ✅", type="primary", use_container_width=True):
                    to_delete = edited_df[edited_df['ลบ?'] == True]['id'].tolist()
                    if to_delete:
                        cursor = conn.cursor()
                        for item_id in to_delete:
                            cursor.execute("DELETE FROM transactions WHERE id=?", (item_id,))
                        conn.commit()
                        st.success("ลบเรียบร้อย!")
                        safe_rerun() # ใช้ฟังก์ชันแก้ Error
            
            with col_btn2:
                # ปุ่มบันทึกการแก้ไข
                if st.button("💾 บันทึกการแก้ไขทั้งหมด", use_container_width=True):
                    # แปลงวันที่กลับเป็น Text เพื่อเก็บลง DB
                    save_df = edited_df.drop(columns=['ลบ?'])
                    save_df['date'] = save_df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else x)
                    
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transactions") # ลบเก่า
                    save_df.to_sql('transactions', conn, if_exists='append', index=False) # ใส่ใหม่
                    conn.commit()
                    st.success("บันทึกข้อมูลใหม่แล้ว!")
                    safe_rerun() # ใช้ฟังก์ชันแก้ Error
        else:
            st.info("ยังไม่มีรายการ")

    st.markdown("---")
    if st.button("🚪 ออกจากระบบ"):
        logout()
        safe_rerun()
