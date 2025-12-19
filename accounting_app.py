import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- การตั้งค่าหน้าเว็บโทน Pastel & Cat Theme ---
st.set_page_config(page_title="Meow Accounting", layout="wide", page_icon="🐱")

st.markdown("""
    <style>
    /* พื้นหลังพาสเทล */
    .main { background-color: #FFF5F7; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #FFD1DC; }
    
    /* ปุ่มกดสีชมพูพาสเทล */
    .stButton>button { 
        background-color: #FFB7C5; color: white; border-radius: 20px; 
        font-weight: bold; width: 100%; border: none;
    }
    .stButton>button:hover { background-color: #FFC0CB; color: white; }
    
    /* กล่องหัวข้อไอคอนแมว */
    .record-box { 
        background-color: #FFD1DC; color: #D87093; padding: 15px; 
        border-radius: 20px; text-align: center; font-weight: bold; margin-bottom: 10px;
        border: 2px dashed #FFB7C5;
    }
    
    /* กล่องสรุปยอด */
    [data-testid="stMetric"] { 
        background-color: #FFFFFF; padding: 15px; border-radius: 20px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-bottom: 5px solid #FFB7C5;
    }
    
    h1 { color: #D87093; text-align: center; font-family: 'Tahoma'; }
    .stTable { background-color: white; border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบฐานข้อมูล ---
conn = sqlite3.connect('wallet_pastel.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS my_records (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, desc TEXT, income REAL DEFAULT 0, expense REAL DEFAULT 0, is_debt INTEGER DEFAULT 0)''')
conn.commit()

# --- เมนูหลัก ---
st.sidebar.markdown("<h1 style='font-size: 50px; text-align: center;'>🐱</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #D87093;'>Meow Menu</h3>", unsafe_allow_html=True)
menu = st.sidebar.radio("", ["🐾 บันทึกรายรับ รายจ่าย", "📊 สรุปยอด Meow", "💰 หนี้สิน"])

if menu == "🐾 บันทึกรายรับ รายจ่าย":
    st.markdown("<h1>🌸 บันทึกรายรับ รายจ่าย 🌸</h1>", unsafe_allow_html=True)
    st.markdown("<div class='record-box'>🐱 กรอกรายการใหม่ตรงนี้เมี๊ยววว</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
    with col1: d_in = st.date_input("วันที่", datetime.now())
    with col2: desc_in = st.text_input("รายการ (เช่น ค่าปลาทู)")
    with col3: type_in = st.selectbox("ประเภท", ["รายจ่าย", "รายรับ", "หนี้สิน"])
    with col4: amt_in = st.number_input("จำนวนเงิน (฿)", min_value=0.0)
    
    if st.button("🐾 บันทึกรายการ"):
        if desc_in and amt_in > 0:
            inc, exp, debt = (amt_in, 0, 0) if type_in == "รายรับ" else (0, amt_in, 0) if type_in == "รายจ่าย" else (amt_in, 0, 1)
            c.execute("INSERT INTO my_records (date, desc, income, expense, is_debt) VALUES (?,?,?,?,?)", (d_in.strftime('%Y-%m-%d'), desc_in, inc, exp, debt))
            conn.commit()
            st.success("บันทึกสำเร็จแล้วเมี๊ยวว! ✨")
            st.rerun()

    st.write("---")
    st.markdown("### 📋 ช่องรายการ")
    
    df_display = pd.read_sql("SELECT id, date as วันที่, desc as รายการ, income as รายรับ, expense as รายจ่าย FROM my_records ORDER BY id ASC", conn)
    
    if not df_display.empty:
        df_display['คงเหลือ'] = df_display['รายรับ'].cumsum() - df_display['รายจ่าย'].cumsum()
        df_latest = df_display.sort_values(by='id', ascending=False).head(10)
        st.table(df_latest[['วันที่', 'รายการ', 'รายรับ', 'รายจ่าย', 'คงเหลือ']])
        
        with st.expander("🛠️ แก้ไข หรือ ลบ รายการ (คลิกตรงนี้)"):
            for i, r in df_latest.iterrows():
                col_info, col_edit, col_del = st.columns([4, 4, 2])
                col_info.write(f"🐱 {r['วันที่']} : {r['รายการ']}")
                new_name = col_edit.text_input("แก้ชื่อ", r['รายการ'], key=f"edit_{r['id']}")
                if col_edit.button("✅ ยืนยัน", key=f"btn_up_{r['id']}"):
                    c.execute("UPDATE my_records SET desc=? WHERE id=?", (new_name, r['id']))
                    conn.commit()
                    st.rerun()
                if col_del.button("🗑️ ลบ", key=f"btn_del_{r['id']}"):
                    c.execute("DELETE FROM my_records WHERE id=?", (r['id'],))
                    conn.commit()
                    st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลในช่องรายการเลยเมี๊ยวว")

elif menu == "📊 สรุปยอด Meow":
    st.markdown("<h1>📈 สรุปภาพรวมเมี๊ยวว</h1>", unsafe_allow_html=True)
    df = pd.read_sql("SELECT * FROM my_records", conn)
    if not df.empty:
        t_inc, t_exp = df['income'].sum(), df['expense'].sum()
        m1, m2, m3 = st.columns(3)
        m1.metric("🐾 รายรับรวม", f"{t_inc:,.2f} ฿")
        m2.metric("🐟 รายจ่ายรวม", f"-{t_exp:,.2f} ฿")
        m3.metric("💰 คงเหลือ", f"{t_inc-t_exp:,.2f} ฿")
        
        df['date'] = pd.to_datetime(df['date'])
        chart_df = df.groupby(df['date'].dt.strftime('%B'))[['income','expense']].sum().reset_index()
        fig = px.bar(chart_df, x='date', y=['income','expense'], barmode='group', 
                     color_discrete_sequence=['#FFB7C5', '#98FB98'], title="กราฟรายรับ-รายจ่าย")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("<h1>💰 รายการหนี้สิน</h1>", unsafe_allow_html=True)
    df_d = pd.read_sql("SELECT date as วันที่, desc as รายการ, income as จำนวนหนี้ FROM my_records WHERE is_debt=1", conn)
    if not df_d.empty:
        st.table(df_d)
    else:
        st.success("ไม่มีหนี้สิน สบายใจจังเมี๊ยวว! ✨")