# smsxml2html-appstyle

**Fork of KermMartian's smsxml2html with mobile app-style conversation list and enhanced large conversation handling**

*Note: Significant portions of this codebase were generated and enhanced with AI assistance (Claude by Anthropic).*

## Overview

This tool converts SMS/MMS message backup XML files from [SMS Backup & Restore by SyncTech Pty Ltd](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US) into beautiful, browsable HTML files with a phone-like interface. Unlike the original smsxml2html, this fork provides:

- **Modern mobile app-style interface** with conversation list view
- **Embedded images** - all MMS images are base64-encoded directly into the HTML (no separate image files)
- **Smart handling of huge conversations** - automatic chunking and pagination for better performance
- **Group conversation support** - properly displays group MMS threads with participant tracking
- **Dark mode** - toggle between light and dark themes
- **Search functionality** - quickly find conversations by name or phone number
- **User-friendly conversion GUI** - no command line knowledge required

## What's New in This Fork

### Interface Improvements
- Phone-style conversation list with avatars and message counts
- Click-to-expand conversations instead of separate HTML files
- Real-time search filtering
- Back button navigation

### Technical Enhancements
- **Intelligent conversation chunking**: Large conversations (>50MB) are automatically split into paginated chunks for smooth loading
- **Progressive rendering**: Chunked conversations load page-by-page with Previous/Next buttons
- **Embedded images**: All images are base64-encoded into the HTML - no external files needed
- **Group conversation parsing**: Properly identifies and displays group MMS participants
- **Month-based navigation**: Jump links to navigate through conversation history by month
- **Contact name mapping**: Intelligently maps phone numbers to contact names throughout conversations
- **Adds Python 3.x support**

### User Experience
- **GUI wrapper** (`Run_SMSXML2HTML_Conversion.py`) - simple point-and-click interface
- **Real-time progress**: Live conversion output with success dialog
- **Smart folder naming**: Uses XML filename with auto-incrementing numbers to prevent overwrites
- **One-click folder opening**: Automatically opens output folder when conversion completes

## Files Included

### Core Scripts
- **`smsxml2html.py`** - Main conversion engine (AI-enhanced)
- **`Run_SMSXML2HTML_Conversion.py`** - User-friendly GUI wrapper (AI-generated)

### Output Structure
```
output/
└── YourBackupFile_0001/
    ├── messages.html          # Main conversation list interface
    └── conv_files/            # Individual conversation data files
        ├── conv_xxxxx.js      # Small conversations (single file)
        ├── conv_yyyyy_chunk1.js    # Large conversations (chunked)
        ├── conv_yyyyy_chunk2.js
        └── conv_yyyyy_header.js
```

## Installation

### Requirements
- Python 3.6 or higher
- lxml library
- tkinter (included with Python on Windows/Mac; on Linux may need `python3-tk`)

### Setup
```bash
# Clone the repository
git clone https://github.com/hondaguy900/smsxml2html-appstyle.git
cd smsxml2html-appstyle

# Install dependencies
pip install lxml

# On Linux, if GUI doesn't work, install tkinter:
# Ubuntu/Debian: sudo apt-get install python3-tk
# Fedora: sudo dnf install python3-tkinter
```

## Usage

### Option 1: GUI Interface (Recommended)
```bash
python Run_SMSXML2HTML_Conversion.py
```
1. Click "Browse" to select your SMS backup XML file
2. Enter your phone number (11 digits: 18005551234)
3. Choose output folder (defaults to `./output`)
4. Click "Convert to HTML"
5. Click "Open Folder" when conversion completes
6. Open messages.html in your web browser (Chrome or Edge recommended)

### Option 2: Command Line
```bash
python smsxml2html.py -o <output_dir> -n <your_phone_number> <input_file.xml>
```

**Parameters:**
- `-o <output_dir>`: Directory for output files (e.g., `./output`)
- `-n <your_phone_number>`: Your phone number in 11-digit format with leading 1 (e.g., `18005551234`)
- `<input_file.xml>`: Path to your SMS Backup & Restore XML file

**Example:**
```bash
python smsxml2html.py -o ./output -n 15551234567 my_messages.xml
```

## How to Create a Backup

1. Install [SMS Backup & Restore by SyncTech Pty Ltd](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US) on your Android device
2. Open the app and tap "Backup"
3. Change backup options as desired (i.e. date range, selected conversations, etc.)
4. Choose backup location (local or cloud)
5. After the backup is completed, transfer the generated XML file to your computer
6. Run this tool to convert it to HTML

## Features in Detail

### Supported Image Formats
- JPEG/JPG
- PNG
- GIF
- WebP
- AVIF
- BMP
- TIFF
- SVG
- ICO

### Conversation Handling
- **1-on-1 conversations**: Displayed with contact name or formatted phone number
- **Group conversations**: Shows all participants with "Group · X people" subtitle
- **Unknown contacts**: Displayed with formatted phone number and "#" avatar

### Performance Optimizations
- **Streaming XML parser**: Handles large backup files without excessive memory usage
- **Automatic chunking**: Splits conversations over 50MB into manageable pages
- **Lazy loading**: Conversation data loads only when clicked
- **Memory-efficient**: Clears processed XML elements during parsing

### Dark Mode
- Persistent preference saved in browser localStorage
- Optimized color scheme for comfortable night viewing
- Toggle button in header (moon/sun icon)

## Browser Compatibility

The generated HTML works in all modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

**Note**: Works entirely offline once generated - no internet connection required to view.

## Troubleshooting

### "XML file not found" error
- Verify the file path is correct
- Ensure the XML file isn't corrupted
- Try re-exporting from SMS Backup & Restore

### Images not displaying
- Verify MMS backup was enabled in SMS Backup & Restore
- Check that images were included in the XML (file size should be large)
- Some very old MMS formats may not be supported

### Conversion is slow
- Large backups (years of messages with many images) can take several minutes
- Progress is displayed in real-time in the GUI
- The resulting HTML files will load quickly despite conversion time

### Phone number format issues
- Use 11 digits with leading 1: `18005551234`
- Remove all dashes, spaces, and parentheses
- For international numbers, adjust format accordingly

## Known Limitations

- Does not support voice message MMS (audio files)
- Video MMS attachments are not displayed
- Contact photos are not included (only text names)
- Deleted messages are not recoverable

## Credits

- **Original smsxml2html**: [Christopher Mitchell, Ph.D.](https://github.com/KermMartian/smsxml2html)
- **This fork**: hondaguy900
- **AI assistance**: Significant code generation and enhancement by Claude (Anthropic)
- **SMS Backup & Restore app**: [SyncTech Pty Ltd](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US)

## Privacy & Data Handling

- This tool processes SMS/MMS backup files **locally on your computer**. All conversion happens offline.
- No data is sent to external servers
- All generated HTML files remain on your local machine
- You are responsible for securing your own message backups and converted files
- **Important**: SMS backup files contain private conversations. Handle these files with appropriate care and do not share generated HTML files publicly unless you've removed all personal information.

## License

This project maintains the same license as the original smsxml2html project. Please refer to the original repository for licensing terms.

## Contributing

Contributions are welcome! This fork specifically focuses on:
- UI/UX improvements for conversation viewing
- Performance optimizations for large datasets
- Enhanced group conversation support
- Better contact name mapping

Please open issues or pull requests on GitHub.

## Changelog

### v2.0 (This Fork)
- Complete UI redesign with phone-style interface
- Added GUI wrapper for easy use
- Implemented conversation chunking for large files
- Added embedded base64 images (no external files)
- Group conversation support with participant tracking
- Dark mode with persistent preference
- Search and filter functionality
- Month-based jump navigation
- Progressive loading for chunked conversations
- Smart contact name mapping across SMS and MMS
- Auto-incrementing folder names to prevent overwrites
- Adds Python 3.x support

### v1.0 (Original)
- Basic XML to HTML conversion
- Separate HTML files per conversation
- External image file generation
- Command-line only interface
- Requires Python 2.x

---

**Repository**: https://github.com/hondaguy900/smsxml2html-appstyle  
**Original**: https://github.com/KermMartian/smsxml2html
