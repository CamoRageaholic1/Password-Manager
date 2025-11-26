# Password Manager v2.0

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Security-Encrypted-red?style=for-the-badge&logo=lock&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.0-blue?style=for-the-badge)

**Secure CLI password manager with Fernet encryption, password generation, and comprehensive features.**

**Author:** David Osisek (CamoZeroDay)

---

## 🎉 What's New in v2.0

### 🔒 Security Fixes
- ✅ **Fixed critical hardcoded salt vulnerability** - Now uses unique salt per user
- ✅ **Cryptographically secure password generation** - Uses `secrets` module
- ✅ **Improved key derivation** - PBKDF2 with 100,000 iterations
- ✅ **Master password attempts limit** - 3 attempts before lockout

### ✨ New Features
- ✅ **Built-in password generator** - Generate secure passwords instantly
- ✅ **Password strength analyzer** - Visual feedback on password quality
- ✅ **List all passwords** - View all stored credentials
- ✅ **Search functionality** - Find passwords by service/username
- ✅ **Update passwords** - Modify existing entries
- ✅ **Delete with confirmation** - Safely remove entries
- ✅ **Backup system** - Manual database backups
- ✅ **Clipboard support** - Copy passwords instantly (optional)
- ✅ **Color-coded UI** - Enhanced interface (optional)
- ✅ **Timestamps** - Track creation/update times
- ✅ **URL and notes fields** - Store additional info

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/CamoRageaholic1/Password-Manager.git
cd Password-Manager
pip install -r requirements.txt

# Run v2.0
python password_manager_v2.py
```

---

## 📚 Features

### Core Security
- **Fernet Encryption** (AES 128-bit)
- **PBKDF2** with 100,000 iterations
- **SHA-256** master password hashing
- **Unique salt** per installation

### Password Management
1. **Add** - Store new passwords with optional generation
2. **Get** - Retrieve passwords with search
3. **List** - View all stored passwords
4. **Search** - Find by service name or username
5. **Update** - Modify existing entries
6. **Delete** - Remove with confirmation
7. **Generate** - Create secure passwords
8. **Backup** - Manual database backup

### Password Strength
```
Password: MyP@ssw0rd123
  Strength: ████░ Good
  Length: 13 characters
```

---

## 🎯 Usage

### Main Menu
```
==================================================
  Password Manager v2.0
==================================================

1. Add Password
2. Get Password
3. List All
4. Search
5. Update
6. Delete
7. Generate Password
8. Backup
9. Quit
```

### Adding a Password
```
Service: github.com
Username: john@example.com
Generate password? (y/n): y
Length (12-64, default 16): 20
Generated: K@9mPx#L2nQ$8vY&Tz4W
  Strength: █████ Very Strong
✓ Copied to clipboard
✓ Added
```

---

## 📦 Requirements

### Required
- Python 3.8+
- cryptography>=41.0.0

### Optional
- pyperclip>=1.8.2 (clipboard support)
- colorama>=0.4.6 (colored output)

```bash
# Install all
pip install -r requirements.txt

# Or minimal
pip install cryptography
```

---

## 📁 Files

```
Password-Manager/
├── password_manager_v2.py    # v2.0 (use this)
├── Password_Manager.py       # v1.0 (legacy)
├── requirements.txt          # Dependencies
├── CHANGELOG.md              # Version history
├── README.md                 # This file
├── LICENSE                   # MIT License
├── passwords.db              # Database (created)
├── salt.key                  # Encryption salt (created)
├── master.hash               # Master password (created)
└── backups/                  # Backup directory
```

---

## 🔒 Security

### What's Protected
- ✅ Passwords encrypted with Fernet
- ✅ Master password never stored (only hash)
- ✅ Unique salt per installation
- ✅ 100,000 PBKDF2 iterations

### Best Practices
✅ **DO:**
- Use strong master password (12+ chars)
- Backup database regularly
- Keep salt.key secure
- Use generated passwords

❌ **DON'T:**
- Share master password
- Reuse passwords
- Store database on shared systems
- Lose your master password (no recovery!)

---

## 🔧 Troubleshooting

**Import errors:**
```bash
pip install --upgrade cryptography pyperclip colorama
```

**Decryption fails:**
- Verify master password
- Check salt.key exists
- Restore from backup

**Clipboard not working:**
```bash
pip install pyperclip
# Linux: sudo apt-install xclip
```

---

## 📊 v1.0 vs v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Encryption | ✅ | ✅ |
| Hardcoded Salt | ❌ | ✅ Fixed |
| Generate Passwords | ❌ | ✅ |
| Strength Analysis | ❌ | ✅ |
| List/Search | ❌ | ✅ |
| Update/Delete | ❌ | ✅ |
| Backup | ❌ | ✅ |
| Clipboard | ❌ | ✅ |
| Colors | ❌ | ✅ |

---

## 🤝 Contributing

Contributions welcome!

**Ideas for v3.0:**
- Export/import functionality
- Master password change
- Auto-backup
- Password expiration
- Browser extension

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

## ⚠️ Educational Disclaimer

Designed for **educational purposes** and personal use. For production, consider:
- 1Password
- Bitwarden
- KeePass
- LastPass

---

**Author:** David Osisek (CamoZeroDay)  
**Version:** 2.0  
**License:** MIT

**🔒 Stay secure. Backup your data. Use strong passwords. 🔒**
