import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread
import json
from datetime import datetime, timedelta
import os
from io import BytesIO
from dotenv import load_dotenv
import aiohttp
import asyncio
import random
import string
import flask

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


# File untuk menyimpan data admin dan member
ADMIN_FILE = "admin.json"
MEMBER_FILE = "member.json"
ADMIN_UTAMA = "6754416676"  # ID Admin Utama

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):  # Jika data bukan dictionary
                    data = {}
        except json.JSONDecodeError:  # Jika file rusak atau tidak bisa dibaca
            data = {}
    else:
        data = {}

    # Pastikan admin utama selalu ada
    if file == ADMIN_FILE and ADMIN_UTAMA not in data:
        data[ADMIN_UTAMA] = "2099-12-31 23:59:59"
        save_data(ADMIN_FILE, data)

    return data

# Fungsi untuk menyimpan data ke file
def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# Fungsi untuk menambahkan durasi
def add_days(days):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

# Fungsi untuk memeriksa masa aktif
def is_active(data, user_id):
    user_id = str(user_id)
    if user_id == ADMIN_UTAMA:
        return True  # Admin utama selalu aktif
    if user_id in data:
        expiry = datetime.strptime(data[user_id], "%Y-%m-%d %H:%M:%S")
        return datetime.now() <= expiry
    return False

# Fungsi validasi admin
def is_admin(user_id):
    admins = load_data(ADMIN_FILE)
    return str(user_id) in admins

# Fungsi validasi member
def is_member(user_id):
    members = load_data(MEMBER_FILE)
    return str(user_id) in members

# Fungsi untuk menghasilkan string acak
def random_str(length):
    return ''.join(random.choices(string.digits, k=length))

def random_letters(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Fungsi untuk menghasilkan string acak
def random_str(length):
    return ''.join(random.choices(string.digits, k=length))

def random_letters(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

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

    created_accounts = []
    async with aiohttp.ClientSession() as session:
        while len(created_accounts) < jumlah_akun:
            remaining = jumlah_akun - len(created_accounts)
            tasks = []
            for _ in range(remaining):
                email = f"{random_str(6)}{random_letters(2)}@gmail.com"
                tasks.append(create_account(email, password, session, cookies, headers, url))
            
            results = await asyncio.gather(*tasks)
            valid_results = [result for result in results if result]
            created_accounts.extend(valid_results)

            logger.info(f"Requested: {jumlah_akun}, Created: {len(created_accounts)}, Remaining: {remaining - len(valid_results)}")

    return created_accounts

# Fungsi pembuatan akun tetap sama dengan retry
async def create_account(email, password, session, cookies, headers, url):
    payload = {
        'utf8': 'âœ“',
        'authenticity_token': '8ae4dr8-okquY8afeDlpFWx5x6X8GLVpukZB7GvGvJQxYNFPvOjfXfWp0ei5hgotDRLqwCDdAJW-hNN0Fmxy-g',
        'user[email]': email,
        'user[password]': password,
        'commit': 'Daftar'
    }

    for attempt in range(3):  # Retry hingga 3 kali
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
            logger.warning(f"Attempt {attempt + 1} failed for {email}")
        except Exception as e:
            logger.error(f"Error creating account for {email} on attempt {attempt + 1}: {e}")

    return None  # Jika semua retry gagal
    
async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE, command_name):
    user_id = update.effective_user.id
    user_id_str = str(user_id)

    admins = load_data(ADMIN_FILE)
    members = load_data(MEMBER_FILE)

    if user_id_str == ADMIN_UTAMA:
        role = "Admin Utama"
    elif user_id_str in admins and is_active(admins, user_id):
        role = "Admin"
    elif user_id_str in members and is_active(members, user_id):
        role = "Member"
    else:
        role = "Non-Member"

    role_access = {
        "Non-Member": ["/start"],
        "Member": ["/start", "/create"],
        "Admin": ["/start", "/create", "/add_member", "/delete_member", "/add_admin", "/delete_admin"],
        "Admin Utama": ["/start", "/create", "/add_member", "/delete_member", "/add_admin", "/delete_admin", "/check"]
    }

    if command_name not in role_access[role]:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return False
    return True

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/start"):
        return

    user_id = update.effective_user.id
    admins = load_data(ADMIN_FILE)
    members = load_data(MEMBER_FILE)

    if str(user_id) == ADMIN_UTAMA or (str(user_id) in admins and is_active(admins, user_id)):
        status = "Admin"
        expiry = admins.get(str(user_id), "2099-12-31 23:59:59")
    elif str(user_id) in members and is_active(members, user_id):
        status = "Member"
        expiry = members[str(user_id)]
    else:
        status = "Tidak Berlangganan"
        expiry = "N/A"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await update.message.reply_text(
        f"ID Telegram Anda: {user_id}\n"
        f"Status: {status}\n"
        f"Masa Aktif: {expiry}\n"
        f"Waktu Saat Ini: {now}"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/check"):
        return

    admins = load_data(ADMIN_FILE)
    members = load_data(MEMBER_FILE)

    admin_list = "\n".join([f"{k} | {v}" for k, v in admins.items()])
    member_list = "\n".join([f"{k} | {v}" for k, v in members.items()])

    await update.message.reply_text(
        f"Admin:\n{admin_list}\n\nMember:\n{member_list}"
    )

async def create_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/create"):
        return

    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Format perintah salah. Gunakan: /create <password> <jumlah_akun>")
            return

        password = args[0]
        jumlah_akun = int(args[1])

        if jumlah_akun > 50 or jumlah_akun <= 0:
            await update.message.reply_text("Jumlah akun harus antara 1 hingga 50.")
            return

        await update.message.reply_text("Membuat akun, mohon tunggu beberapa saat...")
        created_accounts = await run_regist_code(password, jumlah_akun)

        if created_accounts:
            file_content = "\n".join(created_accounts)
            file_name = f"account_{jumlah_akun}vidio.txt"
            file_buffer = BytesIO()
            file_buffer.write(file_content.encode("utf-8"))
            file_buffer.seek(0)

            await update.message.reply_document(
                document=InputFile(file_buffer, file_name),
                caption=f"{len(created_accounts)} akun berhasil dibuat."
            )
        else:
            await update.message.reply_text("Gagal membuat akun. Silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Jumlah akun harus berupa angka.")
    except Exception as e:
        logger.error(f"Error in /create: {e}")
        await update.message.reply_text(f"Terjadi kesalahan: {str(e)}")

async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/add_member"):
        return

    try:
        new_member_id, duration = context.args[0], int(context.args[1])
        members = load_data(MEMBER_FILE)
        members[new_member_id] = add_days(duration)
        save_data(MEMBER_FILE, members)
        await update.message.reply_text(f"Member {new_member_id} telah ditambahkan selama {duration} hari.")
    except (IndexError, ValueError):
        await update.message.reply_text("Gunakan format: /add_member idtelegram durasi")

async def delete_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/delete_member"):
        return

    try:
        member_id = context.args[0]
        members = load_data(MEMBER_FILE)
        if member_id in members:
            del members[member_id]
            save_data(MEMBER_FILE, members)
            await update.message.reply_text(f"Member {member_id} telah dihapus.")
        else:
            await update.message.reply_text(f"ID {member_id} bukan member.")
    except IndexError:
        await update.message.reply_text("Gunakan format: /delete_member idtelegram")

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/add_admin"):
        return

    try:
        new_admin_id, duration = context.args[0], int(context.args[1])
        admins = load_data(ADMIN_FILE)
        admins[new_admin_id] = add_days(duration)
        save_data(ADMIN_FILE, admins)
        await update.message.reply_text(f"Admin {new_admin_id} telah ditambahkan selama {duration} hari.")
    except (IndexError, ValueError):
        await update.message.reply_text("Gunakan format: /add_admin idtelegram durasi")

async def delete_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await handle_command(update, context, "/delete_admin"):
        return

    try:
        remove_admin_id = context.args[0]
        if remove_admin_id == ADMIN_UTAMA:
            await update.message.reply_text("Admin utama tidak dapat dihapus.")
            return

        admins = load_data(ADMIN_FILE)
        if remove_admin_id in admins:
            del admins[remove_admin_id]
            save_data(ADMIN_FILE, admins)
            await update.message.reply_text(f"Admin {remove_admin_id} telah dihapus.")
        else:
            await update.message.reply_text(f"ID {remove_admin_id} bukan admin.")
    except IndexError:
        await update.message.reply_text("Gunakan format: /delete_admin idtelegram")

# Main Function
def main():
    load_dotenv()
    keep_alive()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("Token bot tidak ditemukan.")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create", create_account_handler))
    application.add_handler(CommandHandler("add_member", add_member))
    application.add_handler(CommandHandler("delete_member", delete_member))
    application.add_handler(CommandHandler("add_admin", add_admin))
    application.add_handler(CommandHandler("delete_admin", delete_admin))
    application.add_handler(CommandHandler("check", check))

    logger.info("Bot berjalan...")
    application.run_polling()

if __name__ == "__main__":
    if not os.path.exists(ADMIN_FILE):
        save_data(ADMIN_FILE, {ADMIN_UTAMA: "2099-12-31 23:59:59"})
    if not os.path.exists(MEMBER_FILE):
        save_data(MEMBER_FILE, {})

    main()
