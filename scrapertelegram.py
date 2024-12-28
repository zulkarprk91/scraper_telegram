from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os
import sys
import configparser
import csv
import time

# Warna untuk konsol
RE = "\033[1;31m"
GR = "\033[1;32m"
CY = "\033[1;36m"

def banner():
    """Menampilkan banner."""
    print(f"""By : Zulkarnaen""")

# Periksa file konfigurasi
if not os.path.exists('config.data'):
    print(RE + "[!] 'config.data' tidak ditemukan. Jalankan 'python3 setup.py' untuk mengatur API.\n")
    sys.exit(1)

# Memuat konfigurasi
cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
except KeyError:
    print(RE + "[!] Konfigurasi tidak valid. Periksa file 'config.data'.\n")
    sys.exit(1)

# Koneksi ke Telegram
with TelegramClient(phone, api_id, api_hash) as client:
    if not client.is_user_authorized():
        client.send_code_request(phone)
        banner()
        code = input(GR + '[+] Masukkan kode verifikasi: ' + CY)
        client.sign_in(phone, code)

    os.system('clear')
    banner()
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    # Ambil daftar grup
    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except:
            continue

    # Menampilkan grup yang tersedia
    print(GR + '[+] Pilih grup untuk mengambil anggota:' + RE)
    for idx, g in enumerate(groups):
        print(f"{GR}[{CY}{idx}{GR}]{CY} - {g.title}")

    print('')
    try:
        g_index = int(input(GR + "[+] Masukkan nomor grup: " + RE))
        target_group = groups[g_index]
    except (ValueError, IndexError):
        print(RE + "[!] Nomor grup tidak valid.")
        sys.exit(1)

    # Mengambil anggota grup
    print(GR + '[+] Mengambil anggota grup...')
    time.sleep(1)
    all_participants = client.get_participants(target_group, aggressive=True)

    # Menyimpan data anggota ke file CSV
    print(GR + '[+] Menyimpan anggota ke file...')
    time.sleep(1)
    with open("members.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        for user in all_participants:
            username = user.username if user.username else ""
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])

    print(GR + '[+] Anggota berhasil disimpan ke "members.csv".')
