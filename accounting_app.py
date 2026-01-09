import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import io
from PIL import Image

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Meow Wallet Ultimate", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF5F7 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; 
        color: #2D2D2D !important;
    }
    .main-title { color: #FF69B4; text-align: center; font-size: 40px; font-weight: bold; padding: 15px; }
    div[data-testid="stMetric"] { background: white !important; border-radius: 15px; border: 2px solid #FFD1DC !important; padding: 15px; }
    .stButton>button { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฐานข้อมูล ---
def get_db():
    conn = sqlite3.connect('meow_wallet_v20.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
c = conn.cursor()
# เพิ่ม column receipt_img สำหรับเก็บไฟล์ภาพ (BLOB)
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
              receipt_img BLOB)''')
conn.commit()

# --- 3. ระบบ Session ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_l2, _ = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", key="login_name")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. ดึงข้อมูลและจัดการ Data ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['เดือน'] = df['date'].dt.strftime('%Y-%m') # สำหรับกราฟรายเดือน

# --- 5. Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        receipt_file = st.file_uploader("📸 อัปโหลดใบเสร็จ (ถ้ามี)", type=['jpg', 'jpeg', 'png'])
        
    with col2:
        cat_map = {
            "รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"],
            "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"],
            "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]
        }
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        final_cat = st.text_input("✍️ ระบุหมวดหมู่เอง") if selected_cat == "อื่นๆ ➕" else selected_cat
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0 and final_cat:
            # แปลงไฟล์ภาพเป็น bytes
            img_byte = None
            if receipt_file is not None:
                img_byte = receipt_file.getvalue()
                
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_cat, sub_cat, inc, exp, sav, img_byte))
            conn.commit()
            st.success("บันทึกสำเร็จเมี๊ยววว!")
            st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    c_w1, c_w2, c_w3 = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w in enumerate(wallets):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        cols = [c_w1, c_w2, c_w3]
        cols[i].metric(w, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์การเงินรายเดือน")
    if not df.empty:
        # 1. กราฟแท่งเปรียบเทียบรายรับ-รายจ่ายรายเดือน
        monthly_stats = df.groupby('เดือน')[['income', 'expense']].sum().reset_index()
        monthly_stats = monthly_stats.rename(columns={'income': 'รายรับ', 'expense': 'รายจ่าย'})
        fig_bar = px.bar(monthly_stats, x='เดือน', y=['รายรับ', 'รายจ่าย'], 
                         barmode='group',
                         title="📈 เปรียบเทียบรายรับ - รายจ่าย",
                         color_discrete_sequence=['#B2E2F2', '#FF9AA2'], # พาสเทล ฟ้า-ชมพู
                         labels={'value': 'จำนวนเงิน (฿)', 'variable': 'ประเภท'})
        fig_bar.update_layout(font_family="Kanit")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        
        # 2. แผนภูมิวงกลมภาพรวม (รายจ่าย vs เงินออม)
        total_exp = df['expense'].sum()
        total_sav = df['savings'].sum()
        if total_exp > 0 or total_sav > 0:
            st.markdown("#### 🍰 ภาพรวมรายจ่ายและเงินออม")
            fig_pie_main = px.pie(names=['รายจ่าย', 'เงินออม'], 
                                  values=[total_exp, total_sav], 
                                  hole=0.4, 
                                  color_discrete_sequence=['#FFB7CE', '#C5E1A5'])
            st.plotly_chart(fig_pie_main, use_container_width=True)

        col_a, col_b = st.columns(2)
        
        with col_a:
            # 3. รายรับแยกตามหมวดหมู่
            inc_df = df[df['income'] > 0]
            if not inc_df.empty:
                st.markdown("#### 💰 รายรับแยกตามหมวดหมู่")
                fig_inc = px.pie(inc_df, names='category', values='income', 
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_inc, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลรายรับ")

        with col_b:
            # 4. รายจ่ายแยกตามหมวดหมู่
            exp_df = df[df['expense'] > 0]
            if not exp_df.empty:
                st.markdown("#### 💸 รายจ่ายแยกตามหมวดหมู่")
                fig_exp = px.pie(exp_df, names='category', values='expense', 
                                 color_discrete_sequence=px.colors.qualitative.Pastel2)
                st.plotly_chart(fig_exp, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลรายจ่าย")
    else:
        st.info("บันทึกข้อมูลก่อนเพื่อดูการวิเคราะห์เมี๊ยวว")

with tab4:
    st.markdown("### 🎯 การออม")
    total_save = df['savings'].sum() if not df.empty else 0
    total_in = df['income'].sum() if not df.empty else 0
    st.metric("เงินออมสะสม", f"{total_save:,.2f} ฿")
    if total_in > 0:
        progress_val = min(total_save/total_in, 1.0)
        st.progress(progress_val)
        st.write(f"ออมไปแล้ว {(total_save/total_in)*100:.1f}% ของรายรับทั้งหมด")
    else:
        st.info("เพิ่มรายรับเพื่อดูสัดส่วนการออม")

with tab5:
    st.markdown("### 📖 ประวัติและจัดการรายการ")
    if not df.empty:
        df_display = df.sort_values(by='id', ascending=False)
        # ไม่แสดง column receipt_img ในตาราง
        st.dataframe(df_display.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🛠️ จัดการรายการและดูใบเสร็จ")
        selected_id = st.selectbox("เลือก ID รายการที่ต้องการดู/จัดการ:", df_display['id'].tolist())
        
        if selected_id:
            row = df[df['id'] == selected_id].iloc[0]
            
            # แสดงใบเสร็จถ้ามี
            if row['receipt_img'] is not None:
                st.markdown("##### 📸 ใบเสร็จ")
                st.image(row['receipt_img'], width=300)
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                new_date = st.date_input("แก้ไขวันที่", row['date'])
                new_amt = st.number_input("แก้ไขจำนวนเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
            with col_e2:
                new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
                
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("✅ ยืนยันการแก้ไข", use_container_width=True):
                # ตรวจสอบประเภทเพื่ออัปเดตช่องที่ถูกต้อง
                if row['income'] > 0: new_vals = (new_amt, 0, 0)
                elif row['expense'] > 0: new_vals = (0, new_amt, 0)
                else: new_vals = (0, 0, new_amt)
                
                c.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                          (new_date.strftime('%Y-%m-%d'), new_vals[0], new_vals[1], new_vals[2], new_sub, selected_id))
                conn.commit()
                st.success("แก้ไขข้อมูลเรียบร้อย!")
                st.rerun()
                
            if c_btn2.button("🗑️ ลบรายการนี้", use_container_width=True):
                c.execute("DELETE FROM records WHERE id=?", (selected_id,))
                conn.commit()
                st.warning("ลบรายการแล้ว!")
                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลเมี๊ยวว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
