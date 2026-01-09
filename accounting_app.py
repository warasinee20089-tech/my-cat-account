import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
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

# --- 2. DATABASE ENGINE ---
def get_db():
    conn = sqlite3.connect('meow_wallet_ultimate.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS records 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
              wallet TEXT, category TEXT, sub_category TEXT,
              income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0)''')
conn.commit()

# --- 3. SESSION MANAGEMENT ---
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

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. LOGIC: MOOD & LEVEL ---
def get_cat_status(t_in, t_out, t_save):
    if t_in == 0: 
        mood = "🐱 (รอกินปลาทูอยู่เมี๊ยวว)"
    elif (t_save/t_in) >= 0.3: 
        mood = "😸 (ทาสออมเก่งมาก ยิ้มแก้มปริ!)"
    elif t_out > t_in: 
        mood = "🙀 (ทาสใช้เงินเกินงบแล้ว! ตกใจล้าวว)"
    else: 
        mood = "😺 (วันนี้ทำดีแล้วเมี๊ยวว)"
    
    if t_save < 5000: 
        level = "ลูกแมวฝึกหัด 🌱"
    elif t_save < 20000: 
        level = "แมวเหมียวเศรษฐี ✨"
    else: 
        level = "ท่านเจ้าของคาเฟ่แมว 👑"
    return mood, level

mood_text, level_text = get_cat_status(total_in, total_out, total_save)

# --- 6. MAIN UI ---
# แก้ไขจุดที่ทำให้เกิด SyntaxError จากรูปภาพ
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #FF69B4;'>{mood_text}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 18px;'>ระดับทาส: <b>{level_text}</b></p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
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
        if amt > 0:
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", 
                      (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_cat, sub_cat, inc, exp, sav))
            conn.commit()
            st.success("บันทึกสำเร็จ!")
            st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    c_w1, c_w2, c_w3 = st.columns(3)
    wallets_list = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w in enumerate(wallets_list):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        cols = [c_w1, c_w2, c_w3]
        cols[i].metric(w, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์ (🌡️ Meow Thermometer)")
    if not df.empty:
        # 🌡️ Budget Alert
        st.markdown("#### เกจวัดการใช้จ่ายเดือนนี้")
        monthly_limit = st.number_input("ตั้งงบรายจ่ายต่อเดือน (฿):", min_value=1.0, value=10000.0)
        current_month_exp = df[df['date'].dt.month == datetime.now().month]['expense'].sum()
        
        usage_pct = min(current_month_exp / monthly_limit, 1.0)
        color = "green" if usage_pct < 0.5 else "orange" if usage_pct < 0.8 else "red"
        st.markdown(f"""
            <div style='width:100%; background:#eee; border-radius:10px;'>
                <div style='width:{usage_pct*100}%; background:{color}; height:20px; border-radius:10px;'></div>
            </div>
            """, unsafe_allow_html=True)
        st.write(f"ใช้ไปแล้ว {current_month_exp:,.2f} / {monthly_limit:,.2f} ฿")
        if usage_pct >= 0.9: 
            st.error("🙀 ทาสหยุดช้อปได้แล้ว! อาหารแมวจะหมดแล้วนะ!")

        # 📅 Monthly Comparison
        st.markdown("---")
        st.markdown("#### เปรียบเทียบรายเดือน")
        df['month_year'] = df['date'].dt.strftime('%Y-%m')
        monthly_df = df.groupby('month_year')[['income', 'expense']].sum().reset_index()
        fig_bar = px.bar(monthly_df, x='month_year', y=['income', 'expense'], barmode='group', 
                         color_discrete_map={'income': '#FF69B4', 'expense': '#FF5252'},
                         title="รายรับ vs รายจ่าย รายเดือน")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Pie Chart
        st.markdown("---")
        fig_pie = px.pie(names=['รายจ่าย', 'เงินออม'], values=[total_out, total_save], hole=0.4, color_discrete_sequence=['#FF5252', '#FF69B4'])
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลให้วิเคราะห์")

with tab4:
    st.markdown("### 🎯 การออม (Saving Level Up)")
    st.metric("เงินออมสะสมทั้งหมด", f"{total_save:,.2f} ฿")
    st.write(f"ระดับปัจจุบัน: **{level_text}**")
    
    # Progress to Next Level
    next_goal = 5000 if total_save < 5000 else 20000 if total_save < 20000 else 50000
    p_val = min(total_save / next_goal, 1.0)
    st.write(f"เป้าหมายต่อไป: {next_goal:,.0f} ฿")
    st.progress(p_val)
    
    if total_in > 0:
        st.write(f"คิดเป็น {(total_save/total_in)*100:.1f}% ของรายรับ")

with tab5:
    st.markdown("### 📖 ประวัติและจัดการ")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ดาวน์โหลดรายงาน (CSV)", data=csv, file_name=f'meow_report_{user_name}.csv', mime='text/csv')
        
        st.divider()
        df_display = df.sort_values(by='id', ascending=False)
        st.dataframe(df_display.drop(columns=['user_id']), use_container_width=True)
        
        selected_id = st.selectbox("เลือก ID รายการที่ต้องการจัดการ:", df_display['id'].tolist())
        if selected_id:
            row = df[df['id'] == selected_id].iloc[0]
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                # แก้ไขจุดที่ทำให้วงเล็บไม่ปิดในรูปที่ 2
                new_date = st.date_input("แก้ไขวันที่", row['date'].to_pydatetime())
                new_amt = st.number_input("แก้ไขจำนวนเงิน", value=float(max(row['income'], row['expense'], row['savings'])))
            with col_e2:
                new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
                
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("✅ ยืนยันการแก้ไข", use_container_width=True):
                # ตรวจสอบประเภทเพื่อ Update ค่าให้ถูกช่อง
                if row['income'] > 0: 
                    new_vals = (new_amt, 0, 0)
                elif row['expense'] > 0: 
                    new_vals = (0, new_amt, 0)
                else: 
                    new_vals = (0, 0, new_amt)
                
                c.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                          (new_date.strftime('%Y-%m-%d'), new_vals[0], new_vals[1], new_vals[2], new_sub, selected_id))
                conn.commit()
                st.success("แก้ไขแล้ว!")
                st.rerun()
                
            if c_btn2.button("🗑️ ลบรายการนี้", use_container_width=True):
                c.execute("DELETE FROM records WHERE id=?", (selected_id,))
                conn.commit()
                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูล")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
