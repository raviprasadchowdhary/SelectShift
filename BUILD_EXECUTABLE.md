# Building Standalone Executable

## Overview

You have **TWO options** to run this application:

### Option 1: Run with Python (Current Setup)

**Requirements:**
- Python 3.7 or higher installed
- tkinter (included with Python)

**How to run:**
```powershell
python run_gui.py
# OR
Launch_GUI.bat
```

**Pros:**
- ✅ No build step required
- ✅ Easy to modify and debug
- ✅ Smaller file size
- ✅ Cross-platform (Windows, Mac, Linux)

**Cons:**
- ❌ Requires Python installation
- ❌ Users must have Python on their system

---

### Option 2: Standalone Executable (No Python Required)

**Requirements:**
- NONE! The .exe includes everything

**How to create:**

1. **Install PyInstaller** (one-time setup):
```powershell
pip install pyinstaller
```

2. **Build the executable**:
```powershell
pyinstaller oracle_azure_converter.spec
```

3. **Find your executable**:
```
dist/OracleAzureConverter.exe
```

4. **Distribute**:
- Copy `OracleAzureConverter.exe` to any Windows PC
- No Python installation needed!
- Just double-click to run

**Pros:**
- ✅ No Python required on target machine
- ✅ Single .exe file
- ✅ Easy to distribute to QA testers
- ✅ Professional deployment

**Cons:**
- ❌ Larger file size (~15-30 MB)
- ❌ Windows-only (need separate build for Mac/Linux)
- ❌ Requires build step when code changes

---

## Detailed Build Instructions

### Step 1: Install PyInstaller

```powershell
# Activate virtual environment (if using)
.venv\Scripts\Activate.ps1

# Install PyInstaller
pip install pyinstaller
```

### Step 2: Build Executable

```powershell
# From project root directory
pyinstaller oracle_azure_converter.spec
```

This creates:
```
dist/
└── OracleAzureConverter.exe    ← Standalone executable (15-30 MB)
```

### Step 3: Test the Executable

```powershell
# Run the executable
.\dist\OracleAzureConverter.exe
```

The GUI should launch without requiring Python!

### Step 4: Distribute

**For QA Testers:**
1. Copy `dist/OracleAzureConverter.exe` to a shared location
2. QA testers just double-click the .exe
3. No Python installation needed!

**For End Users:**
- Just distribute the single `OracleAzureConverter.exe` file
- No dependencies
- No installation required

---

## Alternative: Build One-Folder Bundle

If you prefer a folder with multiple files instead of a single large .exe:

```powershell
# Build one-folder bundle
pyinstaller --onedir --windowed run_gui.py
```

Creates:
```
dist/run_gui/
├── run_gui.exe
├── python312.dll
├── (other DLLs and files)
```

**Trade-offs:**
- Faster startup time
- Smaller executable file
- But multiple files to distribute

---

## Comparison Matrix

| Feature | Python Required | Standalone .exe |
|---------|----------------|-----------------|
| **Target Users** | Developers, Python users | QA testers, end users |
| **Installation** | Python 3.7+ | None |
| **File Size** | <1 MB | 15-30 MB |
| **Startup Time** | Fast | Slightly slower |
| **Distribution** | Share source code | Share .exe file |
| **Updates** | Just update .py files | Rebuild .exe |
| **Cross-Platform** | Yes | No (Windows only) |
| **Professional** | Developer tool | Production ready |

---

## Recommended Approach

### For Development Team:
Use **Option 1** (Python) - easier to modify and debug

### For QA Testers:
Use **Option 2** (Standalone .exe) - no Python needed

### For Production Deployment:
Use **Option 2** (Standalone .exe) - professional distribution

---

## Troubleshooting

### Build Issues

**Problem:** PyInstaller not found
```powershell
# Solution: Install PyInstaller
pip install pyinstaller
```

**Problem:** Missing tkinter
```powershell
# Solution: Tkinter comes with Python, reinstall Python with Tcl/Tk option checked
```

**Problem:** Antivirus blocks .exe
```
# Solution: This is normal for PyInstaller executables
# Add exception in antivirus or code-sign the executable
```

### Runtime Issues

**Problem:** .exe won't start
```
# Solution: Build with console mode first to see errors
# Change console=False to console=True in .spec file
```

**Problem:** Slow startup
```
# Solution: This is normal for PyInstaller (3-5 seconds)
# Consider one-folder mode for faster startup
```

---

## Building for Other Platforms

### For macOS:
```bash
# On a Mac:
pyinstaller --onefile --windowed run_gui.py
# Creates: dist/run_gui (macOS app)
```

### For Linux:
```bash
# On Linux:
pyinstaller --onefile --windowed run_gui.py
# Creates: dist/run_gui (Linux executable)
```

**Note:** Must build on each target platform

---

## Advanced Options

### Custom Icon

1. Get an `.ico` file (Windows icon)
2. Update spec file:
```python
icon='path/to/icon.ico'
```

### Code Signing (Professional)

For corporate deployment, sign the executable:
```powershell
signtool sign /f certificate.pfx /p password OracleAzureConverter.exe
```

### Include Additional Files

Add data files to spec:
```python
datas=[
    ('README.md', '.'),
    ('docs', 'docs'),
]
```

---

## Summary

**Current Status:**
- ✅ Application works with Python installed
- ✅ No external dependencies except Python standard library
- ✅ Spec file ready for building standalone executable

**To create standalone .exe:**
```powershell
pip install pyinstaller
pyinstaller oracle_azure_converter.spec
# Result: dist/OracleAzureConverter.exe (no Python needed!)
```

**Recommendation:**
- Developers: Use Python version (`python run_gui.py`)
- QA/Users: Use standalone .exe (`OracleAzureConverter.exe`)
