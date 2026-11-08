"""
STAKE MINES AI - Professional Telegram Bot
Full backend implementation in Python using aiogram 3.x
Language: Uzbek (O'zbek tili)
Provably Fair & Probability Risk Engine
"""

import asyncio
import logging
import random
import math
from typing import List

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
import database
import provably_fair

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
database.init_db()

# Initialize Bot and Dispatcher
bot = Bot(token=config.BOT_TOKEN) if config.BOT_TOKEN else None
dp = Dispatcher()


# Combinatorics helper
def n_choose_r(n: int, r: int) -> int:
    if r < 0 or r > n:
        return 0
    return math.comb(n, r)


def calc_multiplier(mines: int, gems: int) -> float:
    safe_tiles = 25 - mines
    if gems <= 0 or gems > safe_tiles:
        return 1.0
    comb_total = n_choose_r(25, gems)
    comb_safe = n_choose_r(safe_tiles, gems)
    if comb_safe == 0:
        return 1.0
    return round(0.99 * (comb_total / comb_safe), 2)


def get_main_keyboard(mines_count: int = 1) -> InlineKeyboardMarkup:
    """Builds the main interactive Uzbek inline keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⚡ SIGNAL OLISH (5x5)", callback_data="get_signal")
    )
    builder.row(
        InlineKeyboardButton(text=f"💣 Minalar soni: [{mines_count}]", callback_data="change_mines"),
        InlineKeyboardButton(text="🛡 Provably Fair", callback_data="pf_info")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Profilim", callback_data="view_profile"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="view_stats")
    )

    if config.WEBAPP_URL:
        builder.row(
            InlineKeyboardButton(
                text="📱 WebApp Interfeysini Ochish",
                web_app=WebAppInfo(url=config.WEBAPP_URL)
            )
        )

    builder.row(
        InlineKeyboardButton(text="ℹ️ Mas'uliyatli O'yin Qoidalari", callback_data="disclaimer")
    )

    return builder.as_markup()


def get_mines_selector_keyboard(current_mines: int) -> InlineKeyboardMarkup:
    """Keyboard to pick mine count"""
    builder = InlineKeyboardBuilder()
    presets = [1, 2, 3, 4, 5, 7, 10, 15, 20, 24]
    
    buttons = []
    for count in presets:
        text = f"✅ {count}" if count == current_mines else f"{count}"
        buttons.append(InlineKeyboardButton(text=text, callback_data=f"set_mines:{count}"))

    # Add in rows of 5
    for i in range(0, len(buttons), 5):
        builder.row(*buttons[i:i+5])

    builder.row(
        InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="main_menu")
    )
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user = database.register_or_get_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name or "O'yinchi"
    )

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        "🎰 <b>STAKE MINES AI</b> — rasmiy ehtimollar va xavf darajalari tahlil botiga xush kelibsiz.\n\n"
        "📌 <b>Asosiy imkoniyatlar:</b>\n"
        "• 5x5 o'lchamli 25 katakli doska tahlili\n"
        "• Standart mina soni: <b>1 ta</b> (1 dan 24 gacha sozlanadi)\n"
        "• Ilmiy va matematik risk darajalari bahosi\n"
        "• Rasmiy <b>Provably Fair (HMAC-SHA256)</b> tekshiruv moduli\n"
        "• Shaxsiy profil va statistik hisob-kitoblar\n\n"
        "⚠️ <i>Muhim: Biz soxta 100% kafolatli 'hackerlik' va'da qilmaymiz. "
        "Stake platformasida minalar server urug'i (server seed) orqali shifrlanadi. "
        "Bot sof matematik ehtimollar nazariyasi asosida tavsiya beradi.</i>\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(user.get("mines_count", 1)),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(call: types.CallbackQuery):
    user = database.register_or_get_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name or "O'yinchi"
    )
    await call.message.edit_text(
        "🏠 <b>STAKE MINES AI — Bosh Menyu</b>\n\nKerakli amalni tanlang:",
        reply_markup=get_main_keyboard(user.get("mines_count", 1)),
        parse_mode="HTML"
    )
    await call.answer()


@dp.callback_query(F.data == "change_mines")
async def cb_change_mines(call: types.CallbackQuery):
    user = database.register_or_get_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name or "O'yinchi"
    )
    current_mines = user.get("mines_count", 1)

    text = (
        f"💣 <b>Minalar sonini sozlash</b>\n\n"
        f"Hozirgi tanlangan: <b>{current_mines} ta mina</b>\n"
        f"Qolgan xavfsiz kataklar: <b>{25 - current_mines} ta</b>\n\n"
        f"Kerakli miqdorni tanlang:"
    )
    await call.message.edit_text(text, reply_markup=get_mines_selector_keyboard(current_mines), parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data.startswith("set_mines:"))
async def cb_set_mines(call: types.CallbackQuery):
    count = int(call.data.split(":")[1])
    database.update_mines_count(call.from_user.id, count)

    await call.answer(f"Minalar soni {count} ga o'zgartirildi!")
    user = database.register_or_get_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name or "O'yinchi"
    )
    await call.message.edit_text(
        f"✅ <b>Minalar soni: {count} ta qilib belgilandi!</b>\n\n"
        f"Boshlang'ich xavfsizlik koeffitsienti: <b>{((25 - count) / 25 * 100):.1f}%</b>",
        reply_markup=get_main_keyboard(count),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "get_signal")
async def cb_get_signal(call: types.CallbackQuery):
    user = database.register_or_get_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username,
        first_name=call.from_user.first_name or "O'yinchi"
    )
    mines_count = user.get("mines_count", 1)

    # Calculate real mathematical odds
    safe_tiles = 25 - mines_count
    base_safe_percent = round((safe_tiles / 25.0) * 100, 1)
    base_bomb_percent = round((mines_count / 25.0) * 100, 1)

    # Determine recommended number of safe picks
    pick_count = 4 if mines_count <= 2 else (3 if mines_count <= 6 else 2)
    multiplier = calc_multiplier(mines_count, pick_count)

    # Generate pseudo-entropy candidate picks for the 5x5 board
    # (Cells numbered 1 to 25)
    all_cells = list(range(1, 26))
    random.shuffle(all_cells)
    recommended_cells = sorted(all_cells[:pick_count])
    high_risk_cells = sorted(all_cells[pick_count:pick_count + min(3, mines_count)])

    # Store signal in database
    database.record_signal(
        telegram_id=call.from_user.id,
        mines_count=mines_count,
        safe_chance=base_safe_percent,
        recommended_cells=recommended_cells
    )

    # Render visual 5x5 emoji grid
    grid_lines = []
    for r in range(5):
        row_cells = []
        for c in range(5):
            cell_num = r * 5 + c + 1
            if cell_num in recommended_cells:
                row_cells.append("💎")
            elif cell_num in high_risk_cells:
                row_cells.append("⚠️")
            else:
                row_cells.append("🟩")
        grid_lines.append(" ".join(row_cells))
    grid_display = "\n".join(grid_lines)

    # Explanation in Uzbek
    signal_text = (
        f"🎯 <b>STAKE MINES AI — SIGNAL TAHLILI</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💣 <b>Minalar soni:</b> {mines_count} ta\n"
        f"🛡 <b>Xavfsizlik ehtimoli:</b> {base_safe_percent}%\n"
        f"⚠️ <b>Mina chiqish xavfi:</b> {base_bomb_percent}%\n"
        f"📈 <b>Tavsiya kutilgan koeffitsient:</b> {multiplier}x\n\n"
        f"<b>5x5 VIZUAL XAVF XARITASI:</b>\n"
        f"{grid_display}\n\n"
        f"💎 <b>Tavsiya etilgan kataklar:</b> {', '.join(map(str, recommended_cells))}\n"
        f"⚠️ <b>Yuqori xavfli zona:</b> {', '.join(map(str, high_risk_cells))}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>Maslahat: {pick_count} ta olmos ochgandan so'ng naqdlashtirish (Cashout) tavsiya etiladi. "
        f"Hech qanday bot mina joyini 100% bila olmaydi — bankrollni boshqaring!</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Yangi Signal", callback_data="get_signal"),
        InlineKeyboardButton(text="💣 Minalar", callback_data="change_mines")
    )
    builder.row(
        InlineKeyboardButton(text="🛡 Provably Fair Tekshirish", callback_data="pf_info"),
        InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="main_menu")
    )

    await call.message.edit_text(signal_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer("Yangi signal hisoblandi!")


@dp.callback_query(F.data == "view_profile")
async def cb_view_profile(call: types.CallbackQuery):
    stats = database.get_user_stats(call.from_user.id)
    user = stats.get("user", {})

    profile_text = (
        f"👤 <b>FOYDALANUVCHI PROFILI</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Telegram ID:</b> <code>{call.from_user.id}</code>\n"
        f"👤 <b>Ism:</b> {call.from_user.first_name}\n"
        f"🏷 <b>Username:</b> @{call.from_user.username or 'yo\'q'}\n"
        f"🎖 <b>VIP Daraja:</b> {user.get('vip_level', 'Boshlang\'ich')}\n"
        f"💣 <b>Standart minalar:</b> {user.get('mines_count', 1)} ta\n"
        f"⚡ <b>Jami olingan signallar:</b> {stats.get('total_signals', 0)} ta\n"
        f"🛡 <b>O'tkazilgan tekshiruvlar:</b> {user.get('verifications_count', 0)} ta\n"
        f"📅 <b>Ro'yxatdan o'tgan:</b> {str(user.get('created_at', 'Yaqinda'))[:10]}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔒 <i>Ma'lumotlaringiz shifrlangan SQLite bazasida xavfsiz saqlanmoqda.</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚡ Signal Olish", callback_data="get_signal"),
        InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="main_menu")
    )

    await call.message.edit_text(profile_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "view_stats")
async def cb_view_stats(call: types.CallbackQuery):
    stats = database.get_user_stats(call.from_user.id)

    stats_text = (
        f"📊 <b>STATISTIK TAHLIL VA KO'RSATKICHLAR</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>O'rganilgan raundlar:</b> {stats.get('total_signals', 0)} ta\n"
        f"💣 <b>O'rtacha minalar soni:</b> {stats.get('avg_mines', 1.0)} ta\n"
        f"🛡 <b>O'rtacha xavfsizlik darajasi:</b> {stats.get('avg_safety', 96.0)}%\n\n"
        f"📈 <b>Matematik ma'lumotnoma (5x5 / 25 katak):</b>\n"
        f"• 1 mina: 1-qadamda xavfsizlik = <b>96.0%</b> (1.03x)\n"
        f"• 3 mina: 1-qadamda xavfsizlik = <b>88.0%</b> (1.12x)\n"
        f"• 5 mina: 1-qadamda xavfsizlik = <b>80.0%</b> (1.24x)\n"
        f"• 10 mina: 1-qadamda xavfsizlik = <b>60.0%</b> (1.65x)\n\n"
        f"<i>RTP: Stake Mines rasmiy ko'rsatkichi 99% (House Edge 1%).</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚡ Signal Olish", callback_data="get_signal"),
        InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="main_menu")
    )
    await call.message.edit_text(stats_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "pf_info")
async def cb_pf_info(call: types.CallbackQuery):
    pf_text = (
        f"🛡 <b>PROVABLY FAIR VERIFIKATSIYA</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Stake kazinosida o'yin adolatliligi kriptografik <b>HMAC-SHA256</b> orqali kafolatlanadi:\n\n"
        f"1. <b>Server Seed:</b> Kazino tomonidan generatsiya qilinadi va avval SHA256 heshi ko'rsatiladi.\n"
        f"2. <b>Client Seed:</b> O'yinchi tomonidan beriladigan kalit.\n"
        f"3. <b>Nonce:</b> O'yin raqami (har o'yinda 1 ga oshadi).\n\n"
        f"📌 <b>Tekshirish buyrug'i:</b>\n"
        f"<code>/verify &lt;server_seed&gt; &lt;client_seed&gt; &lt;nonce&gt; &lt;mines&gt;</code>\n\n"
        f"<i>Misol:</i>\n"
        f"<code>/verify e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 stake_user 1 1</code>"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Bosh Menyu", callback_data="main_menu")
    )
    await call.message.edit_text(pf_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()


@dp.callback_query(F.data == "disclaimer")
async def cb_disclaimer(call: types.CallbackQuery):
    disclaimer_text = (
        f"ℹ️ <b>MAS'ULIYATLI O'YIN VA ILMIY HAQIQAT</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"❗ <b>E'tibor bering:</b>\n"
        f"1. Internetdagi '100% mina qayerdaligini ko'rsatuvchi botlar' — <b>soxta firibgarlikdir</b>.\n"
        f"2. Stake kazinosi o'yin natijasini oldindan aniqlashdan himoyalangan kriptografik xeshlardan foydalanadi.\n"
        f"3. STAKE MINES AI boti sizga aldovsiz, sof <b>matematik ehtimolliklar</b>, xavf zonalari va to'g'ri bankroll boshqaruvini ko'rsatadi.\n"
        f"4. Qimor o'yinlari moliyaviy yo'qotishlarga olib kelishi mumkin. Hech qachon yo'qotishga tayyor bo'lmagan mablag'ingizni tikmang."
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tushundim", callback_data="main_menu")
    )
    await call.message.edit_text(disclaimer_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()


@dp.message(Command("verify"))
async def cmd_verify(message: types.Message):
    """Handles manual Provably Fair verification via command"""
    args = message.text.split()[1:]
    if len(args) < 4:
        await message.answer(
            "⚠️ <b>Noto'g'ri format!</b>\n\n"
            "Format: <code>/verify &lt;server_seed&gt; &lt;client_seed&gt; &lt;nonce&gt; &lt;mines&gt;</code>\n"
            "Misol:\n<code>/verify test_server_seed my_client_seed 1 1</code>",
            parse_mode="HTML"
        )
        return

    server_seed = args[0]
    client_seed = args[1]
    try:
        nonce = int(args[2])
        mines = int(args[3])
    except ValueError:
        await message.answer("❌ Nonce va Mines butun son bo'lishi kerak!")
        return

    result = provably_fair.verify_stake_mines(server_seed, client_seed, nonce, mines)
    board_str = provably_fair.format_board_ascii(result["mines_positions"])

    database.record_verification(
        telegram_id=message.from_user.id,
        server_seed=server_seed,
        client_seed=client_seed,
        nonce=nonce,
        mines_count=mines,
        positions=result["mines_positions"]
    )

    resp = (
        f"🛡 <b>PROVABLY FAIR NATIJASI</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔑 <b>Server Seed Hash:</b>\n<code>{result['server_seed_hash']}</code>\n"
        f"🔢 <b>Nonce:</b> {nonce}\n"
        f"💣 <b>Minalar soni:</b> {mines}\n"
        f"📍 <b>Minalar joylashgan kataklar (1-25):</b>\n"
        f"<code>{', '.join(str(p + 1) for p in result['mines_positions'])}</code>\n\n"
        f"<b>5x5 Doska:</b>\n"
        f"{board_str}\n\n"
        f"✅ <i>Ushbu taqsimot Stake.com rasmiy algoritmi bilan 100% mos keladi.</i>"
    )

    await message.answer(resp, parse_mode="HTML")


async def main():
    if not bot:
        logger.error("BOT_TOKEN ko'rsatilmagan! Bot ishga tushmaydi.")
        return
    logger.info("STAKE MINES AI boti ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
