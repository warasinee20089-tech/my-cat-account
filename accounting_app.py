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

# --- 3. CSS ตกแต่งให้สวยงาม (สไตล์มินิมอลสีชมพู) ---
st.markdown("""
<style>
    .stApp { background-color: #FFF5F7; }
    .stButton>button { 
        background-color: #DB7093; 
        color: white; 
        border-radius: 12px; 
        border: none; 
        height: 50px;
        font-weight: bold;
        font-size: 18px;
    }
    .stButton>button:hover { background-color: #C71585; color: white; border: 2px solid white; }
    
    /* ตกแต่ง Card */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    h1, h2, h3 { color: #800080; font-family: 'Prompt', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 4. ฐานข้อมูล (V6 Final Design) ---
def init_db():
    conn = sqlite3.connect('meow_wallet_design_v6.db', check_same_thread=False)
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
    # หน้า Login (จัดกึ่งกลางสวยๆ)
    st.write("") # เว้นบรรทัด
    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='background-color: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h1>🐱 Meow Wallet</h1>", unsafe_allow_html=True)
        st.markdown("<h3>จดรับ-จ่าย สไตล์ทาสแมว</h3>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/616/616430.png", width=120) # รูปแมวน่ารักๆ
        st.write("")
        st.text_input("พิมพ์ชื่อทาสแมว:", key="login_name_input", placeholder="ชื่อของคุณ...")
        st.button("🚀 เข้าสู่ระบบ", on_click=login, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/616/616554.png", width=80)
        st.markdown(f"### 👤 {st.session_state.username}")
        st.write("ยินดีต้อนรับกลับมา!")
        st.divider()
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout()
            safe_rerun()

    # Main Content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 จดรายการ", "💰 กระเป๋าเงิน", "📊 กราฟสรุป", "🐷 เงินออม", "⚙️ แก้ไขข้อมูล"])

    # === TAB 1: หน้าจดบันทึก (จัด Layout ใหม่) ===
    with tab1:
        st.markdown("### ✨ เพิ่มรายการใหม่")
        
        with st.container(): # กรอบสีขาวพื้นหลัง
            with st.form("transaction_form", clear_on_submit=True):
                # แถวที่ 1: วันที่ | ประเภท | จำนวนเงิน
                c1, c2, c3 = st.columns([1, 1, 1])
                date_val = c1.date_input("📅 วันที่", datetime.now())
                trans_type = c2.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
                amount = c3.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, format="%.2f")

                st.markdown("---") # เส้นขีดคั่น

                # แถวที่ 2: จัดการหมวดหมู่ (จุดสำคัญ)
                st.info("📂 **เลือกหมวดหมู่** (เลือกจากที่มี หรือ พิมพ์ใหม่ก็ได้)")
                mc1, mc2 = st.columns([1, 2])
                
                with mc1:
                    cat_mode = st.radio("วิธีระบุ:", ["เลือกที่มีอยู่", "➕ พิมพ์ใหม่"], horizontal=False)
                
                with mc2:
                    if cat_mode == "เลือกที่มีอยู่":
                        all_cats = get_categories()
                        category = st.selectbox("🔽 เลือกหมวดหมู่:", all_cats)
                    else:
                        category = st.text_input("✍️ พิมพ์ชื่อหมวดหมู่:", placeholder="เช่น ค่าอาหารเม็ด, ค่า Grab")
                        if category == "": category = "อื่นๆ"

                st.markdown("---")

                # แถวที่ 3: ช่องทาง | รายละเอียด
                r3_1, r3_2 = st.columns([1, 2])
                source = r3_1.selectbox("👛 จ่าย/รับ ผ่านช่องทาง:", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
                description = r3_2.text_input("📝 บันทึกช่วยจำ:", placeholder="รายละเอียดเพิ่มเติม (ถ้ามี)")

                st.write("")
                # ปุ่มบันทึกใหญ่ๆ
                if st.form_submit_button("💖 บันทึกรายการ", use_container_width=True):
                    c = conn.cursor()
                    c.execute("INSERT INTO transactions (date, category, source, description, type, amount) VALUES (?, ?, ?, ?, ?, ?)",
                              (date_val, category, source, description, trans_type, amount))
                    conn.commit()
                    st.success(f"✅ บันทึกยอด {amount} บาท ลงในหมวด '{category}' เรียบร้อย!")

    # === TAB 2: กระเป๋าเงิน (Dashboard) ===
    with tab2:
        st.markdown("### 🏛️ สถานะการเงินปัจจุบัน")
        
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        # คำนวณยอดรวมทั้งหมด
        if not df.empty:
            total_inc = df[df['type'] == 'รายรับ 💰']['amount'].sum()
            total_exp = df[df['type'] == 'รายจ่าย 💸']['amount'].sum()
            total_sav = df[df['type'] == 'เงินออม 🐷']['amount'].sum()
            net_balance = total_inc - total_exp - total_sav
        else:
            net_balance = 0.0

        # แสดงยอดรวมใหญ่ๆ ตรงกลาง
        st.markdown(f"<h1 style='text-align: center; color: #DB7093;'>ยอดสุทธิ: {net_balance:,.2f} ฿</h1>", unsafe_allow_html=True)
        st.write("")

        # แสดงแยกช่องทางแบบการ์ด
        def get_bal(src):
            if df.empty: return 0.0
            d = df[df['source'] == src]
            return d[d['type']=='รายรับ 💰']['amount'].sum() - d[d['type']=='รายจ่าย 💸']['amount'].sum() - d[d['type']=='เงินออม 🐷']['amount'].sum()

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("💵 เงินสด", f"{get_bal('เงินสด 💵'):,.2f} ฿", delta_color="normal")
        col_b.metric("🏦 บัญชีธนาคาร", f"{get_bal('เงินฝากธนาคาร 🏦'):,.2f} ฿", delta_color="normal")
        col_c.metric("💳 บัตรเครดิต", f"{get_bal('บัตรเครดิต 💳'):,.2f} ฿", delta_color="off")

    # === TAB 3: กราฟ ===
    with tab3:
        st.markdown("### 📊 วิเคราะห์รายจ่าย")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        
        if not df.empty:
            exp_df = df[df['type'] == "รายจ่าย 💸"]
            if not exp_df.empty:
                col_chart1, col_chart2 = st.columns([2, 1])
                with col_chart1:
                    fig = px.pie(exp_df, values='amount', names='category', title='หมดเงินไปกับอะไรบ้าง?', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig, use_container_width=True)
                with col_chart2:
                    st.write("#### 🏆 Top 3 รายจ่ายสูงสุด")
                    top3 = exp_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(3)
                    st.dataframe(top3, use_container_width=True)
            else:
                st.info("ยังไม่มีรายจ่าย เก่งมาก! 👍")
        else:
            st.info("ยังไม่มีข้อมูลให้วิเคราะห์")

    # === TAB 4: เงินออม ===
    with tab4:
        st.markdown("### 🐷 เป้าหมายเงินออม")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            savings = df[df['type'] == "เงินออม 🐷"]['amount'].sum()
        else:
            savings = 0.0
            
        col_pig1, col_pig2 = st.columns([1, 2])
        with col_pig1:
            st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=150)
        with col_pig2:
            st.metric("เงินออมสะสม", f"{savings:,.2f} ฿")
            target = 10000 # เป้าหมายสมมติ
            st.progress(min(savings/target, 1.0))
            st.caption(f"เป้าหมายระยะสั้น: {target:,.0f} บาท (สำเร็จไปแล้ว {savings/target*100:.1f}%)")

    # === TAB 5: แก้ไข ===
    with tab5:
        st.markdown("### ⚙️ จัดการข้อมูลย้อนหลัง")
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

            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("🗑️ ยืนยันลบรายการที่เลือก", type="primary", use_container_width=True):
                to_del = edited_df[edited_df['ลบ'] == True]['id'].tolist()
                if to_del:
                    cur = conn.cursor()
                    for i in to_del: cur.execute("DELETE FROM transactions WHERE id=?", (i,))
                    conn.commit()
                    st.toast("ลบข้อมูลแล้ว!", icon="🗑️")
                    safe_rerun()
            
            if c_btn2.button("💾 บันทึกการแก้ไข", use_container_width=True):
                save_df = edited_df.drop(columns=['ลบ'])
                save_df['date'] = save_df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else x)
                cur = conn.cursor()
                cur.execute("DELETE FROM transactions")
                save_df.to_sql('transactions', conn, if_exists='append', index=False)
                conn.commit()
                st.toast("บันทึกข้อมูลแก้ไขแล้ว!", icon="✅")
                safe_rerun()
        else:
            st.info("ยังไม่มีรายการจ้า")
