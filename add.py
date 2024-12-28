#!/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import rpcerrorlist
import telethon
import configparser
import os
import sys
import csv
import traceback
import time
import random

# Warna untuk output
re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

def banner():
    print(f"""
{gr}Telegram Member Adder
By: Zulkarnaen
""")

# Konfigurasi API Telegram
cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    banner()
    print(re + "[!] Run 'python3 setup.py' first to configure API credentials.\n")
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    os.system('clear')
    banner()
    client.sign_in(phone, input(gr + '[+] Enter the code: ' + re))

# Load anggota dari file CSV tanpa validasi
os.system('clear')
banner()
if len(sys.argv) < 2:
    print(re + "[!] Usage: python3 add_members.py members.csv")
    sys.exit(1)

input_file = sys.argv[1]
users = []
try:
    with open(input_file, encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)  # Lewati header
        for row in rows:
            if len(row) < 4:
                print(re + f"[!] Skipping invalid row: {row}")
                continue
            user = {
                'username': row[0],
                'id': int(row[1]) if row[1].isdigit() else None,
                'access_hash': int(row[2]) if row[2].isdigit() else None,
                'name': row[3],
            }
            users.append(user)
except FileNotFoundError:
    print(re + f"[!] File not found: {input_file}")
    sys.exit(1)

# Dapatkan grup
chats = []
last_date = None
chunk_size = 200
groups = []

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

# Pilih grup target
print(gr + "[+] Available groups:")
for i, group in enumerate(groups):
    print(gr + f"[{cy}{i}{gr}] {cy}{group.title}")

g_index = input(gr + "[+] Enter the group number: " + re)
try:
    target_group = groups[int(g_index)]
except (ValueError, IndexError):
    print(re + "[!] Invalid group number. Exiting.")
    sys.exit(1)

target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

# Pilih mode
print(gr + "[1] Add members by user ID\n[2] Add members by username")
mode = input(gr + "Input: " + re)
if mode not in ("1", "2"):
    print(re + "[!] Invalid mode selected. Exiting.")
    sys.exit(1)

# Mulai menambahkan anggota
MAX_MEMBERS_PER_DAY = 500000  # Disarankan membatasi 50 anggota per hari
DAILY_MEMBER_LIMIT = min(MAX_MEMBERS_PER_DAY, len(users))

print(gr + f"[+] Starting to add up to {DAILY_MEMBER_LIMIT} members today...")

n = 0
success_count = 0
fail_count = 0

for user in users[:DAILY_MEMBER_LIMIT]:
    try:
        print(gr + f"[+] Adding {user['username'] or user['id']}")
        if mode == "1" and user['username']:
            user_to_add = client.get_input_entity(user['username'])
        elif mode == "2" and user['id'] and user['access_hash']:
            user_to_add = InputPeerUser(user['id'], user['access_hash'])
        else:
            print(re + "[!] Skipping invalid user.")
            fail_count += 1
            continue

        client(InviteToChannelRequest(target_group_entity, [user_to_add]))
        print(gr + "[+] Successfully added member!")
        success_count += 1

        # Tunggu acak untuk menghindari PeerFloodError
        print(gr + "[+] Waiting for speed seconds...")
        time.sleep(random.randint(5, 10))

    except telethon.errors.rpcerrorlist.PeerFloodError:
        print(re + "[!] Rate limit hit. Halting operations for safety.")
        time.sleep(30)  # Tunggu 1 jam sebelum melanjutkan
        break
    except Exception as e:
        print(re + f"[!] Unexpected error: {e}")
        traceback.print_exc()
        fail_count += 1
        # Mengurangi jeda waktu jika terjadi kesalahan berulang
        print(gr + "[+] Waiting for 60-120 seconds to prevent flooding...")
        time.sleep(random.randint(5, 10))
        continue

print(gr + f"[+] Finished. Successfully added {success_count} members, {fail_count} failed.")
