import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Meow Wallet v.53", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500&display=swap');
    .stApp { background-color: #FFF0F5 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, label { 
        font-family: 'Kanit', sans-serif !important; color: #4A4A4A !important;
    }
    .main-title { color: #FFB7CE; text-align: center; font-size: 40px; font-weight: bold; padding: 10px; }
    .meow-card { background: white; border-radius: 20px; padding: 15px; border: 2px solid #FFE4E1; margin-bottom: 15px; }
    .stButton>button { border-radius: 10px; background-color: #FFB7CE; color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect('meow_flexible_v53.db', check_same_thread=False)
    c = conn.cursor()
    # ตารางรายการ
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, 
                  wallet TEXT, category TEXT, sub_category TEXT,
                  income REAL DEFAULT 0, expense REAL DEFAULT 0, savings REAL DEFAULT 0,
                  receipt_img BLOB)''')
    # ตารางเป้าหมาย (รองรับหลายรายการ)
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, goal_name TEXT, goal_amount REAL)''')
    # ตารางหมวดหมู่ที่ผู้ใช้สร้างเอง
    c.execute('''CREATE TABLE IF NOT EXISTS custom_categories 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT, name TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>🐾 Meow Wallet 🐾</div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>🐱</h1>", unsafe_allow_html=True)
        name_in = st.text_input("ชื่อทาสแมว:", placeholder="พิมพ์ชื่อเพื่อเข้าสู่ระบบ...")
        if st.button("เข้าสู่ระบบ 🐾", use_container_width=True):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

user_name = st.session_state.user_name

# --- 4. LOAD DATA ---
df = pd.read_sql(f"SELECT * FROM records WHERE user_id='{user_name}'", conn)
if not df.empty:
    df['date'] = pd.to_datetime(df['date'])

# ดึงยอดเงินออมรวมเพื่อคำนวณเป้าหมาย
total_save = df['savings'].sum() if not df.empty else 0

# --- 5. HEADER ---
st.markdown(f"<div class='main-title'>🐾 Meow Wallet: {user_name} 🐾</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 บันทึกรายวัน", "🏦 กระเป๋าเงิน", "📊 วิเคราะห์", "🎯 เป้าหมาย", "📖 ประวัติ/แก้ไข"])

# --- TAB 1: บันทึก ---
with tab1:
    st.markdown("### ✨ เพิ่มรายการใหม่")
    col1, col2 = st.columns(2)
    with col1:
        d_in = st.date_input("📅 วันที่", datetime.now())
        w_in = st.selectbox("👛 ช่องทาง", ["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"])
        t_in = st.radio("🏷️ ประเภท", ["รายรับ 💰", "รายจ่าย 💸", "เงินออม 🐷"], horizontal=True)
        up_file = st.file_uploader("📸 แนบใบเสร็จ (ไม่บังคับ)", type=['jpg', 'jpeg', 'png'], key="add_img")
    
    with col2:
        # ระบบจัดการหมวดหมู่เอง
        db_cats = pd.read_sql(f"SELECT name FROM custom_categories WHERE user_id='{user_name}' AND type='{t_in}'", conn)['name'].tolist()
        default_cats = ["เงินเดือน", "อาหาร", "เดินทาง", "ช้อปปิ้ง", "ออมเงิน"]
        all_cats = list(set(default_cats + db_cats))
        
        selected_cat = st.selectbox("📁 เลือกหมวดหมู่", all_cats + ["+ เพิ่มหมวดหมู่ใหม่"])
        
        if selected_cat == "+ เพิ่มหมวดหมู่ใหม่":
            new_cat_name = st.text_input("✍️ ระบุชื่อหมวดหมู่ใหม่")
            if st.button("💾 บันทึกหมวดหมู่"):
                conn.execute("INSERT INTO custom_categories (user_id, type, name) VALUES (?,?,?)", (user_name, t_in, new_cat_name))
                conn.commit()
                st.rerun()
            final_cat = new_cat_name
        else:
            final_cat = selected_cat

        s_detail = st.text_input("📝 รายละเอียดเพิ่มเติม")
        s_amt = st.number_input("💵 จำนวนเงิน", min_value=0.0, step=1.0)

    if st.button("💖 บันทึกรายการ"):
        if s_amt > 0 and final_cat:
            img_data = up_file.getvalue() if up_file else None
            inc = s_amt if t_in == "รายรับ 💰" else 0
            exp = s_amt if t_in == "รายจ่าย 💸" else 0
            sav = s_amt if t_in == "เงินออม 🐷" else 0
            conn.execute("INSERT INTO records (user_id, date, wallet, category, sub_category, income, expense, savings, receipt_img) VALUES (?,?,?,?,?,?,?,?,?)", 
                         (user_name, d_in.strftime('%Y-%m-%d'), w_in, final_cat, s_detail, inc, exp, sav, img_data))
            conn.commit(); st.rerun()

# --- TAB 2: กระเป๋าเงิน ---
with tab2:
    st.markdown("### 🏦 ยอดเงินคงเหลือ")
    w_cols = st.columns(3)
    for i, w_n in enumerate(["เงินสด 💵", "เงินฝากธนาคาร 🏦", "บัตรเครดิต 💳"]):
        bal = 0
        if not df.empty:
            w_df = df[df['wallet'] == w_n]
            bal = w_df['income'].sum() - (w_df['expense'].sum() + w_df['savings'].sum())
        w_cols[i].metric(w_n, f"{bal:,.2f} ฿")

# --- TAB 3: วิเคราะห์ (ปรับกราฟตามคำขอ) ---
with tab3:
    st.markdown("### 📊 วิเคราะห์การเงิน")
    if not df.empty:
        # กราฟแท่งภาษาไทย + ปรับระยะแกนให้แคบลงเพื่อให้มองง่าย
        st.markdown("#### 📅 เปรียบเทียบรายรับและรายจ่ายรายเดือน")
        df['เดือน'] = df['date'].dt.strftime('%m/%Y')
        m_data = df.groupby('เดือน')[['income', 'expense']].sum().reset_index()
        m_data = m_data.rename(columns={'income': 'รายรับ', 'expense': 'รายจ่าย'})
        
        fig_bar = px.bar(m_data, x='เดือน', y=['รายรับ', 'รายจ่าย'], barmode='group',
                         color_discrete_map={'รายรับ':'#FFB7CE','รายจ่าย':'#B2E2F2'},
                         labels={'value': 'จำนวนเงิน (บาท)', 'variable': 'ประเภท'})
        
        # ปรับแกน Y ให้แคบลงโดยอิงจากค่าสูงสุดที่มี เพื่อให้กราฟดูเด่นชัดขึ้น
        max_val = max(m_data['รายรับ'].max(), m_data['รายจ่าย'].max())
        fig_bar.update_layout(yaxis=dict(range=[0, max_val * 1.1]), font_family="Kanit")
        st.plotly_chart(fig_bar, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 💰 รายรับแยกตามหมวดหมู่")
            inc_df = df[df['income'] > 0]
            if not inc_df.empty:
                st.plotly_chart(px.pie(inc_df, values='income', names='category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        with c2:
            st.markdown("#### 🍱 รายจ่ายแยกตามหมวดหมู่")
            exp_df = df[df['expense'] > 0]
            if not exp_df.empty:
                st.plotly_chart(px.pie(exp_df, values='expense', names='category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe), use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลเมี๊ยว")

# --- TAB 4: เป้าหมาย (รองรับหลายรายการ/แก้ไข/ลบ) ---
with tab4:
    st.markdown("### 🎯 จัดการเป้าหมายการออม")
    col_g1, col_g2 = st.columns([1, 2])
    
    with col_g1:
        st.markdown("#### ✨ เพิ่มเป้าหมายใหม่")
        gn = st.text_input("ชื่อเป้าหมาย")
        ga = st.number_input("จำนวนเงินที่ต้องการ", min_value=0.0)
        if st.button("🚩 เพิ่มเป้าหมาย"):
            conn.execute("INSERT INTO goals (user_id, goal_name, goal_amount) VALUES (?,?,?)", (user_name, gn, ga))
            conn.commit(); st.rerun()

    with col_g2:
        st.markdown("#### 🏆 รายการเป้าหมายของคุณ")
        goals_df = pd.read_sql(f"SELECT * FROM goals WHERE user_id='{user_name}'", conn)
        if not goals_df.empty:
            for index, row in goals_df.iterrows():
                with st.expander(f"📌 {row['goal_name']} - {row['goal_amount']:,.0f} ฿"):
                    p = min(total_save / row['goal_amount'], 1.0) if row['goal_amount'] > 0 else 0
                    st.progress(p)
                    st.write(f"เก็บได้แล้ว {total_save:,.2f} / {row['goal_amount']:,.2f} ฿ ({(p*100):.1f}%)")
                    
                    c_edit1, c_edit2 = st.columns(2)
                    if c_edit1.button("🗑️ ลบเป้าหมาย", key=f"del_g_{row['id']}"):
                        conn.execute("DELETE FROM goals WHERE id=?", (row['id'],))
                        conn.commit(); st.rerun()
                    # (สามารถขยายส่วนแก้ไขชื่อ/ยอดเงินได้ที่นี่)
        else: st.write("ยังไม่มีเป้าหมาย")

# --- TAB 5: ประวัติ (แก้ไขได้ทุกส่วนรวมถึงใบเสร็จ) ---
with tab5:
    st.markdown("### 📖 ประวัติและแก้ไขข้อมูล")
    if not df.empty:
        df_sh = df.sort_values(by='id', ascending=False)
        st.dataframe(df_sh.drop(columns=['user_id', 'receipt_img']), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### ✏️ แก้ไขรายการ")
        sel_id = st.selectbox("เลือก ID รายการที่ต้องการจัดการ:", df_sh['id'].tolist())
        target = df[df['id'] == sel_id].iloc[0]
        
        with st.form(f"edit_form_{sel_id}"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_date = st.date_input("แก้ไขวันที่", pd.to_datetime(target['date']))
                e_cat = st.text_input("แก้ไขหมวดหมู่", value=target['category'])
                e_amt = st.number_input("แก้ไขยอดเงิน", value=float(max(target['income'], target['expense'], target['savings'])))
            with col_e2:
                e_sub = st.text_input("แก้ไขรายละเอียด", value=target['sub_category'])
                e_img = st.file_uploader("เปลี่ยนรูปใบเสร็จ", type=['jpg','png'])
                if target['receipt_img']:
                    st.image(target['receipt_img'], width=150, caption="รูปเดิม")
            
            submit_edit = st.form_submit_button("✅ ยืนยันการแก้ไขข้อมูล")
            if submit_edit:
                # ตรวจสอบประเภท
                ni = e_amt if target['income'] > 0 else 0
                ne = e_amt if target['expense'] > 0 else 0
                ns = e_amt if target['savings'] > 0 else 0
                
                if e_img: # ถ้ามีการอัปโหลดรูปใหม่
                    conn.execute("UPDATE records SET date=?, category=?, income=?, expense=?, savings=?, sub_category=?, receipt_img=? WHERE id=?", 
                                 (e_date.strftime('%Y-%m-%d'), e_cat, ni, ne, ns, e_sub, e_img.getvalue(), sel_id))
                else:
                    conn.execute("UPDATE records SET date=?, category=?, income=?, expense=?, savings=?, sub_category=? WHERE id=?", 
                                 (e_date.strftime('%Y-%m-%d'), e_cat, ni, ne, ns, e_sub, sel_id))
                conn.commit(); st.rerun()
        
        if st.button("🗑️ ลบรายการนี้ถาวร"):
            conn.execute("DELETE FROM records WHERE id=?", (sel_id,))
            conn.commit(); st.rerun()
