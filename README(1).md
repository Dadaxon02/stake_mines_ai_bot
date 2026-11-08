# 🎰 STAKE MINES AI — Telegram Bot & Analitika Platformasi

O'zbek tilidagi professional Stake Mines tahlil va signallar boti. 
Ushbu loyiha soxta 100% kafolatlarsiz, haqiqiy **matematik ehtimollar nazariyasi** va rasmiy **Provably Fair (HMAC-SHA256)** tekshiruv mexanizmi asosida ishlaydi.

---

## 🚀 Imkoniyatlar

1. **5x5 O'yin Doskasi (25 katak):** Standart 1 ta mina bilan (1 dan 24 gacha erkin sozlanadi).
2. **SIGNAL Generatori:** Har bir katak uchun hisoblangan xavf darajalari (Past xavf, O'rtacha, Yuqori) va eng xavfsiz tavsiya etilgan kataklar.
3. **Provably Fair Verifikatsiya:** Stake.com rasmiy algoritmi bo'yicha server urug'i (seed), mijoz urug'i va nonce orqali minalar haqiqiy joylashuvini tekshirish.
4. **Foydalanuvchi Profili va Ro'yxatdan O'tish:** Telegram ID, username, VIP darajalar, so'ralgan signallar hisobi.
5. **Xavfsiz SQLite Bazasi:** Ma'lumotlarni ishonchli saqlash va statistik tahlil.
6. **Telegram WebApp (TMA) Integratsiyasi:** Interaktiv veb ilova bilan to'liq bog'langan.

---

## 🛠 O'rnatish va Ishga Tushirish (Tezkor Qo'llanma)

### 1. Telegram Bot Tokenini Olish
1. Telegramda [@BotFather](https://t.me/botfather) ga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingiz nomini kiriting (masalan, `Stake Mines AI`).
4. Botingiz username'ini kiriting (masalan, `stake_mines_ai_bot`).
5. BotFather bergan **HTTP API Token**ni nusxalab oling.

---

### 2. Python Muhitini Tayyorlash (Ubuntu VPS yoki Kompyuter)

```bash
# Repozitoriy papkasiga o'ting
cd python_bot

# Python virtual muhitini yarating
python3 -m venv venv
source venv/bin/activate   # Windowsda: venv\Scripts\activate

# Kerakli kutubxonalarni o'rnating
pip install -r requirements.txt
```

---

### 3. Konfiguratsiyani Sozlash

`.env.example` faylidan nusxa olib `.env` yarating:

```bash
cp .env.example .env
```

`.env` faylini ochib, BotFather'dan olgan tokenni yozing:

```ini
BOT_TOKEN="1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
ADMIN_ID="Sizning_Telegram_ID"
DATABASE_NAME="stake_mines.db"
WEBAPP_URL="https://ais-dev-fzqpfcgsrcucvmwcf22qvc-82318020725.asia-northeast1.run.app"
```

---

### 4. Botni Ishga Tushirish

```bash
python bot.py
```

Botingiz Telegramda ishga tushadi! Telegramda botingizga `/start` yuboring.

---

### 5. 24/7 Rejimda Ishlatish (Systemd Service)

Serverda fon rejimida uzluksiz ishlashi uchun `systemd` xizmatini yoqing:

```ini
# /etc/systemd/system/stakemines.service
[Unit]
Description=Stake Mines AI Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/stake_mines/python_bot
ExecStart=/root/stake_mines/python_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Xizmatni faollashtirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stakemines
sudo systemctl start stakemines
```

---

## 🛡 Provably Fair Qanday Ishlaydi?

Stake Mines tizimida minalar joyi quyidagi formula orqali aniqlanadi:
`HMAC_SHA256(key = server_seed, message = client_seed:nonce:round)`

Olingan 32 baytli xesh 4 baytlik float qiymatlarga aylantirilib, 25 ta katak ichida minalar o'rni taqsimlanadi. Ushbu bot ushbu jarayonni mustaqil ravishda 100% aniqlikda tekshirish imkonini beradi.
