#!/usr/bin/env python3

"""
SMS XML to HTML Conversion GUI
A simple GUI wrapper for smsxml2html.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

class SMSConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SMS XML to HTML Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Get script directory
        self.script_dir = Path(__file__).parent.resolve()
        
        # Set default paths
        self.default_xml_folder = self.script_dir
        xmls_folder = self.script_dir / "XMLs"
        if xmls_folder.exists() and xmls_folder.is_dir():
            self.default_xml_folder = xmls_folder
        
        self.default_output_folder = self.script_dir / "output"
        self.default_phone = ""
        
        # Create GUI elements
        self.create_widgets()
        
        # Set default values
        self.set_defaults()
    
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="SMS XML to HTML Converter", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # SMS XML Input File
        ttk.Label(main_frame, text="SMS XML Input File:", 
                 font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.xml_file_var = tk.StringVar()
        self.xml_entry = ttk.Entry(main_frame, textvariable=self.xml_file_var, 
                                   width=50, font=('Arial', 9))
        self.xml_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_xml_file).grid(row=1, column=2, padx=5, pady=5)
        
        # My Phone Number
        ttk.Label(main_frame, text="My Phone Number:", 
                 font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(main_frame, textvariable=self.phone_var, 
                                     width=50, font=('Arial', 9))
        self.phone_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Phone number format note (on its own row)
        phone_note = ttk.Label(main_frame, text="(11 digits with preceding 1, no dashes or parentheses. Example: 18005551234)", 
                              font=('Arial', 8), foreground='#666')
        phone_note.grid(row=3, column=1, sticky=tk.W, padx=5, pady=(0, 5))
        
        # Base Output Folder
        ttk.Label(main_frame, text="Base Output Folder:", 
                 font=('Arial', 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_var, 
                                      width=50, font=('Arial', 9))
        self.output_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_output_folder).grid(row=4, column=2, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Convert button (larger and styled)
        self.convert_btn = ttk.Button(button_frame, text="Convert to HTML", 
                                     command=self.run_conversion)
        self.convert_btn.grid(row=0, column=0, padx=5, ipadx=20, ipady=5)
        
        # Reset button
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.set_defaults).grid(row=0, column=1, padx=5, ipadx=20, ipady=5)
        
        # Output text area with scrollbar
        output_frame = ttk.LabelFrame(main_frame, text="Conversion Output", padding="10")
        output_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Text widget for output
        self.output_text = tk.Text(output_frame, height=10, width=70, font=('Consolas', 9), 
                                   wrap=tk.WORD, state='disabled')
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure text widget to expand
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                     font=('Arial', 9), foreground='blue')
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)
    
    def set_defaults(self):
        """Set default values in the form"""
        self.xml_file_var.set("")
        self.phone_var.set(self.default_phone)
        self.output_var.set(str(self.default_output_folder))
        self.status_var.set("Ready")
    
    def browse_xml_file(self):
        """Browse for XML input file"""
        initial_dir = self.default_xml_folder
        if self.xml_file_var.get():
            # If there's already a file selected, use its directory
            initial_dir = Path(self.xml_file_var.get()).parent
        
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select SMS XML File",
            filetypes=(("XML files", "*.xml"), ("All files", "*.*"))
        )
        if filename:
            self.xml_file_var.set(filename)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        initial_dir = self.output_var.get() if self.output_var.get() else self.default_output_folder
        
        folder = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Select Output Folder"
        )
        if folder:
            self.output_var.set(folder)
    
    def show_success_dialog(self, html_file_path, folder_to_open):
        """Show custom success dialog with Open Folder button"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Success")
        dialog.geometry("600x280")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300)
        y = (dialog.winfo_screenheight() // 2) - (140)
        dialog.geometry(f"600x280+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success icon and message
        icon_label = ttk.Label(main_frame, text="✓", font=('Arial', 36), foreground='green')
        icon_label.pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Conversion completed successfully!", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Display the HTML file path
        if html_file_path:
            path_label = ttk.Label(main_frame, text=f"Created: {html_file_path}", 
                                  font=('Arial', 9), wraplength=550, foreground='#666')
            path_label.pack(pady=(0, 15))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(5, 0))
        
        def open_folder():
            try:
                if os.path.exists(folder_to_open):
                    if sys.platform == 'win32':
                        os.startfile(folder_to_open)
                    elif sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', folder_to_open])
                    else:  # Linux
                        subprocess.run(['xdg-open', folder_to_open])
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", f"Folder not found:\n{folder_to_open}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")
        
        # Open Folder button (primary action, styled button)
        style = ttk.Style()
        style.configure('Success.TButton', font=('Arial', 10))
        
        open_btn = ttk.Button(button_frame, text="Open Folder", 
                             command=open_folder, style='Success.TButton')
        open_btn.pack(side=tk.LEFT, padx=5, ipadx=20, ipady=8)
        
        # Close button
        close_btn = ttk.Button(button_frame, text="Close", 
                              command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, ipadx=20, ipady=8)
        
        # Make Enter key open folder, Escape close dialog
        dialog.bind('<Return>', lambda e: open_folder())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Focus the Open Folder button
        open_btn.focus_set()
    
    def validate_inputs(self):
        """Validate user inputs"""
        # Check XML file
        xml_file = self.xml_file_var.get().strip()
        if not xml_file:
            messagebox.showerror("Error", "Please select an SMS XML input file.")
            return False
        
        if not os.path.exists(xml_file):
            messagebox.showerror("Error", f"XML file not found:\n{xml_file}")
            return False
        
        # Check phone number
        phone = self.phone_var.get().strip()
        if not phone:
            messagebox.showerror("Error", "Please enter your phone number.")
            return False
        
        # Basic phone number validation (remove non-digits and check length)
        digits_only = ''.join(c for c in phone if c.isdigit())
        if len(digits_only) not in [10, 11]:
            messagebox.showerror("Error", 
                               "Phone number must be 10 or 11 digits.\n" +
                               f"You entered: {phone} ({len(digits_only)} digits)")
            return False
        
        # Check output folder
        output_folder = self.output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return False
        
        return True
    
    def append_output(self, text):
        """Append text to the output text widget"""
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.configure(state='disabled')
        self.root.update()
    
    def clear_output(self):
        """Clear the output text widget"""
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state='disabled')
    
    def run_conversion(self):
        """Run the conversion script"""
        if not self.validate_inputs():
            return
        
        # Check if smsxml2html.py exists
        smsxml2html_path = self.script_dir / "smsxml2html.py"
        if not smsxml2html_path.exists():
            messagebox.showerror("Error", 
                               f"smsxml2html.py not found in:\n{self.script_dir}\n\n" +
                               "Please ensure smsxml2html.py is in the same folder as this script.")
            return
        
        # Get values
        xml_file = self.xml_file_var.get().strip()
        phone = self.phone_var.get().strip()
        output_folder = self.output_var.get().strip()
        
        # Create output folder if it doesn't exist
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output folder:\n{e}")
            return
        
        # Disable convert button and update status
        self.convert_btn.config(state='disabled')
        self.status_var.set("Converting... Please wait...")
        self.clear_output()
        self.append_output("Starting conversion...\n\n")
        self.root.update()
        
        # Build command
        cmd = [
            sys.executable,  # Python executable
            "-u",  # Unbuffered output for real-time display
            str(smsxml2html_path),
            "-o", output_folder,
            "-n", phone,
            xml_file
        ]
        
        try:
            # Run the conversion with real-time output using a different approach
            import threading
            import queue
            
            output_queue = queue.Queue()
            output_lines = []
            
            def read_output(pipe, q):
                """Read output from pipe and put in queue"""
                try:
                    for line in iter(pipe.readline, ''):
                        if line:
                            q.put(line)
                    pipe.close()
                except:
                    pass
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.script_dir),
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            # Start thread to read output
            thread = threading.Thread(target=read_output, args=(process.stdout, output_queue))
            thread.daemon = True
            thread.start()
            
            # Process output in real-time
            while True:
                # Check if process is done
                if process.poll() is not None:
                    # Process finished, get any remaining output
                    while not output_queue.empty():
                        try:
                            line = output_queue.get_nowait()
                            output_lines.append(line)
                            self.append_output(line)
                        except queue.Empty:
                            break
                    break
                
                # Get output from queue
                try:
                    line = output_queue.get(timeout=0.1)
                    output_lines.append(line)
                    self.append_output(line)
                except queue.Empty:
                    pass
            
            returncode = process.returncode
            
            # Re-enable button
            self.convert_btn.config(state='normal')
            
            if returncode == 0:
                self.status_var.set("Conversion completed successfully!")
                self.append_output("\n✓ Conversion completed successfully!\n")
                
                # Parse the output to find the created file path
                html_file_path = None
                folder_to_open = output_folder
                
                if output_lines:
                    for line in output_lines:
                        # Look for the success line that contains both "Created" and " in "
                        # Example: "Success! Created TextConversation_Multiple_20251210_173903/messages.html in C:\Scripts\smsxml2html\output"
                        if 'Success!' in line and 'Created' in line and ' in ' in line and '.html' in line:
                            # Find the position of "Created" and " in "
                            created_pos = line.find('Created')
                            in_pos = line.rfind(' in ')  # Use rfind to get the last occurrence
                            
                            if created_pos != -1 and in_pos != -1 and in_pos > created_pos:
                                # Extract the relative path (between "Created" and " in ")
                                relative_path = line[created_pos + 8:in_pos].strip()  # +8 to skip "Created "
                                
                                # Extract the base folder (after " in ")
                                base_folder = line[in_pos + 4:].strip()  # +4 to skip " in "
                                
                                # Build the full HTML file path
                                html_file_path = os.path.join(base_folder, relative_path.replace('/', os.sep))
                                
                                # Determine the folder to open
                                if '/' in relative_path:
                                    # Has subfolder - open the subfolder, not conv_files
                                    subfolder = relative_path.split('/')[0]
                                    folder_to_open = os.path.join(base_folder, subfolder)
                                else:
                                    # Single file - open the base folder
                                    folder_to_open = base_folder
                                
                                break
                
                # Show success dialog with the actual paths
                self.show_success_dialog(html_file_path, folder_to_open)
            else:
                self.status_var.set("Conversion failed!")
                self.append_output("\n✗ Conversion failed!\n")
                error_msg = "Conversion failed!\n\nCheck the output above for details."
                messagebox.showerror("Error", error_msg)
                
        except Exception as e:
            self.convert_btn.config(state='normal')
            self.status_var.set("Conversion failed!")
            self.append_output(f"\n✗ Error: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to run conversion:\n{e}")

def main():
    root = tk.Tk()
    app = SMSConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()