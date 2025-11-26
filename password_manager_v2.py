#!/usr/bin/env python3
"""
Password Manager v2.0
Author: David Osisek (CamoZeroDay)
Description: Secure password manager with encryption, generation, and backup
"""

import sqlite3
import base64
import os
import sys
import json
import secrets
import string
import hashlib
import getpass
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

try:
    import pyperclip
    CLIPBOARD = True
except ImportError:
    CLIPBOARD = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS = True
except ImportError:
    COLORS = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = ""
    class Style:
        RESET_ALL = ""

DB_FILE = 'passwords.db'
SALT_FILE = 'salt.key'
MASTER_FILE = 'master.hash'
BACKUP_DIR = 'backups'

class PasswordManager:
    def __init__(self):
        self.conn = None
        self.key = None
        self.setup_db()
    
    def setup_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                service TEXT,
                username TEXT,
                password TEXT,
                url TEXT,
                notes TEXT,
                created TEXT,
                updated TEXT
            )
        ''')
        self.conn.commit()
    
    def get_salt(self):
        if os.path.exists(SALT_FILE):
            with open(SALT_FILE, 'rb') as f:
                return f.read()
        salt = secrets.token_bytes(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        return salt
    
    def hash_password(self, pw):
        return hashlib.sha256(pw.encode()).hexdigest()
    
    def get_key(self, pw):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.get_salt(),
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(pw.encode()))
    
    def encrypt(self, data):
        return Fernet(self.key).encrypt(data.encode())
    
    def decrypt(self, data):
        try:
            return Fernet(self.key).decrypt(data).decode()
        except:
            return None
    
    def check_strength(self, pw):
        score = 0
        if len(pw) >= 8: score += 1
        if len(pw) >= 12: score += 1
        if any(c.isupper() for c in pw): score += 1
        if any(c.islower() for c in pw): score += 1
        if any(c.isdigit() for c in pw): score += 1
        if any(c in string.punctuation for c in pw): score += 1
        return min(score, 5)
    
    def show_strength(self, pw):
        s = self.check_strength(pw)
        labels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
        colors = [Fore.RED, Fore.RED, Fore.YELLOW, Fore.YELLOW, Fore.GREEN, Fore.GREEN]
        bars = "█" * s + "░" * (5 - s)
        print(f"  Strength: {colors[s]}{bars} {labels[s]}{Style.RESET_ALL}")
    
    def generate_password(self, length=16):
        chars = string.ascii_letters + string.digits + string.punctuation
        # Remove ambiguous
        chars = ''.join(c for c in chars if c not in 'il1Lo0O')
        pw = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice(string.punctuation)
        ]
        pw += [secrets.choice(chars) for _ in range(length - 4)]
        secrets.SystemRandom().shuffle(pw)
        return ''.join(pw)
    
    def verify_master(self):
        if not os.path.exists(MASTER_FILE):
            return self.set_master()
        
        with open(MASTER_FILE, 'r') as f:
            stored = f.read().strip()
        
        for _ in range(3):
            pw = getpass.getpass(f"{Fore.CYAN}Master password: {Style.RESET_ALL}")
            if self.hash_password(pw) == stored:
                self.key = self.get_key(pw)
                print(f"{Fore.GREEN}✓ Authenticated{Style.RESET_ALL}")
                return True
            print(f"{Fore.RED}✗ Incorrect{Style.RESET_ALL}")
        return False
    
    def set_master(self):
        print(f"{Fore.CYAN}Setting up Password Manager...{Style.RESET_ALL}\n")
        while True:
            pw1 = getpass.getpass("Set master password: ")
            if self.check_strength(pw1) < 3:
                print(f"{Fore.YELLOW}⚠ Weak password. Use stronger.{Style.RESET_ALL}")
                continue
            pw2 = getpass.getpass("Confirm: ")
            if pw1 == pw2:
                with open(MASTER_FILE, 'w') as f:
                    f.write(self.hash_password(pw1))
                self.key = self.get_key(pw1)
                print(f"{Fore.GREEN}✓ Master password set{Style.RESET_ALL}")
                return True
            print(f"{Fore.RED}✗ Passwords don't match{Style.RESET_ALL}")
    
    def add(self):
        print(f"\n{Fore.MAGENTA}=== Add Password ==={Style.RESET_ALL}\n")
        service = input("Service: ").strip()
        username = input("Username: ").strip()
        
        if input("Generate password? (y/n): ").lower() == 'y':
            try:
                length = int(input("Length (12-64, default 16): ") or "16")
                length = max(12, min(64, length))
            except:
                length = 16
            password = self.generate_password(length)
            print(f"{Fore.GREEN}Generated: {password}{Style.RESET_ALL}")
            self.show_strength(password)
            if CLIPBOARD:
                try:
                    pyperclip.copy(password)
                    print(f"{Fore.GREEN}✓ Copied to clipboard{Style.RESET_ALL}")
                except:
                    pass
        else:
            password = getpass.getpass("Password: ")
            self.show_strength(password)
        
        url = input("URL (optional): ").strip()
        notes = input("Notes (optional): ").strip()
        
        encrypted = self.encrypt(password)
        now = datetime.now().isoformat()
        
        c = self.conn.cursor()
        c.execute('INSERT INTO accounts VALUES (NULL,?,?,?,?,?,?,?)',
                 (service, username, encrypted, url, notes, now, now))
        self.conn.commit()
        print(f"{Fore.GREEN}✓ Added{Style.RESET_ALL}")
    
    def get(self):
        print(f"\n{Fore.MAGENTA}=== Get Password ==={Style.RESET_ALL}\n")
        service = input("Service: ").strip()
        
        c = self.conn.cursor()
        c.execute('SELECT * FROM accounts WHERE service LIKE ?', (f'%{service}%',))
        
        for row in c.fetchall():
            id_, svc, user, enc_pw, url, notes, created, updated = row
            pw = self.decrypt(enc_pw)
            if pw:
                print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}ID:{Style.RESET_ALL} {id_}")
                print(f"{Fore.CYAN}Service:{Style.RESET_ALL} {svc}")
                print(f"{Fore.CYAN}Username:{Style.RESET_ALL} {user}")
                print(f"{Fore.CYAN}Password:{Style.RESET_ALL} {pw}")
                self.show_strength(pw)
                if url: print(f"{Fore.CYAN}URL:{Style.RESET_ALL} {url}")
                if notes: print(f"{Fore.CYAN}Notes:{Style.RESET_ALL} {notes}")
                print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
                
                if CLIPBOARD and input("\nCopy? (y/n): ").lower() == 'y':
                    try:
                        pyperclip.copy(pw)
                        print(f"{Fore.GREEN}✓ Copied{Style.RESET_ALL}")
                    except:
                        pass
    
    def list_all(self):
        print(f"\n{Fore.MAGENTA}=== All Passwords ==={Style.RESET_ALL}\n")
        c = self.conn.cursor()
        c.execute('SELECT id, service, username FROM accounts ORDER BY service')
        
        print(f"{Fore.CYAN}{'ID':<6}{'Service':<25}{'Username':<30}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*61}{Style.RESET_ALL}")
        
        for row in c.fetchall():
            print(f"{row[0]:<6}{row[1]:<25}{row[2]:<30}")
        
        print(f"{Fore.YELLOW}{'-'*61}{Style.RESET_ALL}")
    
    def search(self):
        print(f"\n{Fore.MAGENTA}=== Search ==={Style.RESET_ALL}\n")
        q = input("Search: ").strip()
        
        c = self.conn.cursor()
        c.execute('SELECT id, service, username FROM accounts WHERE service LIKE ? OR username LIKE ?',
                 (f'%{q}%', f'%{q}%'))
        
        for row in c.fetchall():
            print(f"ID {row[0]}: {row[1]} ({row[2]})")
    
    def update(self):
        print(f"\n{Fore.MAGENTA}=== Update Password ==={Style.RESET_ALL}\n")
        id_ = input("ID: ").strip()
        
        c = self.conn.cursor()
        c.execute('SELECT service, username FROM accounts WHERE id=?', (id_,))
        result = c.fetchone()
        
        if not result:
            print(f"{Fore.RED}✗ Not found{Style.RESET_ALL}")
            return
        
        print(f"Updating: {result[0]} ({result[1]})\n")
        
        new_user = input("New username (Enter to skip): ").strip()
        
        if input("Generate new password? (y/n): ").lower() == 'y':
            try:
                length = int(input("Length (default 16): ") or "16")
            except:
                length = 16
            new_pw = self.generate_password(length)
            print(f"{Fore.GREEN}Generated: {new_pw}{Style.RESET_ALL}")
            if CLIPBOARD:
                try:
                    pyperclip.copy(new_pw)
                    print(f"{Fore.GREEN}✓ Copied{Style.RESET_ALL}")
                except:
                    pass
        else:
            new_pw = getpass.getpass("New password (Enter to skip): ")
        
        updates = []
        params = []
        
        if new_user:
            updates.append("username=?")
            params.append(new_user)
        if new_pw:
            updates.append("password=?")
            params.append(self.encrypt(new_pw))
        
        if updates:
            updates.append("updated=?")
            params.append(datetime.now().isoformat())
            params.append(id_)
            
            c.execute(f"UPDATE accounts SET {','.join(updates)} WHERE id=?", params)
            self.conn.commit()
            print(f"{Fore.GREEN}✓ Updated{Style.RESET_ALL}")
    
    def delete(self):
        print(f"\n{Fore.MAGENTA}=== Delete Password ==={Style.RESET_ALL}\n")
        id_ = input("ID: ").strip()
        
        c = self.conn.cursor()
        c.execute('SELECT service, username FROM accounts WHERE id=?', (id_,))
        result = c.fetchone()
        
        if not result:
            print(f"{Fore.RED}✗ Not found{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}Delete: {result[0]} ({result[1]}){Style.RESET_ALL}")
        if input("Type DELETE to confirm: ") == "DELETE":
            c.execute('DELETE FROM accounts WHERE id=?', (id_,))
            self.conn.commit()
            print(f"{Fore.GREEN}✓ Deleted{Style.RESET_ALL}")
    
    def backup(self):
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = f"{BACKUP_DIR}/backup_{ts}.db"
        
        import shutil
        shutil.copy2(DB_FILE, backup)
        print(f"{Fore.GREEN}✓ Backup: {backup}{Style.RESET_ALL}")
    
    def gen_only(self):
        print(f"\n{Fore.MAGENTA}=== Generate Password ==={Style.RESET_ALL}\n")
        try:
            length = int(input("Length (12-64, default 16): ") or "16")
            length = max(12, min(64, length))
        except:
            length = 16
        
        pw = self.generate_password(length)
        print(f"\n{Fore.GREEN}Password: {pw}{Style.RESET_ALL}\n")
        self.show_strength(pw)
        
        if CLIPBOARD:
            try:
                pyperclip.copy(pw)
                print(f"{Fore.GREEN}✓ Copied to clipboard{Style.RESET_ALL}")
            except:
                pass
    
    def menu(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"  Password Manager v2.0")
        print(f"{'='*50}{Style.RESET_ALL}\n")
        print("1. Add Password")
        print("2. Get Password")
        print("3. List All")
        print("4. Search")
        print("5. Update")
        print("6. Delete")
        print("7. Generate Password")
        print("8. Backup")
        print("9. Quit\n")
    
    def run(self):
        if not self.verify_master():
            return
        
        actions = {
            '1': self.add,
            '2': self.get,
            '3': self.list_all,
            '4': self.search,
            '5': self.update,
            '6': self.delete,
            '7': self.gen_only,
            '8': self.backup
        }
        
        while True:
            try:
                self.menu()
                choice = input(f"{Fore.CYAN}Choice: {Style.RESET_ALL}").strip()
                
                if choice == '9':
                    print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                    break
                elif choice in actions:
                    actions[choice]()
                    input(f"\n{Fore.YELLOW}Press Enter...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Invalid{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
                break
    
    def cleanup(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    print(f"{Fore.CYAN}")
    print("  ╔═══════════════════════════════════╗")
    print("  ║  Password Manager v2.0            ║")
    print("  ║  By David Osisek (CamoZeroDay)    ║")
    print("  ╚═══════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    if not CLIPBOARD:
        print(f"{Fore.YELLOW}Note: Install pyperclip for clipboard support{Style.RESET_ALL}")
    
    pm = PasswordManager()
    try:
        pm.run()
    finally:
        pm.cleanup()
