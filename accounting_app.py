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
        .item-amount { font-weight: bold; font-size: 18px; }
        .plus .item-amount { color: var(--green); }
        .minus .item-amount { color: var(--red); }
        
        .btn-del {
            background: #FFF5F5; color: #F56565; border: none;
            width: 30px; height: 30px; border-radius: 50%;
            cursor: pointer; margin-left: 10px;
        }
    </style>
</head>
<body>

    <div class="app-container">
        <h2 style="text-align:center; color:#4A5568;">🐱 Meow Wallet</h2>
        
        <div class="wallet-card">
            <div class="balance-label">ยอดเงินคงเหลือ</div>
            <div class="balance-value">฿<span id="balance">0.00</span></div>
            <div class="stats-row">
                <div class="stat-item">
                    <div>รายรับ</div>
                    <div class="stat-value" style="color:#E6FFFA">+<span id="money-plus">0.00</span></div>
                </div>
                <div class="stat-item">
                    <div>รายจ่าย</div>
                    <div class="stat-value" style="color:#FFF5F5">-<span id="money-minus">0.00</span></div>
                </div>
            </div>
        </div>

        <div class="add-box">
            <input type="text" id="text" placeholder="📝 รายการ (เช่น อาหารแมว)">
            <input type="number" id="amount" placeholder="💰 จำนวนเงิน">
            <select id="type">
                <option value="expense">🔴 รายจ่าย</option>
                <option value="income">🟢 รายรับ</option>
            </select>
            <button class="btn-add" onclick="addTransaction()">บันทึกรายการ</button>
        </div>

        <h3 style="color:#718096;">ประวัติรายการ</h3>
        <ul id="list" style="list-style: none; padding: 0;"></ul>
    </div>

    <script>
        const balanceEl = document.getElementById('balance');
        const money_plusEl = document.getElementById('money-plus');
        const money_minusEl = document.getElementById('money-minus');
        const listEl = document.getElementById('list');
        const textEl = document.getElementById('text');
        const amountEl = document.getElementById('amount');
        const typeEl = document.getElementById('type');

        // โหลดข้อมูลจากเครื่อง
        let transactions = JSON.parse(localStorage.getItem('meow_transactions')) || [];

        function init() {
            listEl.innerHTML = '';
            transactions.forEach(addTransactionDOM);
            updateValues();
        }

        function addTransaction() {
            if (textEl.value.trim() === '' || amountEl.value.trim() === '') {
                alert('กรุณากรอกข้อมูลให้ครบถ้วน'); return;
            }
            const amount = +amountEl.value;
            const isExpense = typeEl.value === 'expense';
            const transaction = {
                id: Math.floor(Math.random() * 100000000),
                text: textEl.value,
                amount: isExpense ? -amount : amount,
                date: new Date().toLocaleDateString('th-TH')
            };
            transactions.push(transaction);
            addTransactionDOM(transaction);
            updateValues();
            localStorage.setItem('meow_transactions', JSON.stringify(transactions));
            textEl.value = ''; amountEl.value = '';
        }

        function addTransactionDOM(transaction) {
            const sign = transaction.amount < 0 ? '-' : '+';
            const item = document.createElement('li');
            item.className = transaction.amount < 0 ? 'list-item minus' : 'list-item plus';
            item.innerHTML = `
                <div>
                    <div class="item-text">\${transaction.text}</div>
                    <div class="item-date">\${transaction.date}</div>
                </div>
                <div style="display:flex; align-items:center;">
                    <span class="item-amount">\${sign}\${Math.abs(transaction.amount).toLocaleString()}</span>
                    <button class="btn-del" onclick="removeTransaction(\${transaction.id})">x</button>
                </div>
            `;
            listEl.insertBefore(item, listEl.firstChild);
        }

        function updateValues() {
            const amounts = transactions.map(t => t.amount);
            const total = amounts.reduce((acc, item) => acc + item, 0).toFixed(2);
            const income = amounts.filter(item => item > 0).reduce((acc, item) => acc + item, 0).toFixed(2);
            const expense = (amounts.filter(item => item < 0).reduce((acc, item) => acc + item, 0) * -1).toFixed(2);
            
            balanceEl.innerText = Number(total).toLocaleString();
            money_plusEl.innerText = Number(income).toLocaleString();
            money_minusEl.innerText = Number(expense).toLocaleString();
        }

        function removeTransaction(id) {
            if(confirm('ลบรายการนี้?')) {
                transactions = transactions.filter(t => t.id !== id);
                localStorage.setItem('meow_transactions', JSON.stringify(transactions));
                init();
            }
        }
        init();
    </script>
</body>
</html>
"""

# --- 3. สั่งให้แสดงผล ---
# ต้องมีบรรทัดนี้ ไม่งั้นหน้าจอจะว่างเปล่า
components.html(html_code, height=850, scrolling=True)
