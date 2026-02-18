import os
from cryptography.fernet import Fernet

vault_dir = os.path.expanduser("~/ZemiV1/vault")
key_path = os.path.join(vault_dir, "master.key")

with open(key_path, "rb") as f:
    key = f.read()

fernet = Fernet(key)

password = input("Paste your Proton Bridge IMAP password: ").strip()
encrypted = fernet.encrypt(password.encode())

out_path = os.path.join(vault_dir, "proton.enc")
with open(out_path, "wb") as f:
    f.write(encrypted)

print(f"✅ Bridge password saved to vault/proton.enc")
