<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meow Wallet</title>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #FF9966 0%, #FF5E62 100%);
            --bg-color: #F7F9FC;
            --card-bg: #FFFFFF;
            --text-color: #2D3748;
            --green: #48BB78;
            --red: #F56565;
            --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        body {
            font-family: 'Kanit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }

        .app-container {
            width: 100%;
            max-width: 400px; /* ขนาดเท่ามือถือ */
            position: relative;
        }

        /* ส่วนหัว */
        header {
            text-align: center;
            margin-bottom: 20px;
        }
        header h2 { margin: 0; font-weight: 600; color: #4A5568; }

        /* การ์ดแสดงเงิน */
        .wallet-card {
            background: var(--primary-gradient);
            color: white;
            padding: 30px 20px;
            border-radius: 24px;
            text-align: center;
            box-shadow: 0 20px 25px -5px rgba(255, 94, 98, 0.4);
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }

        .wallet-card::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
            animation: rotate 10s linear infinite;
        }

        @keyframes rotate { from {transform: rotate(0deg);} to {transform: rotate(360deg);} }

        .balance-label { font-size: 14px; opacity: 0.9; position: relative; }
        .balance-value { font-size: 48px; font-weight: 600; margin: 5px 0 15px; position: relative; }
        
        .stats-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            position: relative;
            background: rgba(255,255,255,0.15);
            padding: 10px;
            border-radius: 12px;
            backdrop-filter: blur(5px);
        }

        .stat-item { text-align: center; flex: 1; }
        .stat-label { font-size: 12px; opacity: 0.9; }
        .stat-value { font-size: 18px; font-weight: 500; }
        .stat-value.inc { color: #E6FFFA; }
        .stat-value.exp { color: #FFF5F5; }

        /* ฟอร์มกรอกข้อมูล */
        .add-box {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            margin-bottom: 25px;
        }

        .form-control {
            margin-bottom: 12px;
        }

        input, select {
            width: 100%;
            padding: 14px;
            border: 2px solid #E2E8F0;
            border-radius: 12px;
            font-family: 'Kanit';
            font-size: 16px;
            outline: none;
            box-sizing: border-box;
            transition: 0.3s;
            background: #F8FAFC;
        }

        input:focus, select:focus {
            border-color: #FF9966;
            background: #FFF;
        }

        .btn-add {
            width: 100%;
            padding: 14px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(255, 94, 98, 0.3);
            transition: 0.2s;
        }

        .btn-add:active { transform: scale(0.98); }

        /* รายการ */
        h3 { font-size: 18px; color: #718096; margin-bottom: 15px; border-left: 4px solid #FF9966; padding-left: 10px; }

        ul { list-style: none; padding: 0; }

        .list-item {
            background: var(--card-bg);
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: 0.2s;
            position: relative;
            overflow: hidden;
        }

        .list-item:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }

        .list-item.plus { border-right: 6px solid var(--green); }
        .list-item.minus { border-right: 6px solid var(--red); }

        .item-info h4 { margin: 0; font-size: 16px; font-weight: 500; }
        .item-info p { margin: 4px 0 0; font-size: 12px; color: #A0AEC0; }
        
        .item-amount { font-weight: 600; font-size: 18px; }
        .plus .item-amount { color: var(--green); }
        .minus .item-amount { color: var(--red); }

        .btn-delete {
