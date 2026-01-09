import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว V.2", page_icon="🐱", layout="wide")

# ตกแต่ง CSS ให้ดูน่ารักขึ้น
st.markdown("""
<style>
    .stApp {background-color: #f0f2f6;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
    h1 {color: #ff6f61;}
    h2, h3 {color: #4b4b4b;}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "transactions.csv"

# --- 2. ระบบจัดการข้อมูล ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["วันที่", "หมวดหมู่", "ประเภท", "จำนวนเงิน", "หมายเหตุ"])
    else:
        return pd.DataFrame(columns=["วันที่", "หมวดหมู่", "ประเภท", "จำนวนเงิน", "หมายเหตุ"])

def save_record(date, category, tx_type, amount, note):
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
    if st.session_state.user_input == "admin" and st.session_state.pass_input == "1234":
        st.session_state['logged_in'] = True
    else:
        st.error("❌ รหัสผ่านผิด! ลองใหม่นะเหมียว")

def logout_user():
    st.session_state['logged_in'] = False
    st.rerun()

# --- 4. ส่วนแสดงผลหลัก ---
if not st.session_state['logged_in']:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔐 เข้าสู่ระบบ")
        st.info("Username: admin | Password: 1234")
        st.text_input("Username", key="user_input")
        st.text_input("Password", type="password", key="pass_input")
        st.button("🚀 Login", on_click=check_login, use_container_width=True)

else:
    with st.sidebar:
        st.title("🐱 เมนูเหมียว")
        st.write(f"สวัสดีคุณ Admin! วันนี้เหนื่อยไหม?")
        st.write("---")
        
        # ปุ่มดาวน์โหลดไฟล์ CSV
        df = load_data()
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูล (CSV)",
            data=csv,
            file_name='my_cat_wallet.csv',
            mime='text/csv',
            use_container_width=True
        )
        
        st.write("---")
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()

    st.title("🐱 กระเป๋าเงินเหมียว (Cat Wallet)")

    tab1, tab2, tab3 = st.tabs(["📝 จดบันทึก", "📋 ประวัติ", "📊 แดชบอร์ด"])

    # --- TAB 1: จดบันทึก ---
    with tab1:
        with st.container(border=True):
            st.subheader("📌 เพิ่มรายการใหม่")
            c1, c2 = st.columns(2)
            with c1:
                tx_date = st.date_input("วันที่", value=datetime.date.today())
            with c2:
                tx_type = st.radio("ประเภท:", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)

            # หมวดหมู่
            category_options = {
                "รายจ่าย 💸": ["อาหาร", "เดินทาง", "ของใช้", "แมว/สัตว์เลี้ยง", "ค่าห้อง/น้ำ/ไฟ", "ช้อปปิ้ง", "อื่นๆ"],
                "รายรับ 💰": ["เงินเดือน", "โบนัส", "ขายของ", "อื่นๆ"],
                "เงินออม 🐷": ["กระปุกหมู", "ฝากธนาคาร", "ลงทุน", "ทองคำ"]
            }
            
            c3, c4 = st.columns([1, 1])
            with c3:
                use_manual = st.checkbox("พิมพ์หมวดหมู่เอง")
            
            if use_manual:
                category = st.text_input("ระบุชื่อหมวด:", placeholder="เช่น ชานมไข่มุก")
            else:
                current_opts = category_options.get(tx_type, ["อื่นๆ"])
                category = st.selectbox("เลือกหมวดหมู่:", current_opts)

            c5, c6 = st.columns(2)
            with c5:
                amount = st.number_input("จำนวนเงิน (บาท):", min_value=0.0, format="%.2f", step=10.0)
            with c6:
                note = st.text_input("หมายเหตุ (กันลืม):", placeholder="...")

            if st.button("✅ บันทึกข้อมูล", use_container_width=True, type="primary"):
                if not category:
                    st.error("⚠️ ลืมใส่หมวดหมู่รึเปล่า?")
                elif amount <= 0:
                    st.warning("⚠️ ยอดเงินต้องมากกว่า 0 นะ")
                else:
                    save_record(tx_date, category, tx_type, amount, note)
                    st.success(f"บันทึกเรียบร้อย! พักผ่อนได้!")
                    st.rerun()

    # --- TAB 2: ประวัติ ---
    with tab2:
        st.subheader("📜 รายการย้อนหลัง")
        df = load_data()
        if not df.empty:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            if st.button("🗑️ ล้างข้อมูลทั้งหมด (Reset)", type="secondary"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                    st.success("ล้างข้อมูลเกลี้ยงแล้ว!")
                    st.rerun()
        else:
            st.info("ยังไม่มีข้อมูล เริ่มจดเลย!")

    # --- TAB 3: สรุปยอด ---
    with tab3:
        st.subheader("📈 สรุปสถานะการเงิน")
        df = load_data()
        
        if not df.empty:
            inc = df[df["ประเภท"]=="รายรับ 💰"]["จำนวนเงิน"].sum()
            exp = df[df["ประเภท"]=="รายจ่าย 💸"]["จำนวนเงิน"].sum()
            sav = df[df["ประเภท"]=="เงินออม 🐷"]["จำนวนเงิน"].sum()
            balance = inc - exp - sav # สมมติเงินคงเหลือหักออมด้วย หรือปรับตามสูตรที่ชอบ

            c_a, c_b, c_c, c_d = st.columns(4)
            c_a.metric("💰 รายรับ", f"{inc:,.0f}")
            c_b.metric("💸 รายจ่าย", f"{exp:,.0f}", delta=f"-{exp:,.0f}", delta_color="inverse")
            c_c.metric("🐷 เงินออม", f"{sav:,.0f}", delta=f"+{sav:,.0f}")
            c_d.metric("💎 คงเหลือใช้", f"{balance:,.0f}")
            
            st.divider()

            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("##### 🍰 สัดส่วน รายรับ-รายจ่าย-ออม")
                sum_type = df.groupby("ประเภท")["จำนวนเงิน"].sum()
                if not sum_type.empty:
                    fig, ax = plt.subplots(figsize=(4, 4))
                    ax.pie(sum_type, labels=sum_type.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
                    st.pyplot(fig)

            with col_chart2:
                st.write("##### 💸 หมดเงินไปกับอะไรเยอะสุด?")
                exp_only = df[df["ประเภท"]=="รายจ่าย 💸"]
                if not exp_only.empty:
                    sum_exp = exp_only.groupby("หมวดหมู่")["จำนวนเงิน"].sum().sort_values(ascending=False).head(5)
                    st.bar_chart(sum_exp)
                else:
                    st.info("ยังไม่มีรายจ่าย (เก่งมาก!)")
        else:
            st.warning("จดข้อมูลก่อนนะ กราฟถึงจะมา")
