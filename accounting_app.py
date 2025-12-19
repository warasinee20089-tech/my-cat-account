import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ Meow Wallet Pro ---
st.set_page_config(page_title="Meow Wallet Pro", layout="wide", page_icon="💰")

# CSS ตกแต่งโทนพาสเทลและ UI สะอาดตา
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    .stApp { background-color: #FFF5F7; }
    .main-title { color: #FF69B4; text-align: center; font-size: 45px; font-weight: bold; text-shadow: 2px 2px #FFE4E1; }
    .stButton>button { 
        background: linear-gradient(45deg, #FFB7C5, #FF99AC); 
        color: white; border-radius: 20px; border: none; font-weight: bold; width: 100%;
    }
    div[data-testid="stMetric"] { background: white; border-radius: 15px; border: 1px solid #FFD1DC; padding: 10px; }
    .invest-box { background-color: #E0F7FA; padding: 20px; border-radius: 15px; border-left: 5px solid #00ACC1; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล (เพิ่มคอลัมน์ Wallet และ Sub-category) ---
conn = sqlite3.connect('meow_pro_v1.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0)''')
conn.commit()

# --- 3. Sidebar & Login ---
st.sidebar.markdown("<h2 style='text-align: center;'>🐱 Meow Menu</h2>", unsafe_allow_html=True)
user_name = st.sidebar.text_input("ชื่อทาสแมว", placeholder="กรอกชื่อเพื่อเริ่มจ้า...")

if not user_name:
    st.markdown("<div class='main-title'>💰 Meow Wallet Pro</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 100px;'>🐱✨</h1>", unsafe_allow_html=True)
    st.info("กรุณาใส่ชื่อที่แถบด้านซ้ายเพื่อเปิดระบบจัดการเงินและลงทุนนะเมี๊ยวว!")
    st.stop()

# --- 4. เมนู Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 บันทึกรายวัน", "🏦 กระเป๋าเงิน", "📊 สรุป & ลงทุน", "📖 ประวัติ"])

with tab1:
    st.markdown(f"### ✨ บันทึกรายการ (คุณ {user_name})")
    col1, col2 = st.columns(2)
    
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 จ่าย/รับผ่าน", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰"], horizontal=True)
        
    with col2:
        main_cats = ["อาหารและเครื่องดื่ม", "ค่าสาธารณูปโภค", "การเดินทาง", "ช้อปปิ้ง", "ที่อยู่อาศัย", "อื่นๆ"]
        cat_in = st.selectbox("📁 หมวดหมู่หลัก", main_cats)
        sub_cat_in = st.text_input("📝 รายละเอียด/หมวดหมู่ย่อย (พิมพ์เองได้)", placeholder="เช่น ค่าไฟฟ้า, ค่าเน็ต, กาแฟ")
        amt_in = st.number_input("💵 จำนวนเงิน (บาท)", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการสำเร็จ!"):
        if amt_in > 0:
            inc, exp = (amt_in, 0) if "รายรับ" in type_in else (0, amt_in)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense) VALUES (?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, cat_in, sub_cat_in, inc, exp))
            conn.commit()
            st.balloons()
            st.success("บันทึกเรียบร้อยแล้วจ้า!")
            st.rerun()

with tab2:
    st.markdown("### 🏦 สถานะกระเป๋าเงิน")
    df_w = pd.read_sql(f"SELECT wallet, SUM(income) as inc, SUM(expense) as exp FROM records WHERE user_id='{user_name}' GROUP BY wallet", conn)
    
    if not df_w.empty:
        cols = st.columns(3)
        wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
        for i, w_name in enumerate(wallets):
            row = df_w[df_w['wallet'] == w_name]
            balance = row['inc'].sum() - row['exp'].sum() if not row.empty else 0.0
            cols[i % 3].metric(w_name, f"{balance:,.2f} ฿")
    else:
        st.write("ยังไม่มีข้อมูลกระเป๋าเงิน")

with tab3:
    st.markdown("### 📈 สรุปภาพรวม & แนะนำการลงทุน")
    df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
    
    if not df.empty:
        total_in = df['income'].sum()
        total_out = df['expense'].sum()
        net_balance = total_in - total_out
        
        c1, c2 = st.columns(2)
        c1.metric("💰 รายรับรวม", f"{total_in:,.2f}")
        c2.metric("🍦 ยอดคงเหลือสุทธิ", f"{net_balance:,.2f}")

        # --- AI Investment Logic ---
        st.markdown("---")
        st.markdown("#### 🤖 Meow Advisor: ระบบแนะนำการลงทุน")
        
        risk_level = st.select_slider("🎯 ระดับความเสี่ยงที่คุณยอมรับได้", options=["ต่ำ (Low)", "กลาง (Medium)", "สูง (High)"])
        
        savings_ratio = (net_balance / total_in) * 100 if total_in > 0 else 0
        
        st.markdown(f"**Financial Health Check:** คุณมีเงินเก็บคิดเป็น `{savings_ratio:.1f}%` ของรายได้")
        
        with st.expander("💡 คลิกเพื่อดูคำแนะนำจาก AI"):
            if net_balance <= 0:
                st.warning("⚠️ ตอนนี้ยอดคงเหลือยังน้อยอยู่ แนะนำให้คุมรายจ่ายก่อนเริ่มลงทุนนะเมี๊ยวว!")
            else:
                if savings_ratio > 20:
                    st.success("🌟 เยี่ยมมาก! คุณออมเงินได้เกิน 20% ของรายได้ แนะนำให้แบ่งเงินส่วนเกินไปลงทุนดังนี้:")
                
                if risk_level == "ต่ำ (Low)":
                    st.info("**คำแนะนำ:** เน้นความปลอดภัย! แนะนำเงินฝากประจำดิจิทัล ผลตอบแทนสูงกว่าปกติ หรือกองทุนรวมตลาดเงิน (Money Market Fund)")
                elif risk_level == "กลาง (Medium)":
                    st.info("**คำแนะนำ:** สร้างสมดุล! แนะนำกองทุนรวมดัชนี SET50 หรือหุ้นกู้บริษัทชั้นนำ (Investment Grade)")
                else:
                    st.info("**คำแนะนำ:** เน้นเติบโต! แนะนำกองทุนรวมหุ้นต่างประเทศ (เช่น S&P 500) หรือหุ้นรายตัวพื้นฐานดีเพื่อโอกาสรับปันผล")

            # Compound Interest Forecast
            st.markdown("**🔮 พยากรณ์เงินในอนาคต (5 ปี)**")
            rate = 5.0 if risk_level == "กลาง (Medium)" else (2.0 if risk_level == "ต่ำ (Low)" else 10.0)
            future_val = net_balance * ((1 + (rate/100))**5)
            st.write(f"หากนำเงินคงเหลือปัจจุบัน ({net_balance:,.2f} ฿) ไปลงทุนที่ผลตอบแทน `{rate}%` ต่อปี อีก 5 ปีคุณจะมีเงินประมาณ `{future_val:,.2f} ฿` เมี๊ยวว!")

with tab4:
    st.markdown("### 📖 ประวัติการเงินรายตัว")
    df_history = pd.read_sql(f"SELECT date as วันที่, wallet as กระเป๋า, category as หมวดหมู่, sub_category as รายละเอียด, income as รายรับ, expense as รายจ่าย FROM records WHERE user_id='{user_name}' ORDER BY date DESC, id DESC", conn)
    
    if not df_history.empty:
        # คำนวณช่องยอดคงเหลือ (Running Balance)
        df_rev = df_history.iloc[::-1].copy()
        df_rev['ยอดคงเหลือ'] = df_rev['รายรับ'].cumsum() - df_rev['รายจ่าย'].cumsum()
        st.dataframe(df_rev.iloc[::-1], use_container_width=True)
    else:
        st.write("ยังไม่มีประวัติการบันทึก")

st.sidebar.markdown("---")
st.sidebar.write("🐱 *Meow Wallet Pro v2.0*")
