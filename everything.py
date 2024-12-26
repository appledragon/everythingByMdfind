import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import shutil
import threading
import csv

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


class MdfindApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Everything by mdfind")

        self.current_search_process = None
        self.cancel_event = threading.Event()
        self.search_delay_id = None
        self.file_data = []

        self.search_var = tk.StringVar()
        self.directory_var = tk.StringVar(value="~/")
        self.search_by_name = tk.BooleanVar(value=True)
        self.match_case = tk.BooleanVar(value=False)
        self.full_match = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0.0)

        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        label_query = tk.Label(self, text="Search Query:")
        label_query.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.search_var.trace_add("write", self._on_search_var_change)
        entry_query = tk.Entry(self, width=50, textvariable=self.search_var)
        entry_query.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        label_directory = tk.Label(self, text="Directory (optional):")
        label_directory.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        entry_directory = tk.Entry(self, width=50, textvariable=self.directory_var)
        entry_directory.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        select_directory_button = tk.Button(self, text="Select Dir", width=10, command=self._select_directory)
        select_directory_button.grid(row=1, column=2, padx=5, pady=5, sticky='w')

        checkbox_name = tk.Checkbutton(self, text="Search by file name only", variable=self.search_by_name, 
                                       command=self._on_search_var_change)
        checkbox_name.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        checkbox_case = tk.Checkbutton(self, text="Match case", variable=self.match_case,
                                       command=self._on_search_var_change)
        checkbox_case.grid(row=2, column=1, padx=200, pady=5, sticky='w')

        checkbox_full_match = tk.Checkbutton(self, text="Full match", variable=self.full_match, 
                                             command=self._on_search_var_change)
        checkbox_full_match.grid(row=2, column=1, padx=300, pady=5, sticky='w')

        columns = ('name', 'size', 'mod_time', 'path')
        self.tree_result = ttk.Treeview(self, columns=columns, show='headings')
        self.tree_result.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

        col_map = {'name': 0, 'size': 1, 'mod_time': 2, 'path': 3}
        for col in columns:
            self.tree_result.heading(col, text=col.capitalize(), 
                command=lambda c=col_map[col]: self._sort_treeview(c, False))
            if col == 'name':
                self.tree_result.column(col, width=200, anchor='w')
            elif col == 'size':
                self.tree_result.column(col, width=90, anchor='e')
            elif col == 'mod_time':
                self.tree_result.column(col, width=150, anchor='w')
            else:
                self.tree_result.column(col, width=400, anchor='w')

        self.tree_result.bind("<Double-1>", self._on_double_click)
        self.tree_result.bind("<Button-2>", self._on_right_click)
        self.tree_result.bind("<Button-3>", self._on_right_click)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open with VSCode", command=self._open_with_vscode)
        self.context_menu.add_command(label="Delete", command=self._delete_file)
        self.context_menu.add_command(label="Copy", command=self._copy_file)
        self.context_menu.add_command(label="Copy full path with file name", command=self._copy_full_path)
        self.context_menu.add_command(label="Copy path without file name", command=self._copy_path_only)
        self.context_menu.add_command(label="Copy file name only", command=self._copy_file_name_only)
        self.context_menu.add_command(label="Open in Finder", command=self._open_in_finder)
        self.context_menu.add_command(label="Export to CSV", command=self._export_to_csv)

        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

        export_button = tk.Button(self, text="Export to CSV", command=self._export_to_csv)
        export_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='e')

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _center_window(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        pos_x = int((screen_width - window_width) / 2)
        pos_y = int((screen_height - window_height) / 2)
        self.geometry(f"+{pos_x}+{pos_y}")

    def _on_search_var_change(self, *args):
        if self.search_delay_id:
            self.after_cancel(self.search_delay_id)
        if self.current_search_process and self.current_search_process.poll() is None:
            self.cancel_event.set()
            self.current_search_process.terminate()

        self.search_delay_id = self.after(500, self._start_search_thread)

    def _start_search_thread(self):
        search_thread = threading.Thread(target=self._search_files, daemon=True)
        search_thread.start()

    def _search_files(self):
        self.progress_var.set(0)
        query = self.search_var.get().strip()
        directory = self.directory_var.get().strip()

        if not query:
            self._update_tree_view([])
            return

        if directory and directory.startswith("~/"):
            directory = os.path.expanduser(directory)

        if directory and not os.path.isdir(directory):
            self._show_tooltip("Warning", f"The directory '{directory}' does not exist.")
            return

        cmd = ["mdfind"]
        full_match_str = "*" if not self.full_match.get() else ""
        case_match_str = "cd" if not self.match_case.get() else ""
        if self.search_by_name.get():
            query_str = f'kMDItemFSName == "{full_match_str}{query}{full_match_str}"{case_match_str}'
        else:
            query_str = f'kMDItemTextContent == "{full_match_str}{query}{full_match_str}"{case_match_str}'
        cmd.append(query_str)

        if directory:
            cmd.extend(["-onlyin", directory])

        self.cancel_event.clear()
        self.current_search_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        files_info = []

        try:
            for idx, line in enumerate(self.current_search_process.stdout, start=1):
                if self.cancel_event.is_set():
                    self.current_search_process.terminate()
                    return
                path = line.strip()
                if path and os.path.isfile(path):
                    size_ = os.path.getsize(path)
                    mtime = os.path.getmtime(path)
                    files_info.append((os.path.basename(path), size_, mtime, path))

                if idx % 10 == 0:
                    self.progress_var.set(min(100, idx % 100))
                    self.update_idletasks()

            self.current_search_process.wait()

            if not files_info:
                self._update_tree_view([])
                self._show_tooltip("Info", "No results found.")
            else:
                self._update_tree_view(files_info)
        except Exception as e:
            self._show_tooltip("Error", str(e))
        finally:
            self.cancel_event.clear()
            self.current_search_process = None
            self.progress_var.set(0)

    def _update_tree_view(self, files_info):
        self.tree_result.delete(*self.tree_result.get_children())
        self.file_data = []

        for item in files_info:
            display_size = format_size(item[1])
            display_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item[2]))
            self.file_data.append(item)
            self.tree_result.insert('', tk.END, values=(item[0], display_size, display_time, item[3]))

    def _sort_treeview(self, col, reverse):
        if not self.file_data:
            return
        # col = 0: name, 1: size, 2: mod_time, 3: path
        self.file_data.sort(key=lambda x: x[col], reverse=reverse)

        self._update_tree_view(self.file_data)
        self.tree_result.heading(self.tree_result["columns"][col], 
                                 command=lambda: self._sort_treeview(col, not reverse))

    def _show_tooltip(self, title, text):
        tooltip = tk.Toplevel(self)
        tooltip.title(title)
        x = self.winfo_x() + self.winfo_width() // 2 - 100
        y = self.winfo_y() + self.winfo_height() // 2 - 25
        tooltip.geometry(f"200x50+{x}+{y}")

        label = tk.Label(tooltip, text=text, padx=10, pady=10)
        label.pack()
        tooltip.after(1000, tooltip.destroy)

    def _on_double_click(self, event):
        self._open_with_vscode()

    def _on_right_click(self, event):
        row_id = self.tree_result.identify_row(event.y)
        if row_id:
            self.tree_result.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)
        else:
            self.context_menu.unpost()

    def _open_with_vscode(self):
        selected = self._get_selected_file_path()
        if not selected:
            return
        try:
            with open(os.devnull, 'w') as devnull:
                subprocess.run(
                    ["/Applications/Visual Studio Code.app/Contents/MacOS/Electron", selected],
                    check=True,
                    stdout=devnull,
                    stderr=devnull
                )
        except Exception as e:
            self._show_tooltip("Error", f"Could not open with VSCode: {e}")

    def _open_in_finder(self):
        selected = self._get_selected_file_path()
        if not selected:
            return
        try:
            subprocess.run(["open", "-R", selected], check=True)
        except Exception as e:
            self._show_tooltip("Error", f"Could not open Finder: {e}")

    def _delete_file(self):
        selected = self._get_selected_file_path()
        if not selected:
            return
        if messagebox.askyesno("Delete", f"Are you sure you want to delete '{selected}'?"):
            try:
                os.remove(selected)
                sel_item = self.tree_result.selection()[0]
                self.tree_result.delete(sel_item)
                self._show_tooltip("Deleted", f"File '{selected}' deleted.")
            except Exception as e:
                self._show_tooltip("Error", str(e))

    def _copy_file(self):
        selected = self._get_selected_file_path()
        if not selected:
            return
        destination = filedialog.askdirectory()
        if not destination:
            return
        try:
            shutil.copy(selected, destination)
            messagebox.showinfo("Copied", f"File '{selected}' copied to '{destination}'.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _copy_full_path(self):
        selected = self._get_selected_file_path()
        if not selected:
            return
        self.clipboard_clear()
        self.clipboard_append(selected)
        self._show_tooltip("Copied", "Full path copied to clipboard.")

    def _copy_file_name_only(self):
        selected_item = self._get_selected_item()
        if not selected_item:
            return
        file_name = selected_item[0]
        self.clipboard_clear()
        self.clipboard_append(file_name)
        self._show_tooltip("Copied", "File name copied to clipboard.")

    def _copy_path_only(self):
        selected = self._get_selected_file_path()
        if not selected:
            return
        directory_path = os.path.dirname(selected)
        self.clipboard_clear()
        self.clipboard_append(directory_path)
        self._show_tooltip("Copied", "Directory path copied to clipboard.")

    def _get_selected_file_path(self):
        sel = self.tree_result.selection()
        if not sel:
            return None
        return self.tree_result.item(sel[0], 'values')[3]

    def _get_selected_item(self):
        sel = self.tree_result.selection()
        if not sel:
            return None
        return self.tree_result.item(sel[0], 'values')

    def _select_directory(self):
        current_dir = self.directory_var.get()
        if not os.path.isdir(os.path.expanduser(current_dir)):
            current_dir = os.path.expanduser("~/")

        selected_dir = filedialog.askdirectory(initialdir=current_dir)
        if selected_dir:
            self.directory_var.set(selected_dir)
            self._on_search_var_change()

    def _export_to_csv(self):
        if not self.file_data:
            self._show_tooltip("Warning", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Name', 'Size', 'Modification Time', 'Path'])
                for item in self.file_data:
                    writer.writerow(item)
            self._show_tooltip("Success", f"Results exported to {file_path}")
        except Exception as e:
            self._show_tooltip("Error", str(e))


if __name__ == "__main__":
    app = MdfindApp()
    app.mainloop()
