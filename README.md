# Password Manager v2.5 - Integrated Edition

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Security-Encrypted-red?style=for-the-badge&logo=lock&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.5-blue?style=for-the-badge)

**All-in-one password manager with integrated secure password generator - everything in a single file!**

**Author:** David Osisek (CamoZeroDay)

---

## 🎉 What's New in v2.5

### ⚡ Integrated Password Generator
- ✅ **Full generator built-in** - No separate files needed
- ✅ **Generate during add** - Create passwords when adding entries
- ✅ **Generate during update** - Create new passwords when updating
- ✅ **Standalone generation** - Use generator without saving
- ✅ **Multiple modes** - Standard, memorable, custom
- ✅ **Single file solution** - Everything in one 800-line file

### 🚀 Generation Options

**1. Standard Password**
```
K@9mPx#L2nQ$8vY&Tz4W
  ████████ Very Strong
```

**2. Memorable Passphrase**
```
Alpha-Bravo-Charlie-Delta42
  ███████ Strong
```

**3. Custom Options**
- Choose character types
- Exclude ambiguous characters
- Set length (12-64)

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/CamoRageaholic1/Password-Manager.git
cd Password-Manager
pip install -r requirements.txt

# Run integrated v2.5
python password_manager_v2.5.py
```

---

## ✨ Features

### Password Management
1. **Add** - Store passwords with integrated generation
2. **Get** - Retrieve passwords with copy
3. **List** - View all stored passwords
4. **Search** - Find by service/username
5. **Update** - Modify with new generation
6. **Delete** - Remove with confirmation
7. **Generate** - Standalone password creation
8. **Export** - Export to JSON
9. **Settings** - Configure backups

### Security
- 🔒 Fernet (AES 128-bit) encryption
- 🔒 PBKDF2 (100,000 iterations)
- 🔒 SHA-256 master password hashing
- 🔒 Unique salt per installation
- 🔒 Cryptographic password generation

---

## 🎯 Usage

### Adding a Password with Generation

```
Service: github.com
Username: john@example.com

Password Options:
1. Generate Standard Password
2. Generate Memorable Passphrase
3. Enter Manually

Choice: 1
Length (12-64, default 16): 20

Generated: K@9mPx#L2nQ$8vY&Tz4W
  ████████ Very Strong
✓ Copied to clipboard!

✓ Password for 'github.com' added!
```

### Standalone Password Generation

```
Generation Options:
1. Standard Password
2. Memorable Passphrase
3. Custom Options

Choice: 2
Words (3-8, default 4): 5

Generated: Alpha-Bravo-Charlie-Delta-Echo42
  ███████ Strong
✓ Copied!
```

---

## 📦 Requirements

### Required
- Python 3.8+
- cryptography>=41.0.0

### Optional
- pyperclip>=1.8.2 (clipboard)
- colorama>=0.4.6 (colors)

```bash
pip install -r requirements.txt
```

---

## 📁 Files

```
Password-Manager/
├── password_manager_v2.5.py  # ⭐ USE THIS (integrated)
├── password_manager_v2.0.py  # v2.0 (separate files)
├── Password_Manager.py       # v1.0 (legacy)
├── requirements.txt          # Dependencies
├── CHANGELOG.md              # Version history
├── README.md                 # This file
└── LICENSE                   # MIT License
```

---

## 📊 Version Comparison

| Feature | v2.0 | v2.5 |
|---------|------|------|
| Password Manager | ✅ | ✅ |
| Password Generator | ❌ Separate | ✅ Integrated |
| Generation During Add | ❌ | ✅ |
| Generation During Update | ❌ | ✅ |
| Standalone Generation | ❌ | ✅ |
| Multiple Generation Modes | ❌ | ✅ |
| Export Functionality | ❌ | ✅ |
| Single File | ❌ | ✅ |

---

## 🔒 Security

### Encryption
- **Algorithm:** Fernet (AES 128-bit CBC)
- **Key Derivation:** PBKDF2-HMAC-SHA256
- **Iterations:** 100,000
- **Salt:** 16 bytes (unique per installation)

### Password Generation
- **Random Source:** `secrets` module (cryptographic)
- **Character Variety:** Guaranteed all types
- **Shuffling:** SystemRandom (secure)
- **Ambiguous Exclusion:** Optional (il1Lo0O)

---

## 🛠️ Troubleshooting

**Import errors:**
```bash
pip install --upgrade cryptography pyperclip colorama
```

**Clipboard not working:**
```bash
pip install pyperclip
# Linux: sudo apt-install xclip
```

---

## 🤝 Contributing

Contributions welcome!

**Ideas for v3.0:**
- Browser extension integration
- Cloud sync support
- Biometric authentication
- Password expiration reminders
- Import from other managers

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 📈 Evolution

**v1.0:** Basic password storage  
**v2.0:** Added features, fixed security  
**v2.5:** Integrated generator, single file

---

## ⭐ Why v2.5?

### Single File Benefits
- ✅ **Easy Distribution** - Share one file
- ✅ **No Dependencies** - Between own files
- ✅ **Simple Deployment** - Just run it
- ✅ **Complete Solution** - Everything included

### Integrated Generator Benefits
- ✅ **Seamless Workflow** - Generate while adding
- ✅ **Multiple Modes** - Standard, memorable, custom
- ✅ **Strength Analysis** - Visual feedback
- ✅ **No Context Switching** - Stay in manager

---

**Author:** David Osisek (CamoZeroDay)  
**Version:** 2.5 - Integrated Edition  
**License:** MIT

**🔒 One file. Complete solution. Maximum security. 🔒**
