# GUI Quick Start Guide

## 🚀 Launch the GUI

```powershell
# From the project directory
python run_gui.py
```

## 🖥️ GUI Features

### Two-Panel Layout

**Left Panel:** Oracle SQL Query
**Right Panel:** Azure SQL Query

### Conversion Buttons

1. **Oracle → Azure** - Convert Oracle query to Azure SQL
2. **Azure → Oracle** - Convert Azure SQL query to Oracle
3. **⇄ Swap** - Exchange queries between left and right panels

### Bottom Panel

- **Warnings & Status** - Shows conversion warnings and status messages
- **Clear Buttons** - Clear individual or all panels
- **Help Button** - Display usage instructions

## 📝 How to Use

### Option 1: Oracle → Azure Conversion

1. Enter or paste Oracle SQL query in the **left panel**
2. Click **"Oracle → Azure"** button
3. Converted Azure SQL appears in the **right panel**
4. Check the **Warnings & Status** panel for any issues

### Option 2: Azure → Oracle Conversion

1. Enter or paste Azure SQL query in the **right panel**
2. Click **"Azure → Oracle"** button
3. Converted Oracle SQL appears in the **left panel**
4. Review warnings if any

### Example Workflow

```
Step 1: Paste this in left panel (Oracle):
SELECT NVL(name, 'Unknown') || ' ' || dept 
FROM employees 
WHERE ROWNUM <= 10

Step 2: Click "Oracle → Azure"

Step 3: Right panel shows (Azure):
SELECT TOP 10 ISNULL(name, 'Unknown') + ' ' + dept 
FROM employees

Step 4: Use "Swap" if you want to reverse
Step 5: Click "Azure → Oracle" to convert back
```

## 🎨 GUI Layout

```
┌─────────────────────────────────────────────────────────────┐
│        Oracle ↔ Azure SQL Query Converter                  │
├────────────────────────┬──────┬──────────────────────────────┤
│                        │      │                              │
│   Oracle SQL Query     │  →   │   Azure SQL Query            │
│                        │  ←   │                              │
│   [Text Editor]        │  ⇄   │   [Text Editor]              │
│                        │      │                              │
│                        │      │                              │
├────────────────────────┴──────┴──────────────────────────────┤
│   Warnings & Status                                         │
│   ✓ Conversion complete - No warnings.                      │
├─────────────────────────────────────────────────────────────┤
│ [Clear Oracle] [Clear Azure] [Clear All]  [Help]  [Exit]   │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Tips

1. **Copy & Paste** - Use Ctrl+C / Ctrl+V to copy queries from your tools
2. **Warnings** - Always check the warnings panel for important notes
3. **Swap Feature** - Use swap to quickly exchange queries
4. **Clear All** - Reset both panels when starting a new conversion
5. **Formatting** - The GUI preserves your query formatting

## ⚠️ Important Notes

- Only SELECT queries are supported
- Review converted queries before executing them
- Pay attention to warnings for complex features
- The tool is bidirectional - convert in either direction
- CASE to DECODE conversion (Azure→Oracle) shows warnings for manual review

## 🔧 Troubleshooting

**GUI doesn't start?**
```powershell
# Make sure you have Python 3.7+
python --version

# Tkinter is usually included, but verify:
python -c "import tkinter; print('Tkinter OK')"
```

**Conversion doesn't work?**
- Check if query is a SELECT statement
- Review warnings panel for specific issues
- Ensure query syntax is valid

## 📞 Need Help?

Click the **Help** button in the GUI for built-in instructions.

---

**Enjoy converting queries with the GUI!** 🎉
