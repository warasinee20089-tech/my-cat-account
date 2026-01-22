import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import io
from PIL import Image
import base64

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
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th { background-color: #FFD1DC !important; color: #2D2D2D !important; padding: 10px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #FFD1DC; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันจัดการฐานข้อมูล ---
DB_NAME = 'meow_wallet_v20.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS records 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                      wallet TEXT, category TEXT, sub_category TEXT,
                      income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                      receipt_img BLOB)''')
        conn.commit()

init_db()

def get_image_thumbnail(img_bytes):
    if img_bytes is None:
        return "ไม่มีใบเสร็จ"
    try:
        encoded = base64.b64encode(img_bytes).decode()
        return f'<img src="data:image/png;base64,{encoded}" width="50" style="border-radius:5px;">'
    except:
        return "ไฟล์เสีย"

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

# --- 4. ดึงข้อมูล ---
user_name = st.session_state.user_name
with sqlite3.connect(DB_NAME) as conn:
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id=?", conn, params=(user_name,))

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['เดือน'] = df['date'].dt.strftime('%Y-%m')

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
            img_byte = receipt_file.getvalue() if receipt_file else None
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
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
        monthly_stats = df.groupby('เดือน')[['income', 'expense']].sum().reset_index()
        monthly_stats = monthly_stats.rename(columns={'income': 'รายรับ', 'expense': 'รายจ่าย'})
        fig_bar = px.bar(monthly_stats, x='เดือน', y=['รายรับ', 'รายจ่าย'], 
                         barmode='group', title="📈 แนวโน้มรายรับ - รายจ่าย",
                         color_discrete_sequence=['#B2E2F2', '#FF9AA2'])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("บันทึกข้อมูลก่อนเพื่อดูการวิเคราะห์เมี๊ยวว")

with tab4:
    st.markdown("### 🎯 การติดตามการออม")
    if not df.empty:
        total_save = df['savings'].sum()
        total_in = df['income'].sum()
        c1, c2 = st.columns(2)
        c1.metric("💰 เงินออมสะสมทั้งหมด", f"{total_save:,.2f} ฿")
        if total_in > 0:
            percent_save = (total_save / total_in) * 100
            c2.metric("📈 สัดส่วนการออม", f"{percent_save:.1f}%")
            st.progress(min(total_save / total_in, 1.0))
    else:
        st.info("ยังไม่มีข้อมูลการออมเมี๊ยวว")

with tab5:
    st.markdown("### 📖 ประวัติและจัดการรายการ")
    if not df.empty:
        # คำนวณยอดคงเหลือสะสม (Running Balance)
        df_sorted = df.sort_values(by=['date', 'id'], ascending=[True, True])
        df_sorted['คงเหลือสะสม'] = df_sorted['income'].cumsum() - df_sorted['expense'].cumsum() - df_sorted['savings'].cumsum()
        
        # เตรียมแสดงผล
        df_thai = df_sorted.copy()
        df_thai['ใบเสร็จ'] = df_thai['receipt_img'].apply(get_image_thumbnail)
        
        # แปลงชื่อคอลัมน์
        df_thai = df_thai.rename(columns={
            'id': 'ลำดับ', 'date': 'วันที่', 'wallet': 'ช่องทาง',
            'category': 'หมวดหมู่', 'sub_category': 'รายละเอียด',
            'income': 'รายรับ', 'expense': 'รายจ่าย', 'savings': 'เงินออม',
            'คงเหลือสะสม': 'คงเหลือ (฿)'
        })
        
        # เลือกคอลัมน์และแสดงจากใหม่ไปเก่า
        display_cols = ['ลำดับ', 'ใบเสร็จ', 'วันที่', 'ช่องทาง', 'หมวดหมู่', 'รายละเอียด', 'รายรับ', 'รายจ่าย', 'เงินออม', 'คงเหลือ (฿)']
        df_final = df_thai[display_cols].sort_values(by='ลำดับ', ascending=False)
        
        st.write(df_final.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 🛠️ จัดการรายการ")
        selected_id = st.selectbox("เลือก ลำดับ (ID) เพื่อดูรูปใหญ่/แก้ไข:", df_final['ลำดับ'].tolist())
        
        if selected_id:
            row = df[df['id'] == selected_id].iloc[0]
            if row['receipt_img'] is not None:
                st.image(row['receipt_img'], width=400, caption="ใบเสร็จขนาดใหญ่")
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                new_date = st.date_input("แก้ไขวันที่", row['date'])
                new_amt = st.number_input("แก้ไขจำนวนเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
            with col_e2:
                new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
                
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("✅ ยืนยันการแก้ไข", use_container_width=True):
                if row['income'] > 0: n_vals = (new_amt, 0, 0)
                elif row['expense'] > 0: n_vals = (0, new_amt, 0)
                else: n_vals = (0, 0, new_amt)
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                                 (new_date.strftime('%Y-%m-%d'), n_vals[0], n_vals[1], n_vals[2], new_sub, selected_id))
                    conn.commit()
                st.success("แก้ไขข้อมูลเรียบร้อย!")
                st.rerun()
                
            if c_btn2.button("🗑️ ลบรายการนี้", use_container_width=True):
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("DELETE FROM records WHERE id=?", (int(selected_id),))
                    conn.commit()
                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลในประวัติเมี๊ยวว")
