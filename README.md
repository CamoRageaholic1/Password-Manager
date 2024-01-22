##Password Manager - By David Osisek

import sqlite3
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import getpass
import hashlib

def hash_master_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_master_password(stored_hash, input_password):
    input_hash = hash_master_password(input_password)
    return input_hash == stored_hash

def get_key(password_provided):
    password = password_provided.encode()
    salt = b'\x1a\xdb\xcf\x1d\x80\x91\xcc\x85\x10\x1d\x2b\x2f\x6e\xdc\x0e\x20'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def encrypt_message(message, key):
    return Fernet(key).encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    return Fernet(key).decrypt(encrypted_message).decode()

def main():
    # Database setup
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (service text, username text, password text)''')
    conn.commit()

    # Check if a master password is set
    try:
        with open('master_password_hash.txt', 'r') as file:
            stored_hash = file.read()
    except FileNotFoundError:
        # Set a new master password if not set
        new_master_password = getpass.getpass("Set your master password: ")
        hashed_password = hash_master_password(new_master_password)
        with open('master_password_hash.txt', 'w') as file:
            file.write(hashed_password)
        print("Master password set.")
        return

    # Verify the master password
    master_password = getpass.getpass("Enter your master password: ")
    if not verify_master_password(stored_hash, master_password):
        print("Incorrect master password.")
        return

    key = get_key(master_password)

    while True:
        print("\nOptions: 1. Add a password 2. Get a password 3. Quit")
        choice = input("Enter your choice: ")
        if choice == "1":
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = getpass.getpass("Enter the password: ")
            encrypted_password = encrypt_message(password, key)
            c.execute('INSERT INTO accounts VALUES (?, ?, ?)', (service, username, encrypted_password))
            conn.commit()
            print("Password added successfully.")
        elif choice == "2":
            service = input("Enter the service name: ")
            c.execute('SELECT username, password FROM accounts WHERE service=?', (service,))
            for row in c.fetchall():
                username, password = row
                decrypted_password = decrypt_message(password, key)
                print(f"Username: {username}, Password: {decrypted_password}")
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
            
        if __name__ == "__main__":
    main()
