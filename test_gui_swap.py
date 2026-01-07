"""
Test script to verify GUI swap functionality updates window title and labels
"""

import tkinter as tk
from oracle_to_azure_select_converter.gui import QueryConverterGUI
import time


def test_swap_labels():
    """Test that swap updates window title and panel labels."""
    print("Testing GUI Swap Functionality...")
    print("=" * 70)
    
    root = tk.Tk()
    app = QueryConverterGUI(root)
    
    # Get initial state
    print(f"\n1. Initial State:")
    print(f"   Window Title: {root.title()}")
    print(f"   Left Panel: {app.left_frame.cget('text')}")
    print(f"   Right Panel: {app.right_frame.cget('text')}")
    print(f"   Swapped: {app.is_swapped}")
    
    # Add some test queries
    app.left_text.delete('1.0', tk.END)
    app.left_text.insert('1.0', 'SELECT NVL(name, "Test") FROM employees')
    
    app.right_text.delete('1.0', tk.END)
    app.right_text.insert('1.0', 'SELECT ISNULL(name, "Test") FROM employees')
    
    # Process events
    root.update()
    
    # Simulate swap button click
    print(f"\n2. Clicking Swap Button...")
    app.swap_queries()
    root.update()
    
    print(f"\n3. After First Swap:")
    print(f"   Window Title: {root.title()}")
    print(f"   Left Panel: {app.left_frame.cget('text')}")
    print(f"   Right Panel: {app.right_frame.cget('text')}")
    print(f"   Swapped: {app.is_swapped}")
    
    # Verify content swapped
    left_content = app.left_text.get('1.0', tk.END).strip()
    right_content = app.right_text.get('1.0', tk.END).strip()
    print(f"   Left Content: {left_content[:40]}...")
    print(f"   Right Content: {right_content[:40]}...")
    
    # Swap back
    print(f"\n4. Clicking Swap Button Again...")
    app.swap_queries()
    root.update()
    
    print(f"\n5. After Second Swap (Back to Normal):")
    print(f"   Window Title: {root.title()}")
    print(f"   Left Panel: {app.left_frame.cget('text')}")
    print(f"   Right Panel: {app.right_frame.cget('text')}")
    print(f"   Swapped: {app.is_swapped}")
    
    # Verify
    print(f"\n{'=' * 70}")
    print("VERIFICATION:")
    print("=" * 70)
    
    # Re-check after swapping back
    app.swap_queries()
    root.update()
    
    checks = [
        ("Window title includes [SWAPPED]", "[SWAPPED]" in root.title()),
        ("Left panel shows Azure (when swapped)", "Azure" in app.left_frame.cget('text')),
        ("Right panel shows Oracle (when swapped)", "Oracle" in app.right_frame.cget('text')),
        ("is_swapped flag is True", app.is_swapped == True)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'=' * 70}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("Window title and panel labels update correctly when swap is clicked.")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    # Clean up
    root.destroy()


if __name__ == '__main__':
    test_swap_labels()
