import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
import json
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
import random
import string

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask App untuk Keep-Alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# File untuk menyimpan admin
ADMIN_FILE = "admin.json"
ADMIN_UTAMA = "6754416676"  # Admin utama

# Fungsi untuk memuat admin dari file
def load_admins():
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as file:
            return json.load(file)
    return [ADMIN_UTAMA]

# Fungsi untuk menyimpan admin ke file
def save_admins(admins):
    with open(ADMIN_FILE, "w") as file:
        json.dump(admins, file)

# Fungsi untuk validasi admin
def is_admin(user_id):
    admins = load_admins()
    return str(user_id) in admins

# Fungsi untuk menghasilkan string acak
def random_str(length):
    return ''.join(random.choices(string.digits, k=length))

def random_letters(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Fungsi untuk membuat akun secara asinkron
async def create_account(email, password, session, cookies, headers, url):
    payload = {
        'utf8': 'âœ“',
        'authenticity_token': '8ae4dr8-okquY8afeDlpFWx5x6X8GLVpukZB7GvGvJQxYNFPvOjfXfWp0ei5hgotDRLqwCDdAJW-hNN0Fmxy-g',
        'user[email]': email,
        'user[password]': password,
        'commit': 'Daftar'
    }

    try:
        async with session.post(url, headers=headers, data=payload, cookies=cookies, allow_redirects=False) as response:
            if response.status == 302:
                location_response = response.headers.get("Location")
                if location_response in ['https://www.vidio.com/users', "https://www.vidio.com/users/signup"]:
                    return f"{email} | {password}"
                elif location_response and location_response.startswith("https://www.vidio.com/user_consent"):
                    consent_url = f"{location_response}/accept"
                    async with session.post(consent_url, headers=headers, cookies=cookies, allow_redirects=False) as consent_response:
                        if consent_response.status == 302 and consent_response.headers.get("Location") in ['https://www.vidio.com/users', "https://www.vidio.com/users/signup"]:
                            return f"{email} | {password}"
    except Exception as e:
        logger.error(f"Error creating account for {email}: {e}")

    return None

# Fungsi utama untuk menangani pembuatan akun
async def run_regist_code(password, jumlah_akun):
    url = 'https://www.vidio.com/users'
    cookies = {
        '_vidio_session': 'M2R0cFkvazFqV3N0Rjh1d2xwbmxDc3pRd3dNQlBRaVIzTmZkbUpLRWI0d1RSK2k5VkJqdW45V1BUR1gxOHpScXk1QU0ybWIrazRaL0ZWQUUzeVdLdXRpb21QUjh3OFlkWmRQeHJMNzMzS1lDZkUyM2ZYM2trcTh1V3J2VmRORHdxcUxzYzgvZGFFcGZtUEJyQlQzWUE2WlNLTWN1NDNUT3FrNy9HOUdZOXRTbThacG1KeFNKbjE5TjVHVmRJZm9OazNOcVJTQUFiaEFrVzBsVWJ5UXpISWVmN0pKNHZNN0lKVEg1blEwVWI2bE1VL0NrcWRsWU5rblpzRHdJRVZVallRN1JYOEliZEhZeWxmVmIxVDN2L0x3dG9lRUYyWDJYcGNSSG1zWXptYXRWelM1dWxWTUhNNll6OFlaSzBaQWh0ME1uaTR5QnR6dkVaNVB6eHVZUU0wYjZKZk5uRG5Pb0JCYTA3c3JyM0RsN3pLUXRwdEFUanFjQ3IrRlBhVENIQTUwaVdiaGFEckNxN3NPSG1ZVkdSYTBsdUxxZ09rNXg1Y0FUc2dPMEphRFBFQ1JjeUxMeDRuRjNUWWlFTVliWC0tN2cxNXU4cmdxa25nakxqUWgvdDJyUT09--ae85dd8df69ccfd51ae5d9dbcfb78de0a091e654'
    }
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.vidio.com',
        'referer': 'https://www.vidio.com/users',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(jumlah_akun):
            email = f"{random_str(6)}{random_letters(2)}@gmail.com"
            tasks.append(create_account(email, password, session, cookies, headers, url))
        results = await asyncio.gather(*tasks)
    return [result for result in results if result]

# Command untuk memulai bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admins = load_admins()
    status = "Admin" if str(user_id) in admins else "Belum Berlanggan"
    await update.message.reply_text(
        f"ID Telegram Anda: {user_id}\nStatus: {status}"
    )

# Command untuk menambahkan admin
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Maaf Anda belum berlangganan!")
        return

    try:
        new_admin_id = context.args[0]
        admins = load_admins()
        if new_admin_id in admins:
            await update.message.reply_text(f"ID {new_admin_id} sudah menjadi admin.")
        else:
            admins.append(new_admin_id)
            save_admins(admins)
            await update.message.reply_text(f"ID {new_admin_id} telah ditambahkan sebagai admin.")
    except IndexError:
        await update.message.reply_text("Gunakan format: /add_admin idtelegram")

# Command untuk menghapus admin
async def delete_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Maaf Anda belum berlangganan!")
        return

    try:
        remove_admin_id = context.args[0]
        if remove_admin_id == ADMIN_UTAMA:
            await update.message.reply_text("Admin utama tidak dapat dihapus.")
            return

        admins = load_admins()
        if remove_admin_id in admins:
            admins.remove(remove_admin_id)
            save_admins(admins)
            await update.message.reply_text(f"ID {remove_admin_id} telah dihapus dari admin.")
        else:
            await update.message.reply_text(f"ID {remove_admin_id} bukan admin.")
    except IndexError:
        await update.message.reply_text("Gunakan format: /delete_admin idtelegram")

async def create_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Maaf Anda belum berlangganan!")
        return

    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Format perintah salah. Gunakan: /create password jumlahakun")
            return

        password = args[0]
        jumlah_akun = int(args[1])

        if jumlah_akun > 50:
            await update.message.reply_text("Jumlah akun maksimal adalah 50.")
            return
        if jumlah_akun <= 0:
            await update.message.reply_text("Jumlah akun harus lebih dari 0.")
            return

        await update.message.reply_text("Membuat akun, mohon tunggu...")
        created_accounts = await run_regist_code(password, jumlah_akun)

        if created_accounts:
            file_name = f"accounts_{jumlah_akun}.txt"
            with open(file_name, "w") as file:
                file.write("\n".join(created_accounts))
            
            with open(file_name, "rb") as file:
                await update.message.reply_document(InputFile(file), filename=file_name)

            # Kirim pesan setelah file berhasil dikirim
            await update.message.reply_text("Yeay, Anda berhasil membuat Akun Vidio!")
        else:
            await update.message.reply_text("Gagal membuat akun.")
    except Exception as e:
        logger.error(f"Error in /create: {e}")
        await update.message.reply_text(f"Terjadi kesalahan: {str(e)}")
# Fungsi utama
def main():
    # Load environment variables
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        logger.error("Telegram Bot Token tidak ditemukan di environment variables.")
        return

    # Start Flask Keep-Alive Server
    keep_alive()

    # Start Telegram Bot
    application = Application.builder().token(TOKEN).build()

    # Daftarkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_admin", add_admin))
    application.add_handler(CommandHandler("delete_admin", delete_admin))
    application.add_handler(CommandHandler("create", create_account_handler))

    # Jalankan bot
    logger.info("Bot dimulai...")
    application.run_polling()

if __name__ == "__main__":
    # Inisialisasi admin file jika belum ada
    if not os.path.exists(ADMIN_FILE):
        save_admins([ADMIN_UTAMA])

    main()