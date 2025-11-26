#!/usr/bin/env python3
"""
Password Manager v2.5 - Integrated Edition
Author: David Osisek (CamoZeroDay)
Description: All-in-one password manager with integrated secure password generator

Combines Password Manager v2.0 + Password Generator v2.0 into a single file
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
import argparse
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
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = ""
    class Style:
        RESET_ALL = BRIGHT = ""

# Constants
VERSION = "2.5.0"
DB_FILE = 'passwords.db'
SALT_FILE = 'salt.key'
MASTER_FILE = 'master.hash'
BACKUP_DIR = 'backups'
CONFIG_FILE = 'config.json'

class PasswordGenerator:
    """Integrated secure password generator with cryptographic randomness"""
    
    def __init__(self):
        self.uppercase = string.ascii_uppercase
        self.lowercase = string.ascii_lowercase
        self.digits = string.digits
        self.symbols = string.punctuation
        self.ambiguous = 'il1Lo0O'
    
    def generate(self, length=16, use_upper=True, use_lower=True, 
                use_digits=True, use_symbols=True, exclude_ambiguous=True):
        """Generate a secure password using cryptographic randomness"""
        chars = ''
        required = []
        
        if use_upper:
            upper_chars = self.uppercase
            if exclude_ambiguous:
                upper_chars = ''.join(c for c in upper_chars if c not in self.ambiguous)
            chars += upper_chars
            required.append(secrets.choice(upper_chars))
        
        if use_lower:
            lower_chars = self.lowercase
            if exclude_ambiguous:
                lower_chars = ''.join(c for c in lower_chars if c not in self.ambiguous)
            chars += lower_chars
            required.append(secrets.choice(lower_chars))
        
        if use_digits:
            digit_chars = self.digits
            if exclude_ambiguous:
                digit_chars = ''.join(c for c in digit_chars if c not in self.ambiguous)
            chars += digit_chars
            required.append(secrets.choice(digit_chars))
        
        if use_symbols:
            chars += self.symbols
            required.append(secrets.choice(self.symbols))
        
        if not chars:
            raise ValueError("At least one character type must be selected")
        
        if length < len(required):
            length = len(required)
        
        password = required.copy()
        password += [secrets.choice(chars) for _ in range(length - len(required))]
        
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def generate_memorable(self, words=4, separator='-', capitalize=True, add_number=True):
        """Generate a memorable passphrase"""
        word_list = [
            'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot',
            'golf', 'hotel', 'india', 'juliet', 'kilo', 'lima',
            'mike', 'november', 'oscar', 'papa', 'quebec', 'romeo',
            'sierra', 'tango', 'uniform', 'victor', 'whiskey', 'xray',
            'yankee', 'zulu', 'coffee', 'python', 'tiger', 'ocean',
            'mountain', 'river', 'forest', 'desert', 'cloud', 'thunder',
            'lightning', 'rainbow', 'sunset', 'sunrise', 'winter', 'summer'
        ]
        
        selected = [secrets.choice(word_list) for _ in range(words)]
        
        if capitalize:
            selected = [w.capitalize() for w in selected]
        
        passphrase = separator.join(selected)
        
        if add_number:
            passphrase += str(secrets.randbelow(100))
        
        return passphrase
    
    def check_strength(self, password):
        """Analyze password strength - returns (score, feedback)"""
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Too short (min 8)")
        
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Add numbers")
        
        if any(c in string.punctuation for c in password):
            score += 1
        else:
            feedback.append("Add symbols")
        
        return min(score, 5), feedback
    
    def display_strength(self, password):
        """Display password strength with visual indicator"""
        score, feedback = self.check_strength(password)
        
        labels = [
            ("Very Weak", Fore.RED),
            ("Weak", Fore.RED),
            ("Fair", Fore.YELLOW),
            ("Good", Fore.YELLOW),
            ("Strong", Fore.GREEN),
            ("Very Strong", Fore.GREEN)
        ]
        
        label, color = labels[score]
        bars = "█" * score + "░" * (5 - score)
        
        print(f"  {color}{bars} {label}{Style.RESET_ALL}")
        print(f"  Length: {len(password)} characters")
        
        if feedback:
            print(f"\n{Fore.YELLOW}Suggestions:{Style.RESET_ALL}")
            for tip in feedback:
                print(f"  • {tip}")

class PasswordManager:
    """Integrated password manager with built-in generator"""
    
    def __init__(self):
        self.conn = None
        self.key = None
        self.generator = PasswordGenerator()
        self.config = self.load_config()
        self.setup_db()
        
        print(f"\n{Fore.CYAN}╔{'═'*48}╗")
        print(f"║  Password Manager v{VERSION} - Integrated    ║")
        print(f"║  By David Osisek (CamoZeroDay){' '*11}║")
        print(f"╚{'═'*48}╝{Style.RESET_ALL}\n")
        
        if not CLIPBOARD:
            print(f"{Fore.YELLOW}Note: Install pyperclip for clipboard support{Style.RESET_ALL}\n")
    
    def load_config(self):
        """Load configuration"""
        default = {'auto_backup': True, 'backup_count': 5}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.print_error(f"Failed to save config: {e}")
    
    def setup_db(self):
        """Initialize database"""
        try:
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
            c.execute('CREATE INDEX IF NOT EXISTS idx_service ON accounts(service)')
            self.conn.commit()
        except Exception as e:
            self.print_error(f"Database setup failed: {e}")
            sys.exit(1)
    
    def get_salt(self):
        """Get or create encryption salt"""
        if os.path.exists(SALT_FILE):
            with open(SALT_FILE, 'rb') as f:
                return f.read()
        salt = secrets.token_bytes(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        return salt
    
    def hash_password(self, pw):
        """Hash master password"""
        return hashlib.sha256(pw.encode()).hexdigest()
    
    def get_key(self, pw):
        """Derive encryption key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.get_salt(),
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(pw.encode()))
    
    def encrypt(self, data):
        """Encrypt data"""
        try:
            return Fernet(self.key).encrypt(data.encode())
        except Exception as e:
            self.print_error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, data):
        """Decrypt data"""
        try:
            return Fernet(self.key).decrypt(data).decode()
        except:
            return None
    
    def verify_master(self):
        """Verify or set master password"""
        if not os.path.exists(MASTER_FILE):
            return self.set_master()
        
        with open(MASTER_FILE, 'r') as f:
            stored = f.read().strip()
        
        for attempt in range(3):
            pw = getpass.getpass(f"{Fore.CYAN}Master password: {Style.RESET_ALL}")
            if self.hash_password(pw) == stored:
                self.key = self.get_key(pw)
                self.print_success("Authenticated!")
                return True
            
            remaining = 2 - attempt
            if remaining > 0:
                self.print_error(f"Incorrect. {remaining} attempts remaining.")
            else:
                self.print_error("Too many failed attempts.")
                return False
        
        return False
    
    def set_master(self):
        """Set new master password"""
        self.print_info("Setting up Password Manager...")
        
        while True:
            pw1 = getpass.getpass(f"{Fore.CYAN}Set master password: {Style.RESET_ALL}")
            
            score, _ = self.generator.check_strength(pw1)
            if score < 3:
                self.print_warning("Password is weak. Use a stronger password.")
                self.generator.display_strength(pw1)
                continue
            
            pw2 = getpass.getpass(f"{Fore.CYAN}Confirm: {Style.RESET_ALL}")
            
            if pw1 == pw2:
                with open(MASTER_FILE, 'w') as f:
                    f.write(self.hash_password(pw1))
                self.key = self.get_key(pw1)
                self.print_success("Master password set!")
                return True
            else:
                self.print_error("Passwords don't match.")
    
    def add(self):
        """Add new password"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Add New Password':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        try:
            service = input(f"{Fore.CYAN}Service: {Style.RESET_ALL}").strip()
            if not service:
                self.print_error("Service name required.")
                return
            
            username = input(f"{Fore.CYAN}Username: {Style.RESET_ALL}").strip()
            if not username:
                self.print_error("Username required.")
                return
            
            # Password generation options
            print(f"\n{Fore.CYAN}Password Options:{Style.RESET_ALL}")
            print("1. Generate Standard Password")
            print("2. Generate Memorable Passphrase")
            print("3. Enter Manually")
            
            choice = input(f"\n{Fore.CYAN}Choice (1-3): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                try:
                    length = int(input(f"{Fore.CYAN}Length (12-64, default 16): {Style.RESET_ALL}") or "16")
                    length = max(12, min(64, length))
                except:
                    length = 16
                
                password = self.generator.generate(length)
                print(f"\n{Fore.GREEN}Generated: {password}{Style.RESET_ALL}")
                self.generator.display_strength(password)
                
                if CLIPBOARD:
                    try:
                        pyperclip.copy(password)
                        self.print_success("Copied to clipboard!")
                    except:
                        pass
            
            elif choice == '2':
                try:
                    words = int(input(f"{Fore.CYAN}Words (3-8, default 4): {Style.RESET_ALL}") or "4")
                    words = max(3, min(8, words))
                except:
                    words = 4
                
                password = self.generator.generate_memorable(words=words)
                print(f"\n{Fore.GREEN}Generated: {password}{Style.RESET_ALL}")
                self.generator.display_strength(password)
                
                if CLIPBOARD:
                    try:
                        pyperclip.copy(password)
                        self.print_success("Copied to clipboard!")
                    except:
                        pass
            
            else:
                password = getpass.getpass(f"{Fore.CYAN}Password: {Style.RESET_ALL}")
                if not password:
                    self.print_error("Password required.")
                    return
                self.generator.display_strength(password)
            
            url = input(f"\n{Fore.CYAN}URL (optional): {Style.RESET_ALL}").strip()
            notes = input(f"{Fore.CYAN}Notes (optional): {Style.RESET_ALL}").strip()
            
            encrypted = self.encrypt(password)
            if not encrypted:
                return
            
            now = datetime.now().isoformat()
            c = self.conn.cursor()
            c.execute('INSERT INTO accounts VALUES (NULL,?,?,?,?,?,?,?)',
                     (service, username, encrypted, url, notes, now, now))
            self.conn.commit()
            
            self.print_success(f"Password for '{service}' added!")
            
            if self.config['auto_backup']:
                self.backup(silent=True)
        
        except Exception as e:
            self.print_error(f"Failed to add: {e}")
    
    def get(self):
        """Retrieve password"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Get Password':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        service = input(f"{Fore.CYAN}Service: {Style.RESET_ALL}").strip()
        
        try:
            c = self.conn.cursor()
            c.execute('SELECT * FROM accounts WHERE service LIKE ?', (f'%{service}%',))
            
            results = c.fetchall()
            if not results:
                self.print_warning(f"No passwords found for '{service}'.")
                return
            
            for row in results:
                id_, svc, user, enc_pw, url, notes, created, updated = row
                pw = self.decrypt(enc_pw)
                
                if pw:
                    print(f"\n{Fore.YELLOW}{'─'*60}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}ID:{Style.RESET_ALL} {id_}")
                    print(f"{Fore.CYAN}Service:{Style.RESET_ALL} {svc}")
                    print(f"{Fore.CYAN}Username:{Style.RESET_ALL} {user}")
                    print(f"{Fore.CYAN}Password:{Style.RESET_ALL} {pw}")
                    self.generator.display_strength(pw)
                    if url: print(f"{Fore.CYAN}URL:{Style.RESET_ALL} {url}")
                    if notes: print(f"{Fore.CYAN}Notes:{Style.RESET_ALL} {notes}")
                    print(f"{Fore.CYAN}Created:{Style.RESET_ALL} {created}")
                    print(f"{Fore.CYAN}Updated:{Style.RESET_ALL} {updated}")
                    print(f"{Fore.YELLOW}{'─'*60}{Style.RESET_ALL}")
                    
                    if CLIPBOARD:
                        if input(f"\n{Fore.CYAN}Copy password? (y/n): {Style.RESET_ALL}").lower() == 'y':
                            try:
                                pyperclip.copy(pw)
                                self.print_success("Copied!")
                            except:
                                pass
        
        except Exception as e:
            self.print_error(f"Failed to retrieve: {e}")
    
    def list_all(self):
        """List all passwords"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'All Stored Passwords':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        try:
            c = self.conn.cursor()
            c.execute('SELECT id, service, username, created FROM accounts ORDER BY service')
            results = c.fetchall()
            
            if not results:
                self.print_warning("No passwords stored yet.")
                return
            
            print(f"{Fore.CYAN}{'ID':<6}{'Service':<25}{'Username':<20}{'Created':<15}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'─'*66}{Style.RESET_ALL}")
            
            for row in results:
                id_, svc, user, created = row
                created_short = created[:10] if created else ""
                print(f"{id_:<6}{svc:<25}{user:<20}{created_short:<15}")
            
            print(f"{Fore.YELLOW}{'─'*66}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Total: {len(results)} passwords{Style.RESET_ALL}")
        
        except Exception as e:
            self.print_error(f"Failed to list: {e}")
    
    def search(self):
        """Search passwords"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Search Passwords':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        query = input(f"{Fore.CYAN}Search: {Style.RESET_ALL}").strip()
        
        try:
            c = self.conn.cursor()
            c.execute('''SELECT id, service, username, url FROM accounts 
                        WHERE service LIKE ? OR username LIKE ? ORDER BY service''',
                     (f'%{query}%', f'%{query}%'))
            
            results = c.fetchall()
            if not results:
                self.print_warning(f"No results for '{query}'.")
                return
            
            print(f"\n{Fore.CYAN}{'ID':<6}{'Service':<25}{'Username':<20}{'URL':<15}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'─'*66}{Style.RESET_ALL}")
            
            for row in results:
                id_, svc, user, url = row
                url_short = (url[:12] + "...") if url and len(url) > 15 else (url or "")
                print(f"{id_:<6}{svc:<25}{user:<20}{url_short:<15}")
            
            print(f"{Fore.YELLOW}{'─'*66}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Found: {len(results)} results{Style.RESET_ALL}")
        
        except Exception as e:
            self.print_error(f"Search failed: {e}")
    
    def update(self):
        """Update password"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Update Password':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        try:
            id_ = input(f"{Fore.CYAN}ID to update: {Style.RESET_ALL}").strip()
            
            c = self.conn.cursor()
            c.execute('SELECT service, username FROM accounts WHERE id=?', (id_,))
            result = c.fetchone()
            
            if not result:
                self.print_error(f"No password with ID {id_}.")
                return
            
            print(f"\n{Fore.GREEN}Updating: {result[0]} ({result[1]}){Style.RESET_ALL}\n")
            
            new_user = input(f"{Fore.CYAN}New username (Enter to skip): {Style.RESET_ALL}").strip()
            
            print(f"\n{Fore.CYAN}New Password Options:{Style.RESET_ALL}")
            print("1. Generate Standard")
            print("2. Generate Memorable")
            print("3. Enter Manually")
            print("4. Keep Current")
            
            choice = input(f"\n{Fore.CYAN}Choice (1-4): {Style.RESET_ALL}").strip()
            
            new_pw = None
            if choice == '1':
                try:
                    length = int(input(f"{Fore.CYAN}Length (default 16): {Style.RESET_ALL}") or "16")
                except:
                    length = 16
                new_pw = self.generator.generate(length)
                print(f"\n{Fore.GREEN}Generated: {new_pw}{Style.RESET_ALL}")
                if CLIPBOARD:
                    try:
                        pyperclip.copy(new_pw)
                        self.print_success("Copied!")
                    except:
                        pass
            elif choice == '2':
                new_pw = self.generator.generate_memorable()
                print(f"\n{Fore.GREEN}Generated: {new_pw}{Style.RESET_ALL}")
                if CLIPBOARD:
                    try:
                        pyperclip.copy(new_pw)
                        self.print_success("Copied!")
                    except:
                        pass
            elif choice == '3':
                new_pw = getpass.getpass(f"{Fore.CYAN}New password: {Style.RESET_ALL}")
            
            updates = []
            params = []
            
            if new_user:
                updates.append("username=?")
                params.append(new_user)
            
            if new_pw:
                encrypted = self.encrypt(new_pw)
                if encrypted:
                    updates.append("password=?")
                    params.append(encrypted)
            
            if updates:
                updates.append("updated=?")
                params.append(datetime.now().isoformat())
                params.append(id_)
                
                c.execute(f"UPDATE accounts SET {','.join(updates)} WHERE id=?", params)
                self.conn.commit()
                self.print_success("Updated!")
                
                if self.config['auto_backup']:
                    self.backup(silent=True)
            else:
                self.print_warning("No changes made.")
        
        except Exception as e:
            self.print_error(f"Update failed: {e}")
    
    def delete(self):
        """Delete password"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Delete Password':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        try:
            id_ = input(f"{Fore.CYAN}ID to delete: {Style.RESET_ALL}").strip()
            
            c = self.conn.cursor()
            c.execute('SELECT service, username FROM accounts WHERE id=?', (id_,))
            result = c.fetchone()
            
            if not result:
                self.print_error(f"No password with ID {id_}.")
                return
            
            print(f"\n{Fore.RED}⚠ Deleting: {result[0]} ({result[1]}){Style.RESET_ALL}")
            confirm = input(f"{Fore.CYAN}Type 'DELETE' to confirm: {Style.RESET_ALL}")
            
            if confirm == 'DELETE':
                c.execute('DELETE FROM accounts WHERE id=?', (id_,))
                self.conn.commit()
                self.print_success("Deleted!")
                
                if self.config['auto_backup']:
                    self.backup(silent=True)
            else:
                self.print_warning("Cancelled.")
        
        except Exception as e:
            self.print_error(f"Delete failed: {e}")
    
    def generate_only(self):
        """Standalone password generation"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Password Generator':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Generation Options:{Style.RESET_ALL}")
        print("1. Standard Password")
        print("2. Memorable Passphrase")
        print("3. Custom Options")
        
        choice = input(f"\n{Fore.CYAN}Choice (1-3): {Style.RESET_ALL}").strip()
        
        try:
            if choice == '1':
                length = int(input(f"{Fore.CYAN}Length (12-64, default 16): {Style.RESET_ALL}") or "16")
                length = max(12, min(64, length))
                pw = self.generator.generate(length)
            
            elif choice == '2':
                words = int(input(f"{Fore.CYAN}Words (3-8, default 4): {Style.RESET_ALL}") or "4")
                words = max(3, min(8, words))
                pw = self.generator.generate_memorable(words=words)
            
            elif choice == '3':
                print(f"\n{Fore.CYAN}Customize:{Style.RESET_ALL}")
                length = int(input("Length (8-64): ") or "16")
                use_upper = input("Uppercase? (Y/n): ").lower() != 'n'
                use_lower = input("Lowercase? (Y/n): ").lower() != 'n'
                use_digits = input("Numbers? (Y/n): ").lower() != 'n'
                use_symbols = input("Symbols? (Y/n): ").lower() != 'n'
                exclude_amb = input("Exclude ambiguous (il1Lo0O)? (Y/n): ").lower() != 'n'
                
                pw = self.generator.generate(
                    length=length,
                    use_upper=use_upper,
                    use_lower=use_lower,
                    use_digits=use_digits,
                    use_symbols=use_symbols,
                    exclude_ambiguous=exclude_amb
                )
            else:
                self.print_error("Invalid choice.")
                return
            
            print(f"\n{Fore.GREEN}Generated Password:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{pw}{Style.RESET_ALL}\n")
            self.generator.display_strength(pw)
            
            if CLIPBOARD:
                if input(f"\n{Fore.CYAN}Copy? (y/n): {Style.RESET_ALL}").lower() == 'y':
                    try:
                        pyperclip.copy(pw)
                        self.print_success("Copied!")
                    except:
                        pass
        
        except ValueError as e:
            self.print_error(f"Error: {e}")
    
    def backup(self, silent=False):
        """Create database backup"""
        try:
            Path(BACKUP_DIR).mkdir(exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup = f"{BACKUP_DIR}/backup_{ts}.db"
            
            import shutil
            shutil.copy2(DB_FILE, backup)
            
            # Cleanup old backups
            backups = sorted(Path(BACKUP_DIR).glob('backup_*.db'), 
                           key=os.path.getmtime, reverse=True)
            for old in backups[self.config['backup_count']:]:
                old.unlink()
            
            if not silent:
                self.print_success(f"Backup: {backup}")
        
        except Exception as e:
            if not silent:
                self.print_error(f"Backup failed: {e}")
    
    def export(self):
        """Export passwords to JSON"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{'Export Passwords':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        try:
            filename = input(f"{Fore.CYAN}Filename (default: export.json): {Style.RESET_ALL}").strip()
            filename = filename or 'export.json'
            
            c = self.conn.cursor()
            c.execute('SELECT * FROM accounts')
            
            data = []
            for row in c.fetchall():
                _, svc, user, enc_pw, url, notes, created, updated = row
                pw = self.decrypt(enc_pw)
                if pw:
                    data.append({
                        'service': svc,
                        'username': user,
                        'password': pw,
                        'url': url,
                        'notes': notes,
                        'created': created,
                        'updated': updated
                    })
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            
            self.print_success(f"Exported {len(data)} passwords to {filename}")
            self.print_warning("⚠ File contains unencrypted passwords! Keep secure!")
        
        except Exception as e:
            self.print_error(f"Export failed: {e}")
    
    def settings(self):
        """Settings menu"""
        while True:
            print(f"\n{Fore.MAGENTA}{'='*60}")
            print(f"{'Settings':^60}")
            print(f"{'='*60}{Style.RESET_ALL}\n")
            
            print(f"1. Auto Backup: {Fore.GREEN if self.config['auto_backup'] else Fore.RED}"
                  f"{'Enabled' if self.config['auto_backup'] else 'Disabled'}{Style.RESET_ALL}")
            print(f"2. Backup Count: {Fore.CYAN}{self.config['backup_count']}{Style.RESET_ALL}")
            print(f"3. Create Manual Backup")
            print(f"4. Back to Main Menu")
            
            choice = input(f"\n{Fore.CYAN}Choice: {Style.RESET_ALL}")
            
            if choice == '1':
                self.config['auto_backup'] = not self.config['auto_backup']
                self.save_config()
                status = "enabled" if self.config['auto_backup'] else "disabled"
                self.print_success(f"Auto backup {status}.")
            elif choice == '2':
                try:
                    count = int(input(f"{Fore.CYAN}Count (1-20): {Style.RESET_ALL}"))
                    self.config['backup_count'] = max(1, min(20, count))
                    self.save_config()
                    self.print_success(f"Backup count set to {self.config['backup_count']}.")
                except ValueError:
                    self.print_error("Invalid number.")
            elif choice == '3':
                self.backup()
            elif choice == '4':
                break
    
    def menu(self):
        """Display main menu"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"  Password Manager v{VERSION}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print(f" 1. Add Password")
        print(f" 2. Get Password")
        print(f" 3. List All Passwords")
        print(f" 4. Search Passwords")
        print(f" 5. Update Password")
        print(f" 6. Delete Password")
        print(f" 7. Generate Password")
        print(f" 8. Export Passwords")
        print(f" 9. Settings")
        print(f"10. Quit\n")
    
    def run(self):
        """Main program loop"""
        if not self.verify_master():
            return
        
        actions = {
            '1': self.add,
            '2': self.get,
            '3': self.list_all,
            '4': self.search,
            '5': self.update,
            '6': self.delete,
            '7': self.generate_only,
            '8': self.export,
            '9': self.settings
        }
        
        while True:
            try:
                self.menu()
                choice = input(f"{Fore.CYAN}Choice: {Style.RESET_ALL}").strip()
                
                if choice == '10':
                    self.print_success("Goodbye!")
                    break
                elif choice in actions:
                    actions[choice]()
                    input(f"\n{Fore.YELLOW}Press Enter...{Style.RESET_ALL}")
                else:
                    self.print_error("Invalid choice.")
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
                break
            except Exception as e:
                self.print_error(f"Error: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.conn:
            self.conn.close()
    
    # Helper methods
    def print_success(self, text):
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    
    def print_error(self, text):
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    
    def print_warning(self, text):
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    
    def print_info(self, text):
        print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")

def main():
    """Main entry point"""
    pm = PasswordManager()
    try:
        pm.run()
    finally:
        pm.cleanup()

if __name__ == "__main__":
    main()
