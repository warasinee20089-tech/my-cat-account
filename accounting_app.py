import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ & สไตล์ (โทนชมพูพาสเทล) ---
st.set_page_config(page_title="Cute Meow Finance", layout="wide", page_icon="🐱")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .main { background-color: #FFF0F5; }
    .stMetric { background-color: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stButton>button { background: linear-gradient(135deg, #FFB7C5 0%, #FF99AC 100%); color: white; border-radius: 25px; border: none; height: 50px; font-size: 18px; width: 100%; }
    .category-box { background-color: white; padding: 10px; border-radius: 15px; text-align: center; border: 2px solid #FFD1DC; }
    h1, h2, h3 { color: #D87093; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล ---
conn = sqlite3.connect('meow_pro_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, category TEXT, 
              desc TEXT, income REAL DEFAULT 0, expense REAL DEFAULT 0, icon TEXT)''')
conn.commit()

# --- 3. ข้อมูลหมวดหมู่และไอคอน ---
categories = {
    "อาหาร": "🍔", "การเดินทาง": "🚌", "ของขวัญ": "🎁", "สื่อสาร": "📱", 
    "เสื้อผ้า": "👗", "สุขภาพ": "💊", "ที่อยู่อาศัย": "🏠", "สังคม": "🥂",
    "รายรับ": "💰", "อื่นๆ": "✨"
}

# --- 4. ส่วน Sidebar (Login) ---
st.sidebar.markdown(f"## 🐱 Meow Wallet")
user_name = st.sidebar.text_input("กรอกชื่อผู้ใช้", placeholder="ชื่อของคุณ...")

if not user_name:
    st.markdown("<br><br><h1 style='text-align: center;'>🌸 ยินดีต้อนรับสู่แอปบันทึกรายรับรายจ่าย 🌸</h1>", unsafe_allow_html=True)
    st.image("https://img.freepik.com/free-vector/cute-cat-working-laptop-cartoon-icon-illustration_138676-2503.jpg", width=300)
    st.info("กรุณาเข้าสู่ระบบที่แถบด้านซ้ายเพื่อเริ่มใช้งานเมี๊ยวว!")
    st.stop()

# --- 5. เมนูหลัก ---
tab1, tab2, tab3 = st.tabs(["📝 บันทึกใหม่", "📊 สรุปรายงาน", "📜 ประวัติทั้งหมด"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        date_in = st.date_input("วันที่", datetime.now())
        type_in = st.radio("ประเภทรายการ", ["รายจ่าย", "รายรับ"], horizontal=True)
        amt_in = st.number_input("จำนวนเงิน (฿)", min_value=0.0)
        
    with col2:
        cat_in = st.selectbox("เลือกหมวดหมู่", list(categories.keys()))
        desc_in = st.text_input("บันทึกช่วยจำ", placeholder="เช่น ส้มตำป้าประยงค์")
        
    if st.button("💖 บันทึกรายการ"):
        if amt_in > 0:
            icon = categories[cat_in]
            inc, exp = (amt_in, 0) if type_in == "รายรับ" else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, category, desc, income, expense, icon) VALUES (?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), cat_in, desc_in, inc, exp, icon))
            conn.commit()
            st.success("บันทึกสำเร็จแล้วเมี๊ยวว!")
            st.rerun()

with tab2:
    st.markdown(f"### 📈 ภาพรวมของ {user_name}")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    
    if not df.empty:
        t_inc = df['income'].sum()
        t_exp = df['expense'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("รายรับทั้งหมด", f"{t_inc:,.2f} ฿")
        c2.metric("รายจ่ายทั้งหมด", f"-{t_exp:,.2f} ฿", delta_color="inverse")
        c3.metric("คงเหลือสุทธิ", f"{t_inc-t_exp:,.2f} ฿")
        
        st.write("---")
        
        # กราฟวงกลมแบ่งตามหมวดหมู่ (เหมือนในรูปที่คุณต้องการ)
        exp_df = df[df['expense'] > 0].groupby('category')['expense'].sum().reset_index()
        if not exp_df.empty:
            fig = px.pie(exp_df, values='expense', names='category', 
                         title='สัดส่วนรายจ่ายตามหมวดหมู่',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลสำหรับทำรายงาน")

with tab3:
    st.markdown("### 📜 ประวัติการบันทึก")
    df_history = pd.read_sql(f"SELECT date as วันที่, icon as ไอคอน, category as หมวดหมู่, desc as รายการ, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC, id DESC", conn)
    
    if not df_history.empty:
        # คำนวณยอดคงเหลือสะสม
        df_calc = df_history.iloc[::-1].copy()
        df_calc['คงเหลือ'] = df_calc['รายรับ'].cumsum() - df_calc['รายจ่าย'].cumsum()
        st.dataframe(df_calc.iloc[::-1], use_container_width=True)
    else:
        st.write("ไม่มีประวัติการบันทึก")
