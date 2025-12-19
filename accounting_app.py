import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บธีม Super Pastel & Cute ---
st.set_page_config(page_title="My Pastel Meow Wallet", layout="wide", page_icon="🌈")

# เพิ่ม CSS ตกแต่งสไตล์ลูกกวาด (Candy Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    
    /* พื้นหลังไล่สีพาสเทล */
    .stApp {
        background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
        background-attachment: fixed;
    }
    
    /* ตกแต่ง Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFF0F5 !important;
        border-right: 5px solid #FFD1DC;
    }

    /* ปุ่มกดสีชมพูฟรุ้งฟริ้ง */
    .stButton>button {
        background: linear-gradient(to right, #FFB7C5, #FFC0CB);
        color: white;
        border-radius: 30px;
        border: 3px solid #FFFFFF;
        box-shadow: 0 4px 15px rgba(255, 183, 197, 0.4);
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 183, 197, 0.6);
    }

    /* การ์ดตัวเลขยอดเงิน */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8);
        border: 2px dashed #FFB7C5;
        border-radius: 20px;
        padding: 15px;
    }
    
    h1 { color: #FF69B4; text-shadow: 2px 2px #FFE4E1; }
    h3 { color: #DB7093; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('pastel_meow_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              desc TEXT, income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. ส่วน Login ---
st.sidebar.markdown("# 🎀 Meow Menu")
user_name = st.sidebar.text_input("✨ ลงชื่อเจ้าของกระเป๋า", placeholder="พิมพ์ชื่อเล่นเมี๊ยว...")

if not user_name:
    st.markdown("<h1 style='text-align: center;'>🌈 My Pastel Meow Wallet 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>บันทึกความสุขและการเงินไปกับน้องแมว</h3>", unsafe_allow_html=True)
    st.image("https://img.freepik.com/free-vector/cute-cat-with-coin-cartoon-vector-icon-illustration_138676-2621.jpg", width=400)
    st.balloons()
    st.stop()

# --- 4. เมนูหลัก (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🍓 บันทึกรายวัน", "🍭 สรุปยอดฟรุ้งฟริ้ง", "📖 สมุดบันทึก"])

with tab1:
    st.markdown(f"### 🧸 เพิ่มรายการใหม่ (คุณ {user_name})")
    
    # ส่วนกรอกข้อมูลแบบใหม่ตามใจคุณ
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 เลือกวันที่", datetime.now())
        type_in = st.radio("✨ ประเภท", ["💸 รายจ่าย", "💰 รายรับ"], horizontal=True)
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=0.5)
        
    with col2:
        # --- ฟีเจอร์ที่คุณต้องการ: พิมพ์หมวดหมู่เองได้ ---
        cat_in = st.text_input("🏷️ หมวดหมู่ (พิมพ์เองได้เลย)", placeholder="เช่น ค่าชานม, ค่าขนมแมว...")
        desc_in = st.text_input("📝 บันทึกสั้นๆ", placeholder="รายละเอียดเพิ่มเติม...")
        st.markdown("💡 *ตัวอย่าง: อาหาร, เดินทาง, ช้อปปิ้ง*")

    if st.button("💖 บันทึกรายการเมี๊ยวว!"):
        if cat_in and amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, desc, income, expense) VALUES (?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, desc_in, inc, exp))
            conn.commit()
            st.snow()
            st.success(f"บันทึก '{cat_in}' เรียบร้อยแล้วจ้า!")
            st.rerun()
        else:
            st.error("อย่าลืมพิมพ์หมวดหมู่และจำนวนเงินนะเมี๊ยวว!")

with tab2:
    st.markdown("### 📊 ภาพรวมการเงินสุดน่ารัก")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        total_in = df['income'].sum()
        total_out = df['expense'].sum()
        
        c1.metric("🎀 รายรับ", f"{total_in:,.2f}")
        c2.metric("🍬 รายจ่าย", f"{total_out:,.2f}")
        c3.metric("🍦 คงเหลือ", f"{total_in - total_out:,.2f}")
        
        # กราฟพาสเทล
        st.write("---")
        fig_pie = px.pie(df[df['expense']>0], values='expense', names='category', 
                         title="🧁 สัดส่วนการใช้เงิน",
                         hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลให้สรุปนะเมี๊ยวว")

with tab3:
    st.markdown("### 📖 ประวัติการบันทึกทั้งหมด")
    df_all = pd.read_sql(f"SELECT date as วันที่, category as หมวดหมู่, desc as รายการ, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC, id DESC", conn)
    
    if not df_all.empty:
        # คำนวณยอดคงเหลือสะสมในตาราง
        df_rev = df_all.iloc[::-1].copy()
        df_rev['ยอดคงเหลือ'] = df_rev['รายรับ'].cumsum() - df_rev['รายจ่าย'].cumsum()
        st.dataframe(df_rev.iloc[::-1], use_container_width=True)
    else:
        st.write("สมุดบันทึกยังว่างเปล่า...")

# ตกแต่งท้ายเว็บ
st.sidebar.markdown("---")
st.sidebar.write("🧸 *เวอร์ชัน 6.0 พาสเทลหัวใจ*")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/616/616430.png", width=100)
