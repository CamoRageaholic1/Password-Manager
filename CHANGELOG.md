# Changelog

## [2.0.0] - 2025-11-26

### Added
- ✅ **Unique salt per user** - Fixed critical security issue with hardcoded salt
- ✅ **Password strength indicator** - Visual feedback on password quality
- ✅ **Built-in password generator** - Generate secure passwords with customizable length
- ✅ **List all passwords** - View all stored credentials at once
- ✅ **Search functionality** - Find passwords by service or username
- ✅ **Update passwords** - Modify existing entries
- ✅ **Delete passwords** - Remove entries with confirmation
- ✅ **Backup system** - Manual database backups
- ✅ **Clipboard support** - Copy passwords with pyperclip (optional)
- ✅ **Color-coded UI** - Enhanced interface with colorama (optional)
- ✅ **Better error handling** - Graceful failure recovery
- ✅ **Timestamps** - Track creation and update times
- ✅ **URL and notes fields** - Store additional information
- ✅ **requirements.txt** - Proper dependency management

### Security
- 🔒 **Fixed hardcoded salt vulnerability**
- 🔒 **Improved encryption key derivation**
- 🔒 **Password strength validation**
- 🔒 **3 attempts limit for master password**

### Changed
- Reorganized code into class structure
- Improved menu system
- Enhanced user experience with colors
- Better input validation

## [1.0.0] - Initial Release

### Features
- Basic password storage
- Master password protection
- Fernet encryption
- SQLite database
