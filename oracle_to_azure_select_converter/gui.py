"""
GUI Application for Oracle <-> Azure SQL Query Conversion
A two-panel interface for bidirectional query conversion.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from oracle_to_azure_select_converter.converter import convert_oracle_select_to_azure
from oracle_to_azure_select_converter.reverse_converter import convert_azure_select_to_oracle


class QueryConverterGUI:
    """GUI application for bidirectional SQL query conversion."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Oracle ↔ Azure SQL Query Converter")
        self.root.geometry("1400x800")
        
        # Track panel orientation (False = normal, True = swapped)
        self.is_swapped = False
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main container
        self.setup_ui()
        
        # Set initial focus
        self.left_text.focus_set()
    
    def setup_ui(self):
        """Set up the user interface."""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(
            title_frame,
            text="Oracle ↔ Azure SQL Query Converter",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Bidirectional SQL Query Conversion Tool",
            font=('Helvetica', 10)
        )
        subtitle_label.pack()
        
        # Main content frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel (Oracle SQL)
        self.create_left_panel(main_frame)
        
        # Middle panel (Conversion buttons)
        self.create_middle_panel(main_frame)
        
        # Right panel (Azure SQL)
        self.create_right_panel(main_frame)
        
        # Bottom panel (Warnings and status)
        self.create_bottom_panel(main_frame)
        
        # Button panel
        self.create_button_panel()
    
    def create_left_panel(self, parent):
        """Create the left panel for Oracle SQL."""
        self.left_frame = ttk.LabelFrame(parent, text="Oracle SQL Query", padding="10")
        self.left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Text widget with scrollbar
        self.left_text = scrolledtext.ScrolledText(
            self.left_frame,
            wrap=tk.WORD,
            width=50,
            height=25,
            font=('Consolas', 10)
        )
        self.left_text.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text
        placeholder = """-- Enter Oracle SQL query here
-- Example:
SELECT 
    employee_id,
    NVL(first_name, 'N/A') || ' ' || last_name AS full_name,
    DECODE(status, 'A', 'Active', 'I', 'Inactive') AS status,
    TRUNC(hire_date) AS hire_date
FROM employees
WHERE ROWNUM <= 10"""
        
        self.left_text.insert('1.0', placeholder)
        self.left_text.config(fg='gray')
        
        # Bind events for placeholder behavior
        self.left_text.bind('<FocusIn>', lambda e: self.on_focus_in(self.left_text, placeholder))
        self.left_text.bind('<FocusOut>', lambda e: self.on_focus_out(self.left_text, placeholder))
    
    def create_middle_panel(self, parent):
        """Create the middle panel with conversion buttons."""
        middle_frame = ttk.Frame(parent, padding="10")
        middle_frame.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Add some spacing from top
        ttk.Label(middle_frame, text="").pack(pady=50)
        
        # Oracle -> Azure button
        self.oracle_to_azure_btn = ttk.Button(
            middle_frame,
            text="Oracle → Azure\n(Convert)",
            command=self.convert_oracle_to_azure,
            width=15
        )
        self.oracle_to_azure_btn.pack(pady=10)
        
        # Azure -> Oracle button
        self.azure_to_oracle_btn = ttk.Button(
            middle_frame,
            text="Azure → Oracle\n(Convert)",
            command=self.convert_azure_to_oracle,
            width=15
        )
        self.azure_to_oracle_btn.pack(pady=10)
        
        # Separator
        ttk.Separator(middle_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Swap button
        self.swap_btn = ttk.Button(
            middle_frame,
            text="⇄ Swap",
            command=self.swap_queries,
            width=15
        )
        self.swap_btn.pack(pady=10)
    
    def create_right_panel(self, parent):
        """Create the right panel for Azure SQL."""
        self.right_frame = ttk.LabelFrame(parent, text="Azure SQL Query", padding="10")
        self.right_frame.grid(row=0, column=2, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Text widget with scrollbar
        self.right_text = scrolledtext.ScrolledText(
            self.right_frame,
            wrap=tk.WORD,
            width=50,
            height=25,
            font=('Consolas', 10)
        )
        self.right_text.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text
        placeholder = """-- Enter Azure SQL query here
-- Example:
SELECT TOP 10
    employee_id,
    ISNULL(first_name, 'N/A') + ' ' + last_name AS full_name,
    CASE WHEN status = 'A' THEN 'Active' 
         WHEN status = 'I' THEN 'Inactive' END AS status,
    CAST(hire_date AS DATE) AS hire_date
FROM employees"""
        
        self.right_text.insert('1.0', placeholder)
        self.right_text.config(fg='gray')
        
        # Bind events for placeholder behavior
        self.right_text.bind('<FocusIn>', lambda e: self.on_focus_in(self.right_text, placeholder))
        self.right_text.bind('<FocusOut>', lambda e: self.on_focus_out(self.right_text, placeholder))
    
    def create_bottom_panel(self, parent):
        """Create the bottom panel for warnings and status."""
        bottom_frame = ttk.LabelFrame(parent, text="Warnings & Status", padding="10")
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Warnings text area
        self.warnings_text = scrolledtext.ScrolledText(
            bottom_frame,
            wrap=tk.WORD,
            height=6,
            font=('Consolas', 9),
            bg='#fff9e6'
        )
        self.warnings_text.pack(fill=tk.BOTH, expand=True)
        self.warnings_text.insert('1.0', 'Ready. Select a query and click a conversion button.')
        self.warnings_text.config(state=tk.DISABLED)
    
    def create_button_panel(self):
        """Create the bottom button panel."""
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Clear buttons
        ttk.Button(
            button_frame,
            text="Clear Oracle",
            command=lambda: self.clear_text(self.left_text)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear Azure",
            command=lambda: self.clear_text(self.right_text)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=5)
        
        # Exit button
        ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=5)
        
        # Help button
        ttk.Button(
            button_frame,
            text="Help",
            command=self.show_help
        ).pack(side=tk.RIGHT, padx=5)
    
    def on_focus_in(self, text_widget, placeholder):
        """Handle focus in event (remove placeholder)."""
        if text_widget.get('1.0', tk.END).strip() == placeholder.strip():
            text_widget.delete('1.0', tk.END)
            text_widget.config(fg='black')
    
    def on_focus_out(self, text_widget, placeholder):
        """Handle focus out event (add placeholder if empty)."""
        if not text_widget.get('1.0', tk.END).strip():
            text_widget.insert('1.0', placeholder)
            text_widget.config(fg='gray')
    
    def convert_oracle_to_azure(self):
        """Convert Oracle SQL to Azure SQL."""
        oracle_query = self.left_text.get('1.0', tk.END).strip()
        
        if not oracle_query or oracle_query.startswith('-- Enter Oracle'):
            self.show_warning('Please enter an Oracle SQL query.')
            return
        
        try:
            # Perform conversion
            azure_query, warnings = convert_oracle_select_to_azure(oracle_query)
            
            # Update right panel
            self.right_text.config(fg='black')
            self.right_text.delete('1.0', tk.END)
            self.right_text.insert('1.0', azure_query)
            
            # Update warnings
            self.update_warnings(warnings, 'Oracle → Azure')
            
        except Exception as e:
            self.show_error(f'Conversion error: {str(e)}')
    
    def convert_azure_to_oracle(self):
        """Convert Azure SQL to Oracle SQL."""
        azure_query = self.right_text.get('1.0', tk.END).strip()
        
        if not azure_query or azure_query.startswith('-- Enter Azure'):
            self.show_warning('Please enter an Azure SQL query.')
            return
        
        try:
            # Perform conversion
            oracle_query, warnings = convert_azure_select_to_oracle(azure_query)
            
            # Update left panel
            self.left_text.config(fg='black')
            self.left_text.delete('1.0', tk.END)
            self.left_text.insert('1.0', oracle_query)
            
            # Update warnings
            self.update_warnings(warnings, 'Azure → Oracle')
            
        except Exception as e:
            self.show_error(f'Conversion error: {str(e)}')
    
    def swap_queries(self):
        """Swap the contents of left and right panels."""
        left_content = self.left_text.get('1.0', tk.END).strip()
        right_content = self.right_text.get('1.0', tk.END).strip()
        
        # Clear both
        self.left_text.delete('1.0', tk.END)
        self.right_text.delete('1.0', tk.END)
        
        # Swap
        self.left_text.insert('1.0', right_content)
        self.right_text.insert('1.0', left_content)
        
        # Ensure black text
        self.left_text.config(fg='black')
        self.right_text.config(fg='black')
        
        # Toggle swap state
        self.is_swapped = not self.is_swapped
        
        # Update window title and panel labels
        if self.is_swapped:
            self.root.title("Azure SQL ↔ Oracle Query Converter [SWAPPED]")
            self.left_frame.config(text="Azure SQL Query (Swapped)")
            self.right_frame.config(text="Oracle SQL Query (Swapped)")
        else:
            self.root.title("Oracle ↔ Azure SQL Query Converter")
            self.left_frame.config(text="Oracle SQL Query")
            self.right_frame.config(text="Azure SQL Query")
        
        # Update status
        self.warnings_text.config(state=tk.NORMAL)
        self.warnings_text.delete('1.0', tk.END)
        swap_status = "swapped - Azure is now on LEFT, Oracle on RIGHT" if self.is_swapped else "swapped back to normal - Oracle on LEFT, Azure on RIGHT"
        self.warnings_text.insert('1.0', f'✓ Queries {swap_status}.')
        self.warnings_text.config(state=tk.DISABLED)
    
    def clear_text(self, text_widget):
        """Clear a text widget."""
        text_widget.delete('1.0', tk.END)
        text_widget.config(fg='black')
    
    def clear_all(self):
        """Clear all text fields."""
        self.clear_text(self.left_text)
        self.clear_text(self.right_text)
        self.warnings_text.config(state=tk.NORMAL)
        self.warnings_text.delete('1.0', tk.END)
        self.warnings_text.insert('1.0', 'All fields cleared. Ready for new conversion.')
        self.warnings_text.config(state=tk.DISABLED)
    
    def update_warnings(self, warnings, direction):
        """Update the warnings panel."""
        self.warnings_text.config(state=tk.NORMAL)
        self.warnings_text.delete('1.0', tk.END)
        
        if warnings:
            self.warnings_text.insert('1.0', f'✓ Conversion complete ({direction})\n\n')
            self.warnings_text.insert(tk.END, f'{len(warnings)} warning(s):\n')
            for i, warning in enumerate(warnings, 1):
                self.warnings_text.insert(tk.END, f'{i}. {warning.message}\n')
        else:
            self.warnings_text.insert('1.0', f'✓ Conversion complete ({direction}) - No warnings.')
        
        self.warnings_text.config(state=tk.DISABLED)
    
    def show_warning(self, message):
        """Show a warning message."""
        self.warnings_text.config(state=tk.NORMAL)
        self.warnings_text.delete('1.0', tk.END)
        self.warnings_text.insert('1.0', f'⚠ {message}')
        self.warnings_text.config(state=tk.DISABLED)
    
    def show_error(self, message):
        """Show an error message."""
        messagebox.showerror('Error', message)
    
    def show_help(self):
        """Show help dialog."""
        help_text = """Oracle ↔ Azure SQL Query Converter

HOW TO USE:
1. Enter an Oracle SQL query in the left panel
2. Click "Oracle → Azure" to convert to Azure SQL
3. OR enter an Azure SQL query in the right panel
4. Click "Azure → Oracle" to convert to Oracle SQL

FEATURES:
• Bidirectional conversion between Oracle and Azure SQL
• Warning detection for complex features
• Swap button to exchange queries
• Clear buttons to reset panels

CONVERSIONS SUPPORTED:
Oracle → Azure:
  • NVL → ISNULL
  • DECODE → CASE WHEN
  • SYSDATE → GETDATE()
  • || → + (string concat)
  • FROM DUAL → removed
  • ROWNUM → TOP
  • TRUNC(date) → CAST AS DATE

Azure → Oracle:
  • ISNULL → NVL
  • GETDATE() → SYSDATE
  • + → || (string concat)
  • TOP → ROWNUM
  • CAST AS DATE → TRUNC

NOTES:
• Only SELECT queries are supported
• Always review converted queries before use
• Pay attention to warnings for complex features
"""
        messagebox.showinfo('Help', help_text)


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = QueryConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
