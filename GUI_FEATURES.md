# GUI Application Features

## 🎨 User Interface

The GUI provides a clean, intuitive interface for bidirectional SQL query conversion.

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│               Oracle ↔ Azure SQL Query Converter                    │
│               Bidirectional SQL Query Conversion Tool               │
├──────────────────────────┬───────────┬──────────────────────────────┤
│                          │           │                              │
│  ┌─ Oracle SQL Query ──┐ │           │ ┌─ Azure SQL Query ──────┐  │
│  │                      │ │           │ │                         │  │
│  │  SELECT              │ │ Oracle →  │ │  SELECT TOP 10          │  │
│  │    employee_id,      │ │   Azure   │ │    employee_id,         │  │
│  │    NVL(name, 'N/A')  │ │ (Convert) │ │    ISNULL(name, 'N/A')  │  │
│  │      || ' ' ||       │ │           │ │      + ' ' +            │  │
│  │      last_name,      │ │    ───    │ │      last_name,         │  │
│  │    TRUNC(hire_date)  │ │           │ │    CAST(hire_date       │  │
│  │  FROM employees      │ │ Azure →   │ │      AS DATE)           │  │
│  │  WHERE ROWNUM <= 10  │ │  Oracle   │ │  FROM employees         │  │
│  │                      │ │ (Convert) │ │                         │  │
│  │                      │ │           │ │                         │  │
│  │                      │ │   ⇄ Swap  │ │                         │  │
│  │                      │ │           │ │                         │  │
│  └──────────────────────┘ │           │ └─────────────────────────┘  │
│                          │           │                              │
├──────────────────────────┴───────────┴──────────────────────────────┤
│  ┌─ Warnings & Status ─────────────────────────────────────────┐   │
│  │ ✓ Conversion complete (Oracle → Azure)                      │   │
│  │                                                              │   │
│  │ 1 warning(s):                                                │   │
│  │ 1. ROWNUM used with ORDER BY. Manual review required -      │   │
│  │    results may differ. Consider using ROW_NUMBER()          │   │
│  │    OVER(ORDER BY ...) instead.                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│ [Clear Oracle] [Clear Azure] [Clear All]      [Help]  [Exit]       │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔘 Button Functions

### Conversion Buttons (Middle Panel)

1. **Oracle → Azure (Convert)**
   - Converts query from left panel (Oracle) to right panel (Azure SQL)
   - Displays warnings if any complex features detected
   - Preserves query formatting where possible

2. **Azure → Oracle (Convert)**
   - Converts query from right panel (Azure SQL) to left panel (Oracle)
   - Provides guidance for features that need manual review
   - Maintains query structure

3. **⇄ Swap**
   - Exchanges contents between left and right panels
   - **Updates window title** to show `[SWAPPED]` state
   - **Updates panel labels** to reflect current content
   - Useful for iterative conversion and testing
   - Quick way to reverse direction
   - Click again to return to normal state

### Control Buttons (Bottom Panel)

- **Clear Oracle** - Clears only the left panel (Oracle query)
- **Clear Azure** - Clears only the right panel (Azure SQL query)
- **Clear All** - Clears both query panels and warnings
- **Help** - Shows built-in help dialog with instructions
- **Exit** - Closes the application

## 📝 Text Panels

### Oracle SQL Query Panel (Left)

- **Purpose:** Enter or paste Oracle SQL queries
- **Features:**
  - Syntax highlighting placeholder text
  - Scrollable text area for long queries
  - Auto-clearing placeholder on focus
  - Monospace font (Consolas) for readability

### Azure SQL Query Panel (Right)

- **Purpose:** Enter or paste Azure SQL queries
- **Features:**
  - Same features as Oracle panel
  - Output destination for Oracle → Azure conversion
  - Input source for Azure → Oracle conversion

### Warnings & Status Panel (Bottom)

- **Purpose:** Display conversion status and warnings
- **Shows:**
  - ✓ Success messages
  - ⚠ Warning messages for complex features
  - Number of warnings detected
  - Detailed warning descriptions
  - Status updates for all operations

## 🎯 Usage Patterns

### Pattern 1: Oracle → Azure Conversion

```
1. Paste Oracle query in LEFT panel
2. Click "Oracle → Azure" button
3. View converted query in RIGHT panel
4. Check warnings in bottom panel
5. Copy converted query for use
```

### Pattern 2: Azure → Oracle Conversion

```
1. Paste Azure SQL query in RIGHT panel
2. Click "Azure → Oracle" button
3. View converted query in LEFT panel
4. Review warnings if any
5. Copy converted query for use
```

### Pattern 3: Round-Trip Testing

```
1. Start with Oracle query in LEFT panel
2. Click "Oracle → Azure" → Result in RIGHT panel
3. Click "Azure → Oracle" → Result in LEFT panel
4. Compare original vs round-trip result
5. Identify any conversion issues
```

### Pattern 4: Quick Swap Workflow

```
1. Have queries in both panels
2. Click "⇄ Swap" to exchange them
3. Apply different conversion
4. Swap again if needed
```

## 🎨 Visual Indicators

### Text Colors

- **Black** - Active query text
- **Gray** - Placeholder text (hints)
- **Yellow background** - Warning panel

### Status Messages

- ✓ Green check - Successful conversion
- ⚠ Warning triangle - Attention needed
- 🔴 Error - Conversion failed

## ⌨️ Keyboard Shortcuts

While the GUI doesn't have custom shortcuts, standard text editing works:

- **Ctrl+A** - Select all text in focused panel
- **Ctrl+C** - Copy selected text
- **Ctrl+V** - Paste text
- **Ctrl+X** - Cut text
- **Tab** - Move between panels

## 💡 Tips for Best Experience

1. **Use monospace fonts** - Already configured (Consolas)
2. **Maximize window** - For better view of long queries
3. **Check warnings** - Always review before using converted queries
4. **Test round-trip** - Convert back to verify accuracy
5. **Keep original** - Always keep a copy of your original query
6. **Save frequently** - Copy results to your SQL tool/files

## 🔧 Advanced Features

### Placeholder Behavior

- Automatically shows example queries when panels are empty
- Disappears when you click into the panel
- Returns if you leave panel empty
- Gray text indicates placeholder vs. real query

### Warning System

- Real-time detection of complex features
- Detailed explanations for each warning
- Numbered list for multiple warnings
- Context-specific guidance

### Error Handling

- Validates SELECT queries only
- Prevents conversion of empty queries
- Shows clear error messages
- Maintains application stability

## 📱 Window Management

- **Resizable** - Drag corners/edges to resize
- **Minimum size** - Prevents too-small window
- **Responsive** - Panels adjust to window size
- **Scrollbars** - Appear when content exceeds view

---

**The GUI makes query conversion simple and visual!** 🎉
