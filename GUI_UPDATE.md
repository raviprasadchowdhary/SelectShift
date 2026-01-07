# GUI Application - Project Update

## ✅ NEW FEATURE: Graphical User Interface

The Oracle ↔ Azure SQL Query Converter now includes a **full-featured GUI application** for bidirectional query conversion!

## 🎯 What's New

### 1. GUI Application (`gui.py`)
- **Two-panel layout** - Oracle (left) and Azure SQL (right)
- **Bidirectional conversion** - Convert in either direction
- **Visual warning display** - See warnings instantly
- **Swap functionality** - Exchange queries between panels
- **Built-in help** - Instructions available in the GUI

### 2. Reverse Converter (`reverse_converter.py`)
- **Azure SQL → Oracle** conversion capability
- Converts:
  - `ISNULL()` → `NVL()`
  - `GETDATE()` → `SYSDATE`
  - `SELECT TOP N` → `WHERE ROWNUM <= N`
  - `CAST AS DATE` → `TRUNC()`
  - `+` → `||` (string concatenation)

### 3. Easy Launchers
- **`run_gui.py`** - Python launcher script
- **`Launch_GUI.bat`** - Windows batch file (double-click to run)

### 4. Documentation
- **`GUI_GUIDE.md`** - Quick start guide for GUI
- **`GUI_FEATURES.md`** - Detailed feature documentation
- Updated **`README.md`** with GUI information

## 📁 New Files Created

```
SelectShift/
├── oracle_to_azure_select_converter/
│   ├── gui.py                    ✨ NEW - GUI application (400+ lines)
│   ├── reverse_converter.py      ✨ NEW - Azure→Oracle converter
│   └── __init__.py               📝 UPDATED - Now includes reverse converter
│
├── run_gui.py                    ✨ NEW - Python GUI launcher
├── Launch_GUI.bat                ✨ NEW - Windows double-click launcher
├── GUI_GUIDE.md                  ✨ NEW - GUI quick start
├── GUI_FEATURES.md               ✨ NEW - GUI feature documentation
└── README.md                     📝 UPDATED - Added GUI section
```

## 🚀 How to Use

### Launch Options

**Option 1: Python Script**
```powershell
python run_gui.py
```

**Option 2: Batch File (Windows)**
```
Double-click: Launch_GUI.bat
```

**Option 3: Direct Module**
```powershell
python -m oracle_to_azure_select_converter.gui
```

## 🎨 GUI Features

### Main Interface
- **Left Panel:** Oracle SQL queries
- **Right Panel:** Azure SQL queries
- **Middle Buttons:** Conversion controls
- **Bottom Panel:** Warnings and status
- **Control Bar:** Clear, Help, Exit buttons

### Conversion Modes

1. **Oracle → Azure**
   - Place Oracle query in left panel
   - Click "Oracle → Azure"
   - Result appears in right panel

2. **Azure → Oracle**
   - Place Azure query in right panel
   - Click "Azure → Oracle"
   - Result appears in left panel

3. **Swap**
   - Exchange queries between panels
   - Great for iterative testing

## 📊 Comparison: CLI vs GUI vs API

| Feature | Command Line | GUI | Python API |
|---------|-------------|-----|------------|
| **Ease of Use** | Medium | ⭐⭐⭐ Easy | Advanced |
| **Visual Interface** | No | ⭐⭐⭐ Yes | No |
| **Bidirectional** | Yes | ⭐⭐⭐ Yes | Yes |
| **Copy/Paste** | Manual | ⭐⭐⭐ Built-in | Manual |
| **Warning Display** | Text | ⭐⭐⭐ Visual | Programmatic |
| **Best For** | Scripts | QA Testers | Integration |

## 🎯 Target Users

### Perfect for QA Testers
- ✅ No coding knowledge required
- ✅ Visual, intuitive interface
- ✅ Instant feedback with warnings
- ✅ Easy copy/paste workflow
- ✅ Side-by-side comparison

### Also Great For
- Database administrators
- Migration teams
- Developers testing queries
- Anyone needing quick conversions

## 🔧 Technical Details

### GUI Framework
- **Library:** tkinter (built into Python)
- **No additional dependencies** required
- **Cross-platform** (Windows, Mac, Linux)
- **Responsive design** with resizable panels

### Architecture
```python
QueryConverterGUI
├── Left Panel (Oracle)
├── Middle Panel (Conversion Buttons)
├── Right Panel (Azure SQL)
├── Bottom Panel (Warnings)
└── Control Panel (Buttons)
```

### Conversion Engine
- Uses existing `converter.py` for Oracle→Azure
- Uses new `reverse_converter.py` for Azure→Oracle
- Same reliable conversion rules
- Consistent warning system

## 🎓 Example Session

```
1. Launch GUI: python run_gui.py

2. Enter in left panel:
   SELECT NVL(name, 'Unknown') FROM employees WHERE ROWNUM <= 5

3. Click "Oracle → Azure"

4. Right panel shows:
   SELECT TOP 5 ISNULL(name, 'Unknown') FROM employees

5. Click "Swap" to exchange

6. Click "Azure → Oracle" to convert back

7. Verify round-trip accuracy
```

## ⚡ Performance

- **Instant conversion** - No waiting
- **Lightweight** - Minimal memory usage
- **Responsive** - Smooth text editing
- **Stable** - Error handling built-in

## 📝 Version Update

- **Previous Version:** 1.0.0 (CLI and API only)
- **Current Version:** 2.0.0 (Added GUI and reverse conversion)

## 🎉 Benefits

### Before (CLI/API Only)
```powershell
# Manual process
python -m oracle_to_azure_select_converter -f query.sql
# Open output file
# Copy result
# Paste into tool
```

### After (With GUI)
```
1. Double-click Launch_GUI.bat
2. Paste query
3. Click convert button
4. Copy result
✅ Done!
```

## 🚀 Ready to Use

The GUI application is **fully functional** and ready for QA teams to use immediately!

### Quick Start
1. Navigate to project directory
2. Run: `python run_gui.py` or double-click `Launch_GUI.bat`
3. Start converting queries!

### Documentation
- **Quick Start:** See `GUI_GUIDE.md`
- **Features:** See `GUI_FEATURES.md`
- **Full Docs:** See `README.md`

---

## 📊 Project Statistics

**Total Lines of Code Added:** ~700+ lines
- `gui.py`: ~400 lines
- `reverse_converter.py`: ~200 lines
- Documentation: ~100 lines

**Files Modified:** 3
**Files Created:** 6

**Features Added:**
- ✅ Full GUI application
- ✅ Bidirectional conversion
- ✅ Azure→Oracle converter
- ✅ Visual warning system
- ✅ Swap functionality
- ✅ Multiple launch methods
- ✅ Comprehensive GUI docs

---

**Status:** ✅ COMPLETE - GUI Ready for Production Use  
**Version:** 2.0.0  
**Updated:** January 7, 2026

🎉 **The GUI makes query conversion accessible to everyone!** 🎉
