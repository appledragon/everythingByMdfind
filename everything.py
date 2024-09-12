import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import shutil
import threading

def search_files():
    query = search_var.get()
    directory = directory_var.get()
    
    if not query:
        tree_result.delete(*tree_result.get_children())
        return

    # check if dir exist
    if directory and not os.path.isdir(directory):
        show_tooltip("Warning", f"The directory '{directory}' does not exist.")
        return

    cmd = ['mdfind']
    if search_by_name.get():
        cmd.append('-name')
    cmd.append(query)
    
    # if exist
    if directory:
        cmd.extend(['-onlyin', directory])

    try:
        result = subprocess.check_output(cmd)
        file_paths = result.decode('utf-8').strip().split('\n')
        if not file_paths or file_paths == ['']:
            update_tree_view([])
            return
    except Exception as e:
        show_tooltip("Error", str(e))
        return
    
    # Collect file data
    files_info = []
    for path in file_paths:
        if os.path.isfile(path):
            file_size = os.path.getsize(path)
            mod_time = os.path.getmtime(path)
            files_info.append((os.path.basename(path), file_size, mod_time, path))
    
    # Update the GUI in the main thread
    update_tree_view(files_info)

def update_tree_view(files_info):
    tree_result.delete(*tree_result.get_children())
    global file_data
    file_data = []

    for item in files_info:
        display_size = format_size(item[1])
        display_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[2]))
        file_data.append(item)
        tree_result.insert('', tk.END, values=(item[0], display_size, display_time, item[3]))

def show_tooltip(title, text):
    tooltip = tk.Toplevel(root)
    # set tooltip window on top of the main window, in the center
    x = root.winfo_x() + root.winfo_width() // 2 - 100
    y = root.winfo_y() + root.winfo_height() // 2 - 25
    tooltip.geometry(f"+{x}+{y}")
    tooltip.title(title)
    # tooltip.overrideredirect(True)  # remove window decorations
    # tooltip.configure(bg='black')  # set background color to black
    label = tk.Label(tooltip, text=text)  # set text color to white
    label.pack(pady=10)
    tooltip.after(1000, tooltip.destroy)

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def open_with_vscode():
    selected_item = tree_result.selection()[0]
    file_path = tree_result.item(selected_item, 'values')[3]
    try:
        subprocess.run(['/Applications/Visual Studio Code.app/Contents/MacOS/Electron', file_path], check=True)
    except Exception as e:
        show_tooltip("Error", f"Could not open with VSCode: {str(e)}")

def on_double_click(event):
    open_with_vscode()

def on_right_click(event):
    row_id = tree_result.identify_row(event.y)
    if row_id:
        tree_result.selection_set(row_id)
        context_menu.post(event.x_root, event.y_root)
    else:
        context_menu.unpost()

def delete_file():
    selected_item = tree_result.selection()[0]
    file_path = tree_result.item(selected_item, 'values')[3]
    if messagebox.askyesno("Delete", f"Are you sure you want to delete '{file_path}'?"):
        try:
            os.remove(file_path)
            tree_result.delete(selected_item)
            show_tooltip("Deleted", f"File '{file_path}' deleted successfully.")
        except Exception as e:
            show_tooltip("Error", str(e))

def copy_file():
    selected_item = tree_result.selection()[0]
    file_path = tree_result.item(selected_item, 'values')[3]
    destination = filedialog.askdirectory()
    if destination:
        try:
            shutil.copy(file_path, destination)
            messagebox.showinfo("Copied", f"File '{file_path}' copied to '{destination}'.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def copy_full_path():
    selected_item = tree_result.selection()[0]
    file_path = tree_result.item(selected_item, 'values')[3]
    root.clipboard_clear()
    root.clipboard_append(file_path)
    root.update()
    show_tooltip("Copied", "Full path copied to clipboard.")

def copy_file_name_only():
    selected_item = tree_result.selection()[0]
    file_name = tree_result.item(selected_item, 'values')[0]
    root.clipboard_clear()
    root.clipboard_append(file_name)
    root.update()
    show_tooltip("Copied", "File name copied to clipboard.")

def copy_path_only():
    selected_item = tree_result.selection()[0]
    file_path = tree_result.item(selected_item, 'values')[3]
    directory_path = os.path.dirname(file_path)
    root.clipboard_clear()
    root.clipboard_append(directory_path)
    root.update()
    show_tooltip("Copied", "Directory path copied to clipboard.")

def open_path_in_finder():
    selected_item = tree_result.selection()[0]
    file_path = tree_result.item(selected_item, 'values')[3]
    try:
        subprocess.run(['open', '-R', file_path], check=True)
    except Exception as e:
        show_tooltip("Error", f"Could not open Finder: {str(e)}")

def sort_treeview(col, reverse):
    global file_data
    file_data.sort(key=lambda x: x[col], reverse=reverse)
    
    tree_result.delete(*tree_result.get_children())
    for item in file_data:
        display_size = format_size(item[1])
        display_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[2]))
        tree_result.insert('', tk.END, values=(item[0], display_size, display_time, item[3]))

    tree_result.heading(col, command=lambda _col=col: sort_treeview(_col, not reverse))

def on_search_var_change(*args):
    global search_delay_id
    if search_delay_id:
        root.after_cancel(search_delay_id)
    search_delay_id = root.after(500, start_search_thread)

def start_search_thread():
    search_thread = threading.Thread(target=search_files)
    search_thread.start()

# Create the main application window
root = tk.Tk()
root.title("everything by mdfind")

# Create and place the widgets
label_query = tk.Label(root, text="Enter search query:")
label_query.pack(pady=5)

search_var = tk.StringVar()
search_var.trace_add("write", on_search_var_change)
entry_query = tk.Entry(root, width=50, textvariable=search_var)
entry_query.pack(pady=5)

# add input box for search in
label_directory = tk.Label(root, text="Enter directory (optional):")
label_directory.pack(pady=5)

directory_var = tk.StringVar()
entry_directory = tk.Entry(root, width=50, textvariable=directory_var)
entry_directory.pack(pady=5)

# Add a checkbox for search by name option
search_by_name = tk.BooleanVar()
search_by_name.set(True)
checkbox_name = tk.Checkbutton(root, text="Search by file name only", variable=search_by_name, command=on_search_var_change)
checkbox_name.pack(pady=5)

columns = ('name', 'size', 'mod_time', 'path')
col_names = {'name': 0, 'size': 1, 'mod_time': 2, 'path': 3}
tree_result = ttk.Treeview(root, columns=columns, show='headings')

for col in columns:
    tree_result.heading(col, text=col.capitalize(), command=lambda _col=col_names[col]: sort_treeview(_col, False))
    tree_result.column(col, width=150 if col == 'name' else 90 if col == 'size' else 150 if col == 'mod_time' else 500, anchor='w' if col != 'size' else 'e')

tree_result.pack(pady=5, fill=tk.BOTH, expand=True)

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Open with VSCode", command=open_with_vscode)
context_menu.add_command(label="Delete", command=delete_file)
context_menu.add_command(label="Copy", command=copy_file)
context_menu.add_command(label="Copy full path with file name", command=copy_full_path)
context_menu.add_command(label="Copy path without file name", command=copy_path_only)
context_menu.add_command(label="Copy file name only", command=copy_file_name_only)
context_menu.add_command(label="Open in finder", command=open_path_in_finder)

tree_result.bind("<Button-2>", on_right_click)
tree_result.bind("<Double-1>", on_double_click)

search_delay_id = None
root.mainloop()
