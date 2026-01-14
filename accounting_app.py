import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Meow Wallet Pro", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; }
    .meow-card { background: white; border-radius: 15px; padding: 20px; border: 2px solid #FFE4E1; margin-bottom: 20px; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('meow_pro_v53.db', check_same_thread=False)
    c = conn.cursor()
    # ตารางบันทึก
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                  wallet TEXT, category TEXT, sub_category TEXT,
                  income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                  receipt_img BLOB)''')
    # ตารางเป้าหมาย (รองรับหลายเป้าหมาย)
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, goal_name TEXT, goal_amount REAL)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="พิมพ์ชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾"):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
user_name = st.session_state.user_name
raw_df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
if not raw_df.empty:
    raw_df['date'] = pd.to_datetime(raw_df['date'])
    df = raw_df.dropna(subset=['date']).copy()
else:
    df = pd.DataFrame()

# --- 5. UI TABS ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึก", "🏦 กระเป๋า", "📊 วิเคราะห์", "🎯 เป้าหมาย", "📖 ประวัติและแก้ไข"])

# --- TAB 1: บันทึก ---
with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    ca, cb = st.columns(2)
    with ca:
        d_in = st.date_input("📅 วันที่", datetime.now())
        w_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        t_in = st.radio("🏷️ ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)
        up_file = st.file_uploader("📸 แนบใบเสร็จ", type=['jpg', 'jpeg', 'png'])
    with cb:
        c_map = {
            "รายรับ 💰": ["เงินเดือน 💸", "โบนัส 🎁", "ขายของ 🛍️", "ระบุเอง ✍️"],
            "รายจ่าย 💸": ["ค่าอาหาร 🍱", "เดินทาง 🚗", "ช้อปปิ้ง 🛒", "ระบุเอง ✍️"],
            "เงินออม 🐷": ["ออมทั่วไป 🏦", "ออมฉุกเฉิน 🚑", "ระบุเอง ✍️"]
        }
        s_cat = st.selectbox("📁 หมวดหมู่", c_map[t_in])
        final_cat = st.text_input("📝 ระบุหมวดหมู่เอง") if s_cat == "ระบุเอง ✍️" else s_cat
        s_detail = st.text_input("🔍 รายละเอียด")
        s_amt = st.number_input("💵 จำนวนเงิน", min_value=0.0)
    
    if st.button("💖 บันทึกรายการ"):
        if s_amt > 0 and final_cat:
            img = up_file.getvalue() if up_file else None
            inc = s_amt if t_in == "รายรับ 💰" else 0
            exp = s_amt if t_in == "รายจ่าย 💸" else 0
            sav = s_amt if t_in == "เงินออม 🐷" else 0
            conn.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                         (user_name, d_in.strftime('%Y-%m-%d'), w_in, final_cat, s_detail, inc, exp, sav, img))
            conn.commit(); st.rerun()

# --- TAB 2: กระเป๋าเงิน ---
with tab2:
    st.markdown("### 🏦 ยอดเงินคงเหลือ")
    w_cols = st.columns(3)
    wallets = ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]
    for i, w_name in enumerate(wallets):
        bal = df[df['wallet'] == w_name].apply(lambda x: x['income'] - x['expense'] - x['savings'], axis=1).sum() if not df.empty else 0
        w_cols[i].metric(w_name, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ ---
with tab3:
    st.markdown("### 📊 วิเคราะห์และกราฟ")
    if not df.empty:
        # 1. กราฟแท่ง (ปรับสเกลให้แคบลงอัตโนมัติ)
        df['Month-Year'] = df['date'].dt.strftime('%m/%Y')
        m_df = df.groupby('Month-Year')[['income', 'expense']].sum().reset_index()
        m_df = m_df.rename(columns={'income': 'รายรับ', 'expense': 'รายจ่าย', 'Month-Year': 'เดือน/ปี'})
        
        fig_bar = px.bar(m_df, x='เดือน/ปี', y=['รายรับ', 'รายจ่าย'], barmode='group', 
                         color_discrete_map={'รายรับ':'#FFB7CE','รายจ่าย':'#B2E2F2'})
        fig_bar.update_layout(yaxis=dict(range=[0, max(m_df['รายรับ'].max(), m_df['รายจ่าย'].max()) * 1.2])) # ปรับสเกลให้มองเห็นยอดน้อยๆ ได้ชัดขึ้น
        st.plotly_chart(fig_bar, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 💰 รายรับแยกหมวดหมู่")
            inc_df = df[df['income'] > 0]
            if not inc_df.empty:
                st.plotly_chart(px.pie(inc_df, values='income', names='category', hole=0.4), use_container_width=True)
        with c2:
            st.markdown("#### 🍱 รายจ่ายแยกหมวดหมู่")
            exp_df = df[df['expense'] > 0]
            if not exp_df.empty:
                st.plotly_chart(px.pie(exp_df, values='expense', names='category', hole=0.4), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

# --- TAB 4: เป้าหมาย (Multi-Goal) ---
with tab4:
    st.markdown("### 🎯 เป้าหมายชีวิตทาสแมว")
    g_col1, g_col2 = st.columns([1, 1.5])
    with g_col1:
        st.write("🚩 เพิ่มเป้าหมายใหม่")
        new_gn = st.text_input("ชื่อเป้าหมาย")
        new_ga = st.number_input("ยอดเงินเป้าหมาย", min_value=0.0, key="new_goal_amt")
        if st.button("➕ เพิ่มเป้าหมาย"):
            conn.execute("INSERT INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, new_gn, new_ga))
            conn.commit(); st.rerun()
    
    with g_col2:
        st.write("🏆 รายการเป้าหมาย")
        goals_df = pd.read_sql(f"SELECT * FROM goals WHERE user_id='{user_name}'", conn)
        total_save = df['savings'].sum() if not df.empty else 0
        for idx, row in goals_df.iterrows():
            with st.expander(f"📌 {row['goal_name']}"):
                prog = min(total_save / row['goal_amount'], 1.0) if row['goal_amount'] > 0 else 0
                st.progress(prog)
                st.write(f"เก็บได้แล้ว {total_save:,.0f} / {row['goal_amount']:,.0f} ฿ (สำเร็จ {prog*100:.1f}%)")
                
                ce1, ce2 = st.columns(2)
                if ce1.button("🗑️ ลบเป้าหมาย", key=f"del_g_{row['id']}"):
                    conn.execute("DELETE FROM goals WHERE id=?", (row['id'],))
                    conn.commit(); st.rerun()
                # (การแก้ไขเป้าหมายทำได้ผ่านการลบแล้วเพิ่มใหม่เพื่อความเสถียรของโค้ด)

# --- TAB 5: ประวัติและแก้ไข ---
with tab5:
    st.markdown("### 📖 ประวัติและแก้ไขรายการ")
    if not df.empty:
        df_sh = df.sort_values(by='id', ascending=False)
        st.dataframe(df_sh.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        st.markdown("---")
        sel_id = st.selectbox("เลือก ID รายการที่ต้องการแก้ไข/ลบ:", df_sh['id'].tolist())
        r = df[df['id'] == sel_id].iloc[0]
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            e_date = st.date_input("แก้ไขวัน", r['date'])
            e_amt = st.number_input("แก้ไขเงิน", value=float(max(r['income'], r['expense'], r['savings'])))
            e_img = st.file_uploader("อัปโหลดใบเสร็จใหม่", type=['jpg', 'png'])
        with col_e2:
            e_cat = st.text_input("แก้ไขหมวดหมู่", value=r['category'])
            e_sub = st.text_input("แก้ไขรายละเอียด", value=r['sub_category'])
            if r['receipt_img']: st.image(r['receipt_img'], width=200, caption="ใบเสร็จปัจจุบัน")

        b1, b2 = st.columns(2)
        if b1.button("✅ ยืนยันการแก้ไขทั้งหมด"):
            new_img = e_img.getvalue() if e_img else r['receipt_img']
            ni, ne, ns = (e_amt,0,0) if r['income']>0 else (0,e_amt,0) if r['expense']>0 else (0,0,e_amt)
            conn.execute("UPDATE records SET date=?, income=?, expense=?, savings=?, category=?, sub_category=?, receipt_img=? WHERE id=?", 
                         (e_date.strftime('%Y-%m-%d'), ni, ne, ns, e_cat, e_sub, new_img, sel_id))
            conn.commit(); st.success("แก้ไขข้อมูลแล้ว!"); st.rerun()
        
        if b2.button("🗑️ ลบรายการนี้ทิ้ง"):
            conn.execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.warning("ลบรายการแล้ว!"); st.rerun()

st.markdown("---")
if st.button("🚪 ออกจากระบบ"): st.session_state.logged_in = False; st.rerun()
