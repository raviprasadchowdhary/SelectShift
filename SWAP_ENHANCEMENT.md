# Swap Button - Dynamic Window Title Update

## ✅ Enhancement Complete

The GUI now **dynamically updates the window title and panel labels** when you click the Swap button!

## 🎯 What Changed

### Before Enhancement
- Window title: Always showed "Oracle ↔ Azure SQL Query Converter"
- Left panel: Always labeled "Oracle SQL Query"
- Right panel: Always labeled "Azure SQL Query"
- **Problem:** After swapping, labels didn't reflect the actual content

### After Enhancement
- Window title and panel labels **change dynamically** based on swap state
- Clear visual indication of which database syntax is in which panel
- Status message confirms the swap direction

## 📊 Visual Behavior

### Normal State (Not Swapped)

```
┌─────────────────────────────────────────────────────┐
│    Oracle ↔ Azure SQL Query Converter               │  ← Window Title
├──────────────────┬─────────┬────────────────────────┤
│                  │         │                        │
│ Oracle SQL Query │ Oracle→ │ Azure SQL Query        │  ← Panel Labels
│    (LEFT)        │  Azure  │    (RIGHT)             │
│                  │         │                        │
│  SELECT NVL(...) │ Azure→  │  SELECT ISNULL(...)    │
│                  │ Oracle  │                        │
│                  │  ⇄ Swap │                        │
└──────────────────┴─────────┴────────────────────────┘
   ↑                                    ↑
  Oracle content              Azure SQL content
```

**Status:** ✓ Queries swapped back to normal - Oracle on LEFT, Azure on RIGHT

---

### Swapped State (After Clicking Swap)

```
┌─────────────────────────────────────────────────────┐
│ Azure SQL ↔ Oracle Query Converter [SWAPPED]        │  ← Title Changed!
├──────────────────┬─────────┬────────────────────────┤
│                  │         │                        │
│ Azure SQL Query  │ Oracle→ │ Oracle SQL Query       │  ← Labels Swapped!
│   (Swapped)      │  Azure  │   (Swapped)            │
│    (LEFT)        │         │    (RIGHT)             │
│                  │ Azure→  │                        │
│ SELECT ISNULL(...)│ Oracle │  SELECT NVL(...)       │
│                  │  ⇄ Swap │                        │
└──────────────────┴─────────┴────────────────────────┘
   ↑                                    ↑
 Azure SQL content              Oracle content
```

**Status:** ✓ Queries swapped - Azure is now on LEFT, Oracle on RIGHT

## 🔄 State Tracking

The GUI now maintains an `is_swapped` flag:
- **`False`** (Normal): Oracle on left, Azure on right
- **`True`** (Swapped): Azure on left, Oracle on right

## 📝 What Updates When You Click Swap

1. **Window Title:**
   - Normal → Swapped: `"Oracle ↔ Azure SQL Query Converter"` → `"Azure SQL ↔ Oracle Query Converter [SWAPPED]"`
   - Swapped → Normal: Returns to original title

2. **Left Panel Label:**
   - Normal → Swapped: `"Oracle SQL Query"` → `"Azure SQL Query (Swapped)"`
   - Swapped → Normal: Returns to `"Oracle SQL Query"`

3. **Right Panel Label:**
   - Normal → Swapped: `"Azure SQL Query"` → `"Oracle SQL Query (Swapped)"`
   - Swapped → Normal: Returns to `"Azure SQL Query"`

4. **Status Message:**
   - Shows clear indication: "swapped - Azure is now on LEFT, Oracle on RIGHT"
   - Or: "swapped back to normal - Oracle on LEFT, Azure on RIGHT"

5. **Query Content:**
   - Left and right panel contents are exchanged

## 💡 Benefits

✅ **Clear Visual Feedback** - Immediately see which panel contains which database syntax  
✅ **Prevents Confusion** - No ambiguity about which query is which  
✅ **Intuitive UX** - Window title reflects actual state  
✅ **Status Confirmation** - Warning panel confirms the swap action  
✅ **Reversible** - Clicking swap again restores normal state  

## 🧪 Test Results

```
✅ PASS: Window title includes [SWAPPED]
✅ PASS: Left panel shows Azure (when swapped)
✅ PASS: Right panel shows Oracle (when swapped)
✅ PASS: is_swapped flag is True
✅ ALL TESTS PASSED!
```

## 🎬 Usage Example

```
1. Launch GUI: python run_gui.py

2. Initial State:
   Title: "Oracle ↔ Azure SQL Query Converter"
   Left: "Oracle SQL Query"
   Right: "Azure SQL Query"

3. Click "⇄ Swap" button:
   Title: "Azure SQL ↔ Oracle Query Converter [SWAPPED]" ⬅ Changed!
   Left: "Azure SQL Query (Swapped)" ⬅ Changed!
   Right: "Oracle SQL Query (Swapped)" ⬅ Changed!
   Status: "✓ Queries swapped - Azure is now on LEFT, Oracle on RIGHT"

4. Click "⇄ Swap" again:
   Returns to normal state with original labels
```

## 🎯 Why This Matters

**Scenario:** A QA tester pastes an Oracle query in the left panel, converts it, then clicks Swap to run more conversions.

**Without this fix:**
- Window still says "Oracle" on left even though it now has Azure SQL
- Confusing! Easy to make mistakes.

**With this fix:**
- Window title shows `[SWAPPED]`
- Left panel clearly labeled "Azure SQL Query (Swapped)"
- Right panel clearly labeled "Oracle SQL Query (Swapped)"
- No confusion! Clear which is which.

---

**The GUI now provides clear, accurate visual feedback at all times!** ✨
