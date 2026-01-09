import streamlit as st
import pandas as pd
import os
import datetime
import altair as alt  # ใช้ตัวนี้แทน matplotlib (มีทุกเครื่อง ไม่เออเร่อแน่นอน)

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="กระเป๋าเงินเหมียว", page_icon="🐱", layout="wide")

DATA_FILE = "transactions.csv"

# --- 2. ฟังก์ชันจัดการข้อมูล ---
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
    # >>> รหัสผ่าน (แก้ตรงนี้) <<<
    if st.session_state.u_in == "admin" and st.session_state.p_in == "1234":
        st.session_state['logged_in'] = True
    else:
        st.error("❌ รหัสผิดครับ")

def logout_user():
    st.session_state['logged_in'] = False
    st.rerun()

# --- 4. หน้าจอหลัก ---

if not st.session_state['logged_in']:
    st.title("🔐 Login")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.text_input("Username", key="u_in")
        st.text_input("Password", type="password", key="p_in")
        st.button("เข้าสู่ระบบ", on_click=check_login)

else:
    # Sidebar
    with st.sidebar:
        st.write(f"สวัสดี Admin 🐱")
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()

    st.title("🐱 กระเป๋าเงินเหมียว")
    
    t1, t2, t3 = st.tabs(["📝 จดบันทึก", "📋 ประวัติ", "📊 สรุปกราฟ"])

    # === Tab 1: จดบันทึก ===
    with t1:
        st.subheader("จดรายการใหม่")
        d_col, t_col = st.columns(2)
        with d_col:
            tx_date = st.date_input("วันที่", value=datetime.date.today())
        with t_col:
            tx_type = st.radio("ประเภท", ["รายจ่าย 💸", "รายรับ 💰", "เงินออม 🐷"], horizontal=True)

        st.divider()
        
        # เลือกหมวด หรือ พิมพ์เอง
        mode = st.radio("วิธีระบุหมวด:", ["เลือกจากรายการ", "พิมพ์เอง"], horizontal=True)
        cat = ""
        if mode == "เลือกจากรายการ":
            if tx_type == "เงินออม 🐷":
                opts = ["หยอดกระปุก", "ฝากธนาคาร", "หุ้น/กองทุน", "ทองคำ"]
            elif tx_type == "รายรับ 💰":
                opts = ["เงินเดือน", "โบนัส", "ขายของ", "ได้เงินคืน", "อื่นๆ"]
            else:
                opts = ["อาหาร", "เดินทาง", "ของใช้", "ค่าห้อง", "น้ำ/ไฟ/เน็ต", "ผ่อนของ", "รักษาพยาบาล", "อื่นๆ"]
            cat = st.selectbox("เลือกหมวด:", opts)
        else:
            cat = st.text_input("พิมพ์หมวดเอง:", placeholder="เช่น ค่าอาหารแมว")

        amt = st.number_input("จำนวนเงิน:", min_value=0.0, step=10.0)
        note = st.text_input("โน้ตกันลืม:")

        if st.button("❤️ บันทึก", use_container_width=True):
            if not cat:
                st.error("ใส่หมวดหมู่ด้วยครับ")
            elif amt <= 0:
                st.warning("ยอดเงินต้องมากกว่า 0")
            else:
                save_record(tx_date, cat, tx_type, amt, note)
                st.success("บันทึกเรียบร้อย!")
                st.rerun()

    # === Tab 2: ประวัติ ===
    with t2:
        st.subheader("ประวัติย้อนหลัง")
        df = load_data()
        if not df.empty:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            if st.button("ล้างข้อมูลทั้งหมด"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                    st.rerun()
        else:
            st.info("ยังไม่มีข้อมูล")

    # === Tab 3: สรุปกราฟ (ใช้ Altair แทน Matplotlib) ===
    with t3:
        st.subheader("📊 สรุปยอดเงิน")
        df = load_data()
        if not df.empty:
            # คำนวณยอด
            inc = df[df["ประเภท"]=="รายรับ 💰"]["จำนวนเงิน"].sum()
            exp = df[df["ประเภท"]=="รายจ่าย 💸"]["จำนวนเงิน"].sum()
            sav = df[df["ประเภท"]=="เงินออม 🐷"]["จำนวนเงิน"].sum()

            c1, c2, c3 = st.columns(3)
            c1.metric("รายรับ", f"{inc:,.0f}")
            c2.metric("รายจ่าย", f"{exp:,.0f}")
            c3.metric("เงินออม", f"{sav:,.0f}")
            
            st.divider()

            # กราฟวงกลม 1: สัดส่วน รายรับ-จ่าย-ออม
            st.write("#### 🍰 สัดส่วนการเงิน")
            summ_type = df.groupby("ประเภท")["จำนวนเงิน"].sum().reset_index()
            
            chart1 = alt.Chart(summ_type).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="จำนวนเงิน", type="quantitative"),
                color=alt.Color(field="ประเภท", type="nominal"),
                tooltip=["ประเภท", "จำนวนเงิน"]
            )
            st.altair_chart(chart1, use_container_width=True)

            # กราฟวงกลม 2: รายจ่ายหมดไปกับค่าอะไร?
            st.write("#### 💸 รายจ่ายแยกตามหมวด")
            exp_data = df[df["ประเภท"]=="รายจ่าย 💸"]
            if not exp_data.empty:
                summ_exp = exp_data.groupby("หมวดหมู่")["จำนวนเงิน"].sum().reset_index()
                chart2 = alt.Chart(summ_exp).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="จำนวนเงิน", type="quantitative"),
                    color=alt.Color(field="หมวดหมู่", type="nominal"),
                    tooltip=["หมวดหมู่", "จำนวนเงิน"]
                )
                st.altair_chart(chart2, use_container_width=True)
            else:
                st.info("ไม่มีรายจ่าย")

        else:
            st.info("ลองบันทึกข้อมูลก่อนนะ กราฟถึงจะขึ้น")
