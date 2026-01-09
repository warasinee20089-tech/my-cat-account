import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

# --- 1. ตั้งค่าหน้าเว็บ (บรรทัดแรกสุด) ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐱", layout="wide")

# ชื่อไฟล์ฐานข้อมูล
DATA_FILE = "transactions.csv"

# --- 2. ระบบจัดการข้อมูล (Load/Save) ---
def load_data():
    """โหลดข้อมูลจาก CSV ถ้าไม่มีไฟล์ให้สร้างใหม่"""
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["วันที่", "หมวดหมู่", "ประเภท", "จำนวนเงิน", "หมายเหตุ"])
    else:
        return pd.DataFrame(columns=["วันที่", "หมวดหมู่", "ประเภท", "จำนวนเงิน", "หมายเหตุ"])

def save_record(date, category, tx_type, amount, note):
    """บันทึกข้อมูลลง CSV"""
    df = load_data()
    new_data = pd.DataFrame([{
        "วันที่": date,
        "หมวดหมู่": category,
        "ประเภท": tx_type,
        "จำนวนเงิน": float(amount),
        "หมายเหตุ": note
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- 3. ระบบ Login ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def check_login():
    # >>> แก้รหัสผ่านตรงนี้ <<<
    if st.session_state.user_input == "admin" and st.session_state.pass_input == "1234":
        st.session_state['logged_in'] = True
    else:
        st.error("❌ รหัสผ่านไม่ถูกต้อง")

def logout_user():
    st.session_state['logged_in'] = False
    st.rerun()

# --- 4. ส่วนแสดงผลหลัก (Main UI) ---

if not st.session_state['logged_in']:
    # === หน้าจอ Login ===
    st.title("🔐 เข้าสู่ระบบบัญชี")
    st.write("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.text_input("Username", key="user_input")
        st.text_input("Password", type="password", key="pass_input")
        st.button("Login", on_click=check_login)

else:
    # === เข้าสู่ระบบสำเร็จ ===
    
    # Sidebar
    with st.sidebar:
        st.header("🐱 เมนู")
        st.write("สวัสดี, Admin")
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()

    st.title("🐱 กระเป๋าเงินเหมียว")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📝 บันทึก", "📋 ประวัติ", "📊 สรุปยอด"])

    # --- TAB 1: บันทึกรายการ ---
    with tab1:
        st.subheader("เพิ่มรายการใหม่")
        
        col1, col2 = st.columns(2)
        with col1:
            tx_date = st.date_input("วันที่", value=datetime.date.today())
        with col2:
            tx_type = st.radio("ประเภท:", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)

        st.write("---")
        
        # ฟังก์ชันเลือกหมวด หรือ พิมพ์เอง
        mode = st.radio("วิธีการระบุหมวด:", ["เลือกจากรายการ", "พิมพ์เอง"], horizontal=True)
        
        category = ""
        if mode == "เลือกจากรายการ":
            if tx_type == "เงินออม 🐷":
                opts = ["หยอดกระปุก", "ฝากธนาคาร", "กองทุน", "ทองคำ", "สลากออมสิน"]
            elif tx_type == "รายรับ 💰":
                opts = ["เงินเดือน", "โบนัส", "ขายของ", "เงินคืน", "อื่นๆ"]
            else:
                opts = ["อาหาร", "เดินทาง", "ของใช้", "ค่าห้อง", "น้ำ/ไฟ/เน็ต", "ช้อปปิ้ง", "รักษาพยาบาล", "อื่นๆ"]
            category = st.selectbox("เลือกหมวดหมู่:", opts)
        else:
            category = st.text_input("ระบุชื่อหมวดเอง:", placeholder="เช่น ค่าเน็ต, อาหารแมว")

        c3, c4 = st.columns(2)
        with c3:
            amount = st.number_input("จำนวนเงิน:", min_value=0.0, format="%.2f")
        with c4:
            note = st.text_input("หมายเหตุ:", placeholder="...")

        if st.button("❤️ บันทึกรายการ", use_container_width=True):
            if not category:
                st.error("⚠️ กรุณาระบุหมวดหมู่")
            elif amount <= 0:
                st.warning("⚠️ ยอดเงินต้องมากกว่า 0")
            else:
                save_record(tx_date, category, tx_type, amount, note)
                st.success(f"บันทึก '{category}' เรียบร้อย!")
                st.rerun()

    # --- TAB 2: ประวัติ ---
    with tab2:
        st.subheader("รายการย้อนหลัง")
        df = load_data()
        if not df.empty:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            
            st.write("---")
            if st.checkbox("ต้องการลบข้อมูลทั้งหมด?"):
                if st.button("ยืนยันลบข้อมูล (Reset)"):
                    if os.path.exists(DATA_FILE):
                        os.remove(DATA_FILE)
                        st.success("ล้างข้อมูลเรียบร้อย")
                        st.rerun()
        else:
            st.info("ยังไม่มีข้อมูล")

    # --- TAB 3: สรุปยอด ---
    with tab3:
        st.subheader("📊 ภาพรวมการเงิน")
        df = load_data()
        
        if not df.empty:
            inc = df[df["ประเภท"]=="รายรับ 💰"]["จำนวนเงิน"].sum()
            exp = df[df["ประเภท"]=="รายจ่าย 💸"]["จำนวนเงิน"].sum()
            sav = df[df["ประเภท"]=="เงินออม 🐷"]["จำนวนเงิน"].sum()
            
            c_a, c_b, c_c = st.columns(3)
            c_a.metric("รายรับ", f"{inc:,.2f}")
            c_b.metric("รายจ่าย", f"{exp:,.2f}")
            c_c.metric("เงินออม", f"{sav:,.2f}")
            
            st.divider()
            
            # กราฟวงกลม
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("**สัดส่วนการใช้เงิน**")
                sum_type = df.groupby("ประเภท")["จำนวนเงิน"].sum()
                if not sum_type.empty:
                    fig, ax = plt.subplots()
                    ax.pie(sum_type, labels=sum_type.index, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
            
            with col_chart2:
                st.write("**รายจ่ายหมดไปกับอะไร?**")
                exp_only = df[df["ประเภท"]=="รายจ่าย 💸"]
                if not exp_only.empty:
                    sum_exp = exp_only.groupby("หมวดหมู่")["จำนวนเงิน"].sum()
                    fig2, ax2 = plt.subplots()
                    ax2.pie(sum_exp, labels=sum_exp.index, autopct='%1.1f%%')
                    ax2.axis('equal')
                    st.pyplot(fig2)
                else:
                    st.info("ไม่มีรายการรายจ่าย")

        else:
            st.info("บันทึกข้อมูลก่อนนะครับ กราฟถึงจะขึ้น")
