import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

class FileSystemApp:
    def __init__(self, master):
        self.master = master
        self.master.title("File System Simulator")
        
        # Make the window fullscreen
        self.master.attributes('-fullscreen', True)
        
        self.file_system = FileSystem(disk_size=20)
        
        # Increase the font size for labels and buttons
        font_size = 14

        self.file_label = tk.Label(master, text="File Name:", font=('Arial', font_size))
        self.file_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.file_entry = tk.Entry(master, width=30, font=('Arial', font_size))
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.create_button = tk.Button(master, text="Create File", command=self.create_file, font=('Arial', font_size))
        self.create_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.delete_button = tk.Button(master, text="Delete File", command=self.delete_file, font=('Arial', font_size))
        self.delete_button.grid(row=0, column=3, padx=10, pady=10)
        
        self.rename_button = tk.Button(master, text="Rename File", command=self.rename_file, font=('Arial', font_size))
        self.rename_button.grid(row=0, column=4, padx=10, pady=10)

        self.create_text_button = tk.Button(master, text="Create Text File", command=self.create_text_file, font=('Arial', font_size))
        self.create_text_button.grid(row=0, column=5, padx=10, pady=10)

        self.open_text_button = tk.Button(master, text="Open Text File", command=self.open_text_file, font=('Arial', font_size))
        self.open_text_button.grid(row=0, column=6, padx=10, pady=10)
        
        self.file_listbox = tk.Listbox(master, width=60, height=20, font=('Arial', font_size))
        self.file_listbox.grid(row=1, column=0, columnspan=7, padx=10, pady=10)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.display_file_details)
        
        # Center all widgets
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)
        for child in master.winfo_children():
            child.grid_configure(padx=5, pady=5, sticky='nsew')
        
        master.update_idletasks()
        window_width = master.winfo_width()
        window_height = master.winfo_height()
        position_right = int(master.winfo_screenwidth()/2 - window_width/2)
        position_down = int(master.winfo_screenheight()/2 - window_height/2)
        master.geometry(f"+{position_right}+{position_down}")

        # Populate the file list initially
        self.update_file_list()

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        files = self.file_system.list_files()
        for file in files:
            self.file_listbox.insert(tk.END, file)    

    def create_file(self):
        filename = self.file_entry.get()
        if filename.strip() == "":
            messagebox.showerror("Error", "Please enter a valid file name.")
            return
        result = self.file_system.create_file(filename, size=1)
        messagebox.showinfo("Result", result)
        self.update_file_list()
        
    def delete_file(self):
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a file to delete.")
            return
        filename = self.file_listbox.get(selected_index)
        result = self.file_system.delete_file(filename)
        messagebox.showinfo("Result", result)
        self.update_file_list()
        
    def rename_file(self):
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a file to rename.")
            return
        old_name = self.file_listbox.get(selected_index)
        new_name = simpledialog.askstring("Rename File", f"Enter new name for '{old_name}':")
        if new_name:
            result = self.file_system.rename_file(old_name, new_name)
            messagebox.showinfo("Result", result)
            self.update_file_list()

    def create_text_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w') as f:
                f.write("")
            messagebox.showinfo("Result", f"Text file '{filename}' created successfully.")
            self.update_file_list()

    def open_text_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.edit_text_file(filename)

    def edit_text_file(self, filename):
        editor = TextEditor(self.master, filename)
        editor.mainloop()

    def display_file_details(self, event):
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            return
        filename = self.file_listbox.get(selected_index)

class TextEditor(tk.Toplevel):
    def __init__(self, master, filename):
        super().__init__(master)
        self.filename = filename
        self.title(f"Text Editor - {filename}")
        self.geometry("800x600")

        self.text_widget = tk.Text(self, wrap="word")
        self.text_widget.pack(expand=True, fill="both")
        self.text_widget.bind("<Control-s>", self.save_file)

        with open(filename, 'r') as file:
            self.text_widget.insert("1.0", file.read())

    def save_file(self, event=None):
        with open(self.filename, 'w') as file:
            file.write(self.text_widget.get("1.0", "end-1c"))
        messagebox.showinfo("File Saved", "File saved successfully.")

class File:
    def __init__(self, name, size):
        self.name = name
        self.size = size

class FileSystem:
    def __init__(self, disk_size):
        self.disk_size = disk_size
        self.disk = [None] * disk_size
        self.files = {}

    def create_file(self, name, size):
        if name in self.files:
            return f"Error: File '{name}' already exists."
        if size > self.get_free_space():
            return "Error: Not enough free space."
        file = File(name, size)
        self.files[name] = file
        start_index = self.find_free_space(size)
        if start_index == -1:
            del self.files[name]
            return "Error: Not enough contiguous free space."
        for i in range(start_index, start_index + size):
            self.disk[i] = name
        return f"File '{name}' created successfully."

    def delete_file(self, name):
        if name not in self.files:
            return f"Error: File '{name}' not found."
        file = self.files[name]
        for i in range(self.disk_size):
            if self.disk[i] == name:
                self.disk[i] = None
        del self.files[name]
        return f"File '{name}' deleted successfully."
    
    def rename_file(self, old_name, new_name):
        if old_name not in self.files:
            return f"Error: File '{old_name}' not found."
        if new_name in self.files:
            return f"Error: File '{new_name}' already exists."
        file = self.files.pop(old_name)
        file.name = new_name
        self.files[new_name] = file
        for i in range(self.disk_size):
            if self.disk[i] == old_name:
                self.disk[i] = new_name
        return f"File '{old_name}' renamed to '{new_name}'."

    def list_files(self):
        files_list = []
        for name, file in self.files.items():
            files_list.append(name)
        return files_list
    
    def get_free_space(self):
        return sum(1 for block in self.disk if block is None)
    
    def find_free_space(self, size):
        count = 0
        for i in range(self.disk_size):
            if self.disk[i] is None:
                count += 1
                if count == size:
                    return i - size + 1
            else:
                count = 0
        return -1

root = tk.Tk()
app = FileSystemApp(root)
root.mainloop()
