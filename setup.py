#!/bin/env python3
# Code by: youtube.com/theunknon

"""
Script to join a specific Telegram group using Telethon.
"""

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError

# Colors for console
RE = "\033[1;31m"
GR = "\033[1;32m"
CY = "\033[1;36m"

def banner():
    """Display banner in terminal."""
    print(f"""{GR}By: Zulkarnaen""")

def join_group():
    """Join a specific Telegram group."""
    banner()
    try:
        # Replace with your Telegram API credentials
        api_id = "YOUR_API_ID"  # Replace with your API ID
        api_hash = "YOUR_API_HASH"  # Replace with your API Hash
        phone = "YOUR_PHONE_NUMBER"  # Replace with your phone number
        group_invite_link = "https://t.me/+KlDbihW_jWw1NmI9"  # Replace with the invite link to your group

        client = TelegramClient(phone, api_id, api_hash)
        client.connect()

        if not client.is_user_authorized():
            print(RE + "[!] Login required.")
            client.send_code_request(phone)
            code = input(GR + "[+] Enter the code sent to your phone: " + CY)
            client.sign_in(phone, code)

        print(GR + "[+] Joining the Telegram group...")
        try:
            client(JoinChannelRequest(group_invite_link))
            print(GR + "[+] Successfully joined the group!")
        except UserAlreadyParticipantError:
            print(CY + "[+] Already a participant in the group.")
        except Exception as e:
            print(RE + "[!] Error while joining the group:", e)
        finally:
            client.disconnect()

    except Exception as e:
        print(RE + "[!] An error occurred:", e)

if __name__ == "__main__":
    join_group()
