# Password Manager

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Security-Encrypted-red?style=for-the-badge&logo=lock&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Simple command-line password manager with encryption - securely store and retrieve passwords using a master password.

## 🎯 Purpose

A lightweight, educational password manager demonstrating encryption best practices. Perfect for learning about cryptography, password security, and building CLI tools in Python.

## ✨ Features

- ✅ **Master Password Protection** - Single password to access all stored credentials
- ✅ **Strong Encryption** - Uses Fernet (AES 128-bit) symmetric encryption
- ✅ **Password Derivation** - PBKDF2 with 100,000 iterations for key generation
- ✅ **SQLite Storage** - Local encrypted database
- ✅ **Simple CLI** - Easy-to-use command-line interface
- ✅ **Hidden Input** - Passwords hidden during entry

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CamoRageaholic1/Password-Manager.git
   cd Password-Manager
   ```

2. **Install dependencies**
   ```bash
   pip install cryptography
   ```

### First Run

```bash
python Password_Manager.py
```

You'll be prompted to set a master password on first run.

## 📖 Usage Guide

### Main Menu Options

```
Options: 1. Add a password 2. Get a password 3. Quit
```

### 1. Add a Password

Store credentials for a service:

```bash
Enter your choice: 1
Enter the service name: GitHub
Enter the username: myusername
Enter the password: ********
Password added successfully.
```

### 2. Retrieve a Password

Get stored credentials:

```bash
Enter your choice: 2
Enter the service name: GitHub
Username: myusername, Password: mypassword123
```

### 3. Quit

Exit the program safely.

## 🔒 Security Features

### Encryption

- **Algorithm:** Fernet (symmetric encryption using AES in CBC mode with 128-bit key)
- **Key Derivation:** PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Password Hashing:** SHA-256 for master password verification

### Security Flow

1. **Master Password Set** → SHA-256 hash stored locally
2. **User Login** → Master password verified against hash
3. **Key Generation** → PBKDF2 derives encryption key from master password
4. **Storage** → Passwords encrypted with Fernet before SQLite storage
5. **Retrieval** → Passwords decrypted only after master password verification

## ⚠️ Important Security Notes

### Educational Purpose

This is an **educational project** demonstrating encryption concepts. For production use, consider:

- Commercial password managers (1Password, Bitwarden, LastPass)
- Additional security layers (2FA, hardware keys)
- Cloud sync and backup capabilities
- Security audits and penetration testing

### Security Considerations

- 🔒 Master password is **never stored** - only its hash
- 🔒 Encryption key is **derived** each time from master password
- 🔒 Passwords are encrypted **before storage**
- ⚠️ Database file (`passwords.db`) should be kept secure
- ⚠️ Loss of master password = **permanent data loss**
- ⚠️ No password recovery mechanism

### Best Practices

1. **Choose a strong master password**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Use a passphrase (e.g., "correct-horse-battery-staple")

2. **Backup your database**
   ```bash
   cp passwords.db passwords_backup.db
   ```

3. **Keep the database secure**
   - Don't commit `passwords.db` to version control
   - Store on encrypted disk if possible
   - Use full disk encryption (FileVault on macOS)

4. **Regular updates**
   - Change master password periodically
   - Update stored passwords regularly
   - Keep Python and dependencies updated

## 📁 Project Structure

```
Password-Manager/
├── Password_Manager.py        # Main application
├── passwords.db               # Encrypted password database (created on first run)
├── master_password_hash.txt   # Master password hash (created on first run)
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## 🔧 Dependencies

```bash
cryptography>=41.0.0  # Encryption library
```

Install with:
```bash
pip install cryptography
```

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'"
Install the cryptography library:
```bash
pip install cryptography
```

### "Incorrect master password"
Ensure you're entering the correct master password. There's no recovery mechanism.

### Database corruption
If `passwords.db` becomes corrupted, restore from backup or start fresh (will lose all stored passwords).

## 🤝 Contributing

Contributions welcome! Ideas for improvements:

- Add password generator integration
- Implement password strength checker
- Add export/import functionality
- Create GUI version
- Add password update tracking
- Implement password sharing (encrypted)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided for educational purposes. Use at your own risk. The author is not responsible for any data loss or security breaches. For sensitive data, use professionally audited password managers.

## 📫 Support

- 🐛 **Bug Reports:** Open an issue on GitHub
- 💡 **Feature Requests:** Open an issue with the "enhancement" label

---

**Author:** David Osisek (CamoZeroDay)  
**Made with ❤️ for learning cryptography and security**
