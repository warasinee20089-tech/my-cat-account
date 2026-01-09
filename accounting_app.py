import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Meow Wallet",
    page_icon="🐱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ซ่อนเมนูและ footer ของ Streamlit เพื่อความสวยงาม
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- ส่วนโค้ด HTML/CSS/JS แปะลงในนี้ ---
html_code = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Meow Wallet</title>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Reset และตั้งค่าพื้นฐาน */
        * { box-sizing: border-box; }
        body {
            font-family: 'Kanit', sans-serif;
            background-color: transparent; /* ให้โปร่งใสเพื่อให้เข้ากับพื้นหลัง Streamlit */
            color: #2D3748;
            margin: 0;
            padding: 10px;
            display: flex;
            justify-content: center;
        }

        /* ตัวแปรสี */
        :root {
            --primary-gradient: linear-gradient(135deg, #FF9966 0%, #FF5E62 100%);
            --card-bg: #FFFFFF;
            --green: #48BB78;
            --red: #F56565;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        .app-container {
            width: 100%;
            max-width: 420px;
        }

        /* ส่วนหัว */
        header {
            text-align: center;
            margin-bottom: 25px;
        }
        header h2 {
            margin: 0;
            font-weight: 600;
            color: #4A5568;
            font-size: 28px;
        }

        /* การ์ดแสดงเงิน */
        .wallet-card {
            background: var(--primary-gradient);
            color: white;
            padding: 30px 25px;
            border-radius: 24px;
            text-align: center;
            box-shadow: 0 20px 25px -5px rgba(255, 94, 98, 0.3);
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }

        /* ลายน้ำหมุนๆ */
        .wallet-card::before {
            content: '';
            position: absolute;
            top: -60%; left: -60%;
            width: 220%; height: 220%;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
            animation: rotate 15s linear infinite;
        }
        @keyframes rotate { from {transform: rotate(0deg);} to {transform: rotate(360deg);} }

        .balance-label { font-size: 16px; opacity: 0.9; position: relative; }
        .balance-value { font-size: 52px; font-weight: 700; margin: 5px 0 20px; position: relative; line-height: 1; }
        
        .stats-row {
            display: flex;
            justify-content: center;
            gap: 15px;
            position: relative;
            background: rgba(255,255,255,0.2);
            padding: 12px;
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }

        .stat-item { text-align: center; flex: 1; }
        .stat-label { font-size: 13px; opacity: 0.95; margin-bottom: 4px; }
        .stat-value { font-size: 18px; font-weight: 600; }
        .stat-value.inc { color: #E6FFFA; }
        .stat-value.exp { color: #FFF5F5; }

        /* ฟอร์มกรอกข้อมูล */
        .add-box {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            margin-bottom: 30px;
        }

        .form-label {
            font-weight: 500;
            margin-bottom: 8px;
            display: block;
            color: #4A5568;
        }

        .form-control { margin-bottom: 15px; }

        input, select {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #E2E8F0;
            border-radius: 14px;
            font-family: 'Kanit';
            font-size: 16px;
            outline: none;
            transition: 0.3s;
            background: #F8FAFC;
            color: #2D3748;
        }

        input::placeholder { color: #A0AEC0; }
        input:focus, select:focus { border-color: #FF9966; background: #FFF; box-shadow: 0 0 0 3px rgba(255, 153, 102, 0.1); }

        .btn-add {
            width: 100%;
            padding: 16px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(255, 94, 98, 0.3);
            transition: 0.2s;
            margin-top: 10px;
        }

        .btn-add:active { transform: scale(0.98); box-shadow: none; }

        /* รายการ */
        .history-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            color: #718096;
        }
        .history-header i { margin-right: 10px; color: #FF9966; }
        h3 { margin: 0; font-size: 20px; font-weight: 600; }

        ul { list-style: none; padding: 0; margin: 0; }

        .list-item {
            background: var(--card-bg);
            padding: 16px;
            margin-bottom: 14px;
            border-radius: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            position: relative;
        }

        .list-item:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }

        .list-item::before {
            content: '';
            position: absolute;
            left: 0; top: 50%;
            transform: translateY(-50%);
            height: 70%;
            width: 5px;
            border-radius: 0 4px 4px 0;
        }

        .list-item.plus::before { background-color: var(--green); }
        .list-item.minus::before { background-color: var(--red); }

        .item-info { padding-left: 12px; }
        .item-info h4 { margin: 0; font-size: 17px; font-weight: 500; color: #2D3748; }
        .item-info p { margin: 6px 0 0; font-size: 13px; color: #A0AEC0; display: flex; align-items: center; }
        .item-info p i { margin-right: 6px; font-size: 11px; }
        
        .item-right { display: flex; align-items: center; }
        .item-amount { font-weight: 700; font-size: 19px; margin-right: 15px; }
        .plus .item-amount { color: var(--green); }
        .minus .item-amount { color: var(--red); }

        .btn-delete {
            background: #EDF2F7;
            border: none;
            color: #A0AEC0;
            cursor: pointer;
            width: 32px; height: 32px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            transition: 0.2s;
        }
        .btn-delete
