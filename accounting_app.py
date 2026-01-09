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
    
    /* Achievement Badge Styles - Modern & Cute */
    .badge-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 2px solid #FFD1DC;
        margin-bottom: 20px;
        transition: 0.3s;
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
def get_cat_status(t_in, t_out, t_save):
    if t_in == 0: mood = "🐱 (รอกินปลาทูอยู่เมี๊ยวว)"
    elif (t_save/t_in) >= 0.3: mood = "😸 (ทาสออมเก่งมาก ยิ้มแก้มปริ!)"
    elif t_out > t_in: mood = "🙀 (ทาสใช้เงินเกินงบแล้ว! ตกใจล้าวว)"
    else: mood = "😺 (วันนี้ทำดีแล้วเมี๊ยวว)"
    
    if t_save < 5000: level = "ลูกแมวฝึกหัด 🌱"
    elif t_save < 20000: level = "แมวเหมียวเศรษฐี ✨"
    else: level = "ท่านเจ้าของคาเฟ่แมว 👑"
    return mood, level

mood_text, level_text = get_cat_status(total_in, total_out, total_save)

# --- 6. MAIN UI ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #FF69B4;'>{mood_text}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 18px;'>ระดับทาส: <b>{level_text}</b></p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 การออม", "📖 ประวัติและแก้ไข"])

# --- TAB 1: บันทึก (คงเดิม) ---
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

# --- TAB 2: กระเป๋า (คงเดิม) ---
with tab2:
    st.markdown("### 🏦 ยอดคงเหลือ")
    c_w1, c_w2, c_w3 = st.columns(3)
    wallets_list = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w in enumerate(wallets_list):
        w_df = df[df['wallet'] == w] if not df.empty else pd.DataFrame()
        bal = w_df['income'].sum() - w_df['expense'].sum() - w_df['savings'].sum() if not w_df.empty else 0.0
        [c_w1, c_w2, c_w3][i].metric(w, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ (Update: Achievement Cards & Vertical Charts) ---
with tab3:
    st.markdown("### 📊 วิเคราะห์และเหรียญตรา")
    if not df.empty:
        # ส่วนที่ 2 & 3: เปลี่ยนเป็น Achievement Badges
        st.markdown("#### 🏆 เหรียญตราทาสแมวประจำเดือน")
        col_ach1, col_ach2, col_ach3 = st.columns(3)
        
        # ค้นหาหมวดหมู่ที่ใช้จ่ายมากที่สุด
        exp_df = df[df['expense'] > 0]
        top_exp_cat = exp_df.groupby('category')['expense'].sum().idxmax() if not exp_df.empty else "ไม่มีข้อมูล"
        top_exp_amt = exp_df.groupby('category')['expense'].sum().max() if not exp_df.empty else 0
        
        # ค้นหาแหล่งรายรับหลัก
        inc_df = df[df['income'] > 0]
        top_inc_cat = inc_df.groupby('category')['income'].sum().idxmax() if not inc_df.empty else "ไม่มีข้อมูล"
        
        with col_ach1:
            st.markdown(f"""<div class='badge-card'><div class='badge-icon'>🍛</div><div class='badge-title'>นักชิมอันดับหนึ่ง</div><p class='badge-desc'>เน้นจ่ายหนักที่ <b>{top_exp_cat}</b><br>รวม {top_exp_amt:,.0f} ฿</p></div>""", unsafe_allow_html=True)
        with col_ach2:
            st.markdown(f"""<div class='badge-card'><div class='badge-icon'>💎</div><div class='badge-title'>แหล่งเงินถุงเงินถัง</div><p class='badge-desc'>รายรับหลักมาจาก <b>{top_inc_cat}</b><br>ยอดเยี่ยมมากเมี๊ยว!</p></div>""", unsafe_allow_html=True)
        with col_ach3:
            sav_pct = (total_save / total_in * 100) if total_in > 0 else 0
            st.markdown(f"""<div class='badge-card'><div class='badge-icon'>🛡️</div><div class='badge-title'>ป้อมปราการเงินออม</div><p class='badge-desc'>ออมไปแล้ว <b>{sav_pct:.1f}%</b><br>จากรายรับทั้งหมด</p></div>""", unsafe_allow_html=True)

        st.markdown("---")
        
        # กราฟแท่ง (คงเดิม)
        st.markdown("#### 📈 เปรียบเทียบรายรับและรายจ่ายรายเดือน")
        monthly_df = df.groupby('เดือน')[['income', 'expense']].sum().reset_index()
        monthly_df = monthly_df.rename(columns={'income': 'รายรับ', 'expense': 'รายจ่าย'})
        fig_bar = px.bar(monthly_df, x='เดือน', y=['รายรับ', 'รายจ่าย'], 
                         barmode='group', color_discrete_map={'รายรับ': '#FFB7CE', 'รายจ่าย': '#94E1E1'})
        fig_bar.update_layout(font_family="Kanit", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

        # เรียงแผนภูมิวงกลมลงมาข้างล่างต่อกัน (คงเดิมแต่จัดแถว)
        st.markdown("#### 🍰 1. สัดส่วนการใช้จ่ายและเงินออม")
        fig_pie1 = px.pie(names=['รายจ่าย 💸', 'เงินออม 🐷'], values=[total_out, total_save], 
                         hole=0.5, color_discrete_sequence=['#FF9AA2', '#B2E2F2'])
        fig_pie1.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie1, use_container_width=True)

        st.markdown("#### 🍱 2. รายจ่ายแยกตามหมวดหมู่")
        if not exp_df.empty:
            cat_exp = exp_df.groupby('category')['expense'].sum().reset_index()
            fig_pie2 = px.pie(cat_exp, names='category', values='expense', 
                             hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie2.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie2, use_container_width=True)

        st.markdown("#### 💰 3. รายรับแยกตามหมวดหมู่")
        if not inc_df.empty:
            cat_inc = inc_df.groupby('category')['income'].sum().reset_index()
            fig_pie3 = px.pie(cat_inc, names='category', values='income', 
                             hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie3.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie3, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลให้วิเคราะห์เมี๊ยวว")

# --- TAB 4: การออม (คงเดิม) ---
with tab4:
    st.markdown("### 🎯 การออม (Saving Level Up)")
    st.metric("เงินออมสะสมทั้งหมด", f"{total_save:,.2f} ฿")
    st.write(f"ระดับปัจจุบัน: **{level_text}**")
    next_goal = 5000 if total_save < 5000 else 20000 if total_save < 20000 else 50000
    p_val = min(total_save / next_goal, 1.0)
    st.write(f"เป้าหมายต่อไป: {next_goal:,.0f} ฿")
    st.progress(p_val)

# --- TAB 5: ประวัติ (คงเดิม) ---
with tab5:
    st.markdown("### 📖 ประวัติและจัดการ")
    if not df.empty:
        df_display = df.sort_values(by='id', ascending=False)
        st.dataframe(df_display.drop(columns=['user_id', 'เดือน']), use_container_width=True)
        selected_id = st.selectbox("เลือก ID รายการที่ต้องการลบ:", df_display['id'].tolist())
        if st.button("🗑️ ลบรายการ", use_container_width=True):
            c.execute("DELETE FROM records WHERE id=?", (selected_id,))
            conn.commit()
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลเมี๊ยวว")

st.markdown("---")
if st.button("🚪 ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
