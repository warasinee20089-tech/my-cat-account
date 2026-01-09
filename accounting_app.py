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
    .badge-card {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        border: 2px solid #FFD1DC; margin-bottom: 20px; transition: 0.3s;
    }
    .badge-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(255,182,193,0.3); }
    .badge-icon { font-size: 50px; margin-bottom: 10px; }
    .badge-title { font-weight: bold; color: #FF69B4; font-size: 18px; }
    .badge-desc { font-size: 14px; color: #666; }
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

# --- 4. DATA LOADING & HELPER ---
user_name = st.session_state.user_name
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)

def get_thai_month(date_obj):
    months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
              "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{months[date_obj.month]} {date_obj.year + 543}"

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df['เดือน'] = df['date'].apply(get_thai_month)

total_in = df['income'].sum() if not df.empty else 0
total_out = df['expense'].sum() if not df.empty else 0
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. MOOD & LEVEL LOGIC ---
mood_text, level_text = ("😺", "ลูกแมวฝึกหัด 🌱")
if total_in > 0:
    if (total_save/total_in) >= 0.3: mood_text = "😸 (ทาสออมเก่งมาก!)"
    elif total_out > total_in: mood_text = "🙀 (ใช้เกินงบแล้ว!)"
    if total_save >= 20000: level_text = "แมวเหมียวเศรษฐี ✨"
    elif total_save >= 50000: level_text = "ท่านเจ้าของคาเฟ่แมว 👑"

# --- 6. MAIN UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #FF69B4;'>{mood_text}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>ระดับทาส: <b>{level_text}</b></p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("📅 วันที่", datetime.now())
        wallet_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        type_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
    with col2:
        cat_map = {"รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "อื่นๆ ➕"], "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เครื่องดื่ม ☕", "เดินทาง 🚗", "ช้อปปิ้ง 🛍️", "อื่นๆ ➕"], "เงินออม 🐷": ["ออมระยะยาว 🏦", "ออมฉุกเฉิน 🚑", "อื่นๆ ➕"]}
        selected_cat = st.selectbox("📁 หมวดหมู่", cat_map[type_in])
        final_cat = st.text_input("✍️ ระบุเอง") if selected_cat == "อื่นๆ ➕" else selected_cat
        sub_cat = st.text_input("📝 รายละเอียด")
        amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    if st.button("💖 บันทึกรายการ", use_container_width=True):
        if amt > 0:
            inc, exp, sav = (amt,0,0) if type_in=="รายรับ 💰" else (0,amt,0) if type_in=="รายจ่าย 💸" else (0,0,amt)
            c.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings) VALUES (?,?,?,?,?,?,?,?)", (user_name, date_in.strftime('%Y-%m-%d'), wallet_in, final_cat, sub_cat, inc, exp, sav))
            conn.commit(); st.rerun()

with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    cw1, cw2, cw3 = st.columns(3)
    for i, w in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        [cw1, cw2, cw3][i].metric(w, f"{bal:,.2f} ฿")

with tab3:
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        ca1, ca2, ca3 = st.columns(3)
        exp_df = df[df['expense'] > 0]
        if not exp_df.empty:
            t_cat = exp_df.groupby('category')['expense'].sum().idxmax()
            t_amt = exp_df.groupby('category')['expense'].sum().max()
            e_icon, e_title, e_desc = ("🍛", "นักชิมอันดับหนึ่ง", f"เปย์หนักไปกับของอร่อย\n{t_amt:,.0f} ฿") if "อาหาร" in t_cat else ("🛍️", "นักช้อปมือไว", f"หมดไปกับของต้องมี!\n{t_amt:,.0f} ฿") if "ช้อปปิ้ง" in t_cat else ("📦", "นักจัดการทั่วไป", f"เน้นจ่ายหมวด {t_cat}\n{t_amt:,.0f} ฿")
        else: e_icon, e_title, e_desc = "💤", "ทาสแมวสายจำศีล", "ยังไม่มีรายจ่าย"
        
        inc_df = df[df['income'] > 0]
        i_cat = inc_df.groupby('category')['income'].sum().idxmax() if not inc_df.empty else ""
        i_icon, i_title, i_desc = ("💵", "มนุษย์เงินเดือนผู้มั่งคั่ง", "รับหลักจากงานประจำ") if "เงินเดือน" in i_cat else ("📦", "พ่อค้าแม่ค้าหน้ามน", "รับจากขายของ") if "ขายของ" in i_cat else ("💎", "ขุมทรัพย์มหาศาล", f"รับจาก {i_cat}") if i_cat else ("🐱", "ทาสรอความหวัง", "รอเงินเข้าเมี๊ยว")

        s_pct = (total_save / total_in * 100) if total_in > 0 else 0
        s_icon, s_title, s_desc = ("👑", "ราชา/ราชินีนักออม", f"ออมโหด! {s_pct:.1f}%") if s_pct >= 50 else ("🛡️", "ป้อมปราการมั่นคง", f"วินัยดีมาก {s_pct:.1f}%") if s_pct >= 20 else ("🌱", "ต้นกล้าแห่งการออม", f"สะสมทีละนิด {s_pct:.1f}%") if total_save > 0 else ("🙀", "ไหแตกแล้วเมี๊ยว", "ยังไม่ได้ออมเลย!")

        ca1.markdown(f"<div class='badge-card'><div class='badge-icon'>{e_icon}</div><div class='badge-title'>{e_title}</div><p class='badge-desc'>{e_desc}</p></div>", unsafe_allow_html=True)
        ca2.markdown(f"<div class='badge-card'><div class='badge-icon'>{i_icon}</div><div class='badge-title'>{i_title}</div><p class='badge-desc'>{i_desc}</p></div>", unsafe_allow_html=True)
        ca3.markdown(f"<div class='badge-card'><div class='badge-icon'>{s_icon}</div><div class='badge-title'>{s_title}</div><p class='badge-desc'>{s_desc}</p></div>", unsafe_allow_html=True)
        
        st.markdown("#### 🍰 1. สัดส่วนการใช้จ่ายและเงินออม")
        st.plotly_chart(px.pie(names=['รายจ่าย 💸', 'เงินออม 🐷'], values=[total_out, total_save], hole=0.5, color_discrete_sequence=['#FF9AA2', '#B2E2F2']), use_container_width=True)
        st.markdown("#### 🍱 2. รายจ่ายแยกตามหมวดหมู่")
        if not exp_df.empty: st.plotly_chart(px.pie(exp_df.groupby('category')['expense'].sum().reset_index(), names='category', values='expense', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        st.markdown("#### 💰 3. รายรับแยกตามหมวดหมู่")
        if not inc_df.empty: st.plotly_chart(px.pie(inc_df.groupby('category')['income'].sum().reset_index(), names='category', values='income', hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

with tab4:
    st.markdown("### 🎯 การออม")
    st.metric("เงินออมสะสมทั้งหมด", f"{total_save:,.2f} ฿")
    st.progress(min(total_save / 50000, 1.0))

with tab5:
    st.markdown("### 📖 ประวัติและแก้ไข")
    if not df.empty:
        df_display = df.sort_values(by='id', ascending=False)
        st.dataframe(df_display.drop(columns=['user_id', 'เดือน']), use_container_width=True)
        
        # --- ฟังก์ชันแก้ไขข้อมูล (Restored) ---
        st.markdown("---")
        st.markdown("#### ✏️ แก้ไขหรือลบรายการ")
        sel_id = st.selectbox("เลือก ID รายการที่ต้องการจัดการ:", df_display['id'].tolist())
        if sel_id:
            row = df[df['id'] == sel_id].iloc[0]
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                new_date = st.date_input("แก้ไขวันที่", row['date'].to_pydatetime())
                curr_amt = float(row['income'] if row['income'] > 0 else row['expense'] if row['expense'] > 0 else row['savings'])
                new_amt = st.number_input("แก้ไขจำนวนเงิน", value=curr_amt)
            with col_e2:
                new_sub = st.text_input("แก้ไขรายละเอียด", value=row['sub_category'])
                new_wallet = st.selectbox("แก้ไขช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"], index=["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"].index(row['wallet']))
            
            ce1, ce2 = st.columns(2)
            if ce1.button("✅ ยืนยันการแก้ไข", use_container_width=True):
                n_inc, n_exp, n_sav = (new_amt,0,0) if row['income']>0 else (0,new_amt,0) if row['expense']>0 else (0,0,new_amt)
                c.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, sub_category=?, wallet=? WHERE id=?", (new_date.strftime('%Y-%m-%d'), n_inc, n_exp, n_sav, new_sub, new_wallet, sel_id))
                conn.commit(); st.success("อัปเดตเรียบร้อย!"); st.rerun()
            if ce2.button("🗑️ ลบรายการนี้", use_container_width=True):
                c.execute("DELETE FROM records WHERE id=?", (sel_id,))
                conn.commit(); st.rerun()
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
