import streamlit as st
import streamlit.components.v1 as components

# --- 1. ตั้งค่าหน้าเว็บ Streamlit ---
st.set_page_config(
    page_title="Meow Wallet",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ส่วนโค้ดทำเว็บ (HTML/CSS/JS) ---
# ห้ามลบเครื่องหมายฟันหนู 3 ตัว (""") หัว-ท้าย เด็ดขาด
html_code = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Meow Wallet</title>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Kanit', sans-serif;
            background-color: transparent;
            color: #2D3748;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
        }

        :root {
            --primary-gradient: linear-gradient(135deg, #FF9966 0%, #FF5E62 100%);
            --card-bg: #FFFFFF;
            --green: #48BB78;
            --red: #F56565;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .app-container {
            width: 100%;
            max-width: 500px;
            padding: 20px;
        }

        /* การ์ดเงิน */
        .wallet-card {
            background: var(--primary-gradient);
            color: white;
            padding: 30px;
            border-radius: 24px;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(255, 94, 98, 0.4);
            margin-bottom: 25px;
            position: relative;
            overflow: hidden;
        }

        .balance-label { font-size: 16px; opacity: 0.9; }
        .balance-value { font-size: 48px; font-weight: 700; margin: 10px 0; }
        
        .stats-row {
            display: flex;
            justify-content: space-between;
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 16px;
            backdrop-filter: blur(5px);
        }

        .stat-item { text-align: center; flex: 1; }
        .stat-value { font-size: 18px; font-weight: 600; margin-top: 5px;}

        /* ฟอร์ม */
        .add-box {
            background: white;
            padding: 20px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            margin-bottom: 25px;
        }

        input, select {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 2px solid #E2E8F0;
            border-radius: 12px;
            font-family: 'Kanit';
            font-size: 16px;
        }

        .btn-add {
            width: 100%;
            padding: 14px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            cursor: pointer;
            font-weight: 600;
        }
        .btn-add:hover { opacity: 0.9; }

        /* รายการ */
        .list-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow);
            border-left: 5px solid #DDD;
        }
        .list-item.plus { border-left-color: var(--green); }
        .list-item.minus { border-left-color: var(--red); }
        
        .item-text { font-size: 16px; font-weight: 500; }
        .item-date { font-size: 12px; color: #888; }
