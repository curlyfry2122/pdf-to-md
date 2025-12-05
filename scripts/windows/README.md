# PDF Auto Converter - Automatic Startup Setup

This guide will help you set up the PDF Auto Converter to run automatically when you log into Windows, without requiring administrator privileges.

## Quick Start

1. Ensure watchdog is installed: `pip install watchdog`
2. Double-click `setup_autostart.bat`
3. Restart Windows (or log out and back in)
4. Test by dropping a PDF into the `inputs/` folder

## What This Does

The auto converter will:
- **Start automatically** when you log into Windows
- **Run silently** in the background (no visible window)
- **Monitor** the `inputs/` folder continuously
- **Auto-convert** any PDF files dropped into `inputs/`
- **Archive** processed PDFs to `archive/` with timestamps
- **Log** all activity to `outputs/auto_convert.log`

## Files Created

- **start_auto_converter.bat** - Main script that launches the converter
- **start_auto_converter_silent.vbs** - Wrapper that runs the batch file hidden
- **setup_autostart.bat** - One-click setup script (run this once)
- **AUTOSTART_SETUP.md** - This documentation

## Detailed Setup Instructions

### Step 1: Install Dependencies

```bash
pip install watchdog
```

Verify installation:
```bash
pip show watchdog
```

### Step 2: Run Setup Script

1. Double-click `setup_autostart.bat`
2. You should see a success message
3. The script copies the launcher to your Windows Startup folder

The Startup folder location:
```
C:\Users\jdevine\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### Step 3: Restart or Test Manually

**Option A: Restart Windows**
- The converter will start automatically on next login

**Option B: Test Without Restarting**
- Double-click `start_auto_converter_silent.vbs` to start it manually
- Or run: `start_auto_converter.bat` to see console output

### Step 4: Verify It's Working

1. Check Task Manager:
   - Press `Ctrl+Shift+Esc`
   - Go to "Details" tab
   - Look for `python.exe` or `pythonw.exe`

2. Check the log file:
   - Open `outputs/auto_convert.log`
   - Should see: "WATCHING: c:\Users\jdevine\dev\pdf-to-md\inputs"

3. Test conversion:
   - Drop a PDF into `inputs/` folder
   - Wait a few seconds
   - Check `outputs/` for the converted markdown file
   - Check `archive/` for the original PDF (it will be moved there)

## How It Works

```
Windows Login
    ↓
Startup Folder runs start_auto_converter_silent.vbs
    ↓
VBS script launches start_auto_converter.bat (hidden)
    ↓
Batch file starts Python script: auto_convert.py
    ↓
Python script watches inputs/ folder using watchdog library
    ↓
When PDF is detected → Convert → Archive
```

## Usage

Once set up, simply:
1. Drop PDF files into `inputs/` folder
2. Conversion happens automatically
3. Find converted files in `outputs/`
4. Original PDFs are moved to `archive/`

## Troubleshooting

### Auto Converter Not Running After Restart

**Check 1: Verify VBS file is in Startup folder**
```
C:\Users\jdevine\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\start_auto_converter_silent.vbs
```

**Check 2: Run manually to see errors**
```bash
cd c:\Users\jdevine\dev\pdf-to-md
start_auto_converter.bat
```

**Check 3: Verify Python and watchdog are installed**
```bash
python --version
pip show watchdog
```

### PDFs Not Being Converted

**Check 1: Is the converter running?**
- Check Task Manager for `python.exe`
- Or check `outputs/auto_convert.log` for recent entries

**Check 2: File permissions**
- Make sure you can read files from `inputs/`
- Make sure you can write to `outputs/` and `archive/`

**Check 3: Check the log file**
```
outputs/auto_convert.log
```
Look for error messages

### Console Window Appears on Startup

This means the VBS script isn't working. Try:
1. Re-run `setup_autostart.bat`
2. Or manually copy `start_auto_converter_silent.vbs` to Startup folder

### High CPU Usage

If the converter is using too much CPU:
1. Check `outputs/auto_convert.log` for errors
2. Make sure watchdog is properly installed
3. Consider using `--scan` mode instead (see Alternative Approaches)

## Managing the Auto Converter

### Stop the Converter

**Option 1: Kill the process**
1. Open Task Manager (`Ctrl+Shift+Esc`)
2. Find `python.exe` or `pythonw.exe`
3. Right-click → End Task

**Option 2: Restart Windows**
- It won't start until next login

### Start Manually

Double-click: `start_auto_converter_silent.vbs`

Or for debugging with console output:
```bash
start_auto_converter.bat
```

### Remove Auto-Start

Delete the VBS file from Startup folder:
```
C:\Users\jdevine\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\start_auto_converter_silent.vbs
```

Or run this command:
```bash
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\start_auto_converter_silent.vbs"
```

### Temporarily Disable

Rename the file in Startup folder:
```
start_auto_converter_silent.vbs → start_auto_converter_silent.vbs.disabled
```

## Alternative Approaches

### Manual Start (No Auto-Start)

If you prefer to start manually each time:
1. Don't run `setup_autostart.bat`
2. When you want to use it, double-click `start_auto_converter_silent.vbs`
3. Or run `start_auto_converter.bat` to see console output

### Periodic Scan Mode

Instead of continuous watching, scan periodically:

**Create a scheduled task (user-level, no admin needed):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily or at logon
4. Action: Start a program
5. Program: `python`
6. Arguments: `c:\Users\jdevine\dev\pdf-to-md\auto_convert.py --scan`

This will check for new PDFs periodically instead of watching continuously.

### VS Code Integration

Add to `.vscode/tasks.json` to start when you open the project:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Auto Converter",
      "type": "shell",
      "command": "python auto_convert.py",
      "isBackground": true,
      "problemMatcher": []
    }
  ]
}
```

## Log File Location

All conversion activity is logged to:
```
outputs/auto_convert.log
```

The log includes:
- When files are detected
- Conversion progress
- Images extracted
- Where files were archived
- Any errors encountered

## Project Structure

```
pdf-to-md/
├── inputs/                              # Drop PDFs here
├── outputs/                             # Converted markdown files
│   ├── images/                         # Extracted images
│   └── auto_convert.log                # Activity log
├── archive/                             # Processed PDFs moved here
│   └── YYYYMMDD_HHMMSS/               # Timestamped session folders
├── auto_convert.py                      # Main converter script
├── start_auto_converter.bat             # Launcher script
├── start_auto_converter_silent.vbs      # Silent launcher
├── setup_autostart.bat                  # Setup script
└── AUTOSTART_SETUP.md                   # This file
```

## Support

If you encounter issues:
1. Check `outputs/auto_convert.log`
2. Run `start_auto_converter.bat` to see console output
3. Verify all dependencies are installed: `pip install -r requirements.txt`

## Notes

- The converter only runs when you're logged into Windows
- It stops when you log out or shut down
- Each session creates a new archive subfolder with timestamp
- Processed PDFs are moved (not copied) to archive
- Large PDFs are automatically split into manageable chunks
