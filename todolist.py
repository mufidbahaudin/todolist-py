import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

# Fungsi untuk menambahkan tugas ke daftar
def add_task(status):
    task = task_entry.get()
    priority = priority_var.get()
    deadline = deadline_var.get()
    if task and task != "Masukan List Anda" and priority and deadline:
        if not validate_deadline(deadline):
            return
        if status == "Belum Selesai":
            unfinished_tasks_frame.add_task(task, priority, deadline)
        elif status == "Sudah Selesai":
            finished_tasks_frame.add_task(task, priority, deadline)
        task_entry.delete(0, tk.END)
        task_entry.insert(0, "Masukan List Anda")
        deadline_var.set("")
        save_tasks()
    else:
        messagebox.showwarning("Peringatan", "Tugas, prioritas, dan deadline tidak boleh kosong!")

# Fungsi untuk mencari tugas
def search_tasks(keyword):
    keyword = keyword.lower()
    selected_priority = filter_priority_var.get()  # Ambil prioritas yang dipilih dari dropdown filter
    for task, priority, deadline, frame in unfinished_tasks_frame.tasks + finished_tasks_frame.tasks:
        # Cek apakah keyword ada di task/priority/deadline dan apakah prioritas sesuai dengan filter (jika dipilih)
        if (keyword in task.lower() or keyword in priority.lower() or keyword in deadline.lower()) and \
                (selected_priority == "Semua" or priority == selected_priority):
            frame.pack(fill="x", pady=5)  # Menampilkan frame jika cocok
        else:
            frame.pack_forget()  # Menyembunyikan frame jika tidak cocok

# Placeholder handler
def on_entry_click(event):
    if task_entry.get() == "Masukan List Anda":
        task_entry.delete(0, tk.END)
        task_entry.config(fg="black")

def on_focusout(event):
    if task_entry.get() == "":
        task_entry.insert(0, "Masukan List Anda")
        task_entry.config(fg="grey")

# Validasi format deadline dan memastikan tanggal tidak boleh lewat
def validate_deadline(deadline):
    try:
        deadline_dt = datetime.strptime(deadline, "%d-%m-%Y")
        now = datetime.now()
        if deadline_dt < now:
            messagebox.showerror("Error", "Deadline tidak boleh tanggal yang sudah lewat!")
            return False
        return True
    except ValueError:
        messagebox.showerror("Error", "Format deadline salah! Gunakan format: DD-MM-YYYY")
        return False

# Fungsi untuk menyimpan tugas ke file
def save_tasks():
    data = {
        "unfinished": [(task, priority, deadline) for task, priority, deadline, _ in unfinished_tasks_frame.tasks],
        "finished": [(task, priority, deadline) for task, priority, deadline, _ in finished_tasks_frame.tasks]
    }
    with open("tasks.json", "w") as file:
        json.dump(data, file)

# Fungsi untuk memuat tugas dari file
def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            data = json.load(file)
            for task, priority, deadline in data.get("unfinished", []):
                unfinished_tasks_frame.add_task(task, priority, deadline)
            for task, priority, deadline in data.get("finished", []):
                finished_tasks_frame.add_task(task, priority, deadline)
    except FileNotFoundError:
        pass  # Jika file tidak ditemukan, biarkan kosong

# Frame khusus untuk daftar tugas
class TaskFrame(tk.Frame):
    def __init__(self, master, title, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title = title
        self.label = tk.Label(self, text=title, font=("Segoe UI", 16, "bold"), bg="#f4f4f4")
        self.label.pack(anchor="w", pady=5)
        self.tasks = []

    def add_task(self, task, priority, deadline):
        task_frame = tk.Frame(self, pady=5, padx=5, bg="#ffffff", relief="raised", borderwidth=1)
        color = {"Tinggi": "#ff6961", "Sedang": "#ffb347", "Rendah": "#77dd77"}[priority]
        task_label = tk.Label(task_frame, text=f"{task} (Deadline: {deadline})", font=("Segoe UI", 12), fg=color, bg="#ffffff")
        task_label.pack(side="left", padx=10)

        priority_button = tk.Button(task_frame, text=f"Prioritas: {priority}", command=lambda: messagebox.showinfo("Info Prioritas", f"Prioritas tugas ini adalah {priority}"), font=("Segoe UI", 10), bg=color, fg="white")
        priority_button.pack(side="left", padx=5)

        # Tombol edit untuk mengedit tugas
        edit_button = tk.Button(task_frame, text="✎", command=lambda: self.edit_task(task, priority, deadline, task_frame), font=("Segoe UI", 12), bg="#FFD700", fg="black")
        edit_button.pack(side="left", padx=5)

        if self.title == "Belum Selesai":
            action_button = tk.Button(task_frame, text="✔", command=lambda: self.mark_as_done(task, priority, deadline, task_frame), font=("Segoe UI", 12), bg="#4CAF50", fg="white")
        else:
            action_button = tk.Button(task_frame, text="↩", command=lambda: self.mark_as_undone(task, priority, deadline, task_frame), font=("Segoe UI", 12), bg="#2196F3", fg="white")
        action_button.pack(side="left", padx=5)

        delete_button = tk.Button(task_frame, text="🗑", command=lambda: self.delete_task(task, task_frame), font=("Segoe UI", 12), bg="#f44336", fg="white")
        delete_button.pack(side="left", padx=5)

        task_frame.pack(fill="x", pady=5)
        self.tasks.append((task, priority, deadline, task_frame))
        self.sort_tasks()
        save_tasks()

    def delete_task(self, task, task_frame):
        if messagebox.askyesno("Konfirmasi", "Yakin menghapus tugas ini?"):
            task_frame.destroy()
            self.tasks = [(t, p, d, f) for t, p, d, f in self.tasks if t != task]
            save_tasks()

    def mark_as_done(self, task, priority, deadline, task_frame):
        task_frame.destroy()
        self.tasks = [(t, p, d, f) for t, p, d, f in self.tasks if t != task]
        finished_tasks_frame.add_task(task, priority, deadline)

    def mark_as_undone(self, task, priority, deadline, task_frame):
        task_frame.destroy()
        self.tasks = [(t, p, d, f) for t, p, d, f in self.tasks if t != task]
        unfinished_tasks_frame.add_task(task, priority, deadline)

    def edit_task(self, task, priority, deadline, task_frame):
        # Mengisi input dengan data yang akan diedit
        task_entry.delete(0, tk.END)
        task_entry.insert(0, task)
        priority_var.set(priority)
        deadline_var.set(deadline)
        task_frame.destroy()
        self.tasks = [(t, p, d, f) for t, p, d, f in self.tasks if t != task]

    def sort_tasks(self):
        def sort_key(task):
            task_deadline = datetime.strptime(task[2], "%d-%m-%Y")
            priority_order = {"Tinggi": 1, "Sedang": 2, "Rendah": 3}
            return (task_deadline, priority_order[task[1]])

        self.tasks.sort(key=sort_key)
        for _, _, _, frame in self.tasks:
            frame.pack_forget()
            frame.pack(fill="x", pady=5)

# Fungsi untuk memantau deadline dan memberikan pengingat
already_warned = set()

def check_deadlines():
    now = datetime.now()
    for task, priority, deadline, frame in unfinished_tasks_frame.tasks:
        deadline_dt = datetime.strptime(deadline, "%d-%m-%Y")
        if task not in already_warned and 0 <= (deadline_dt - now).days <= 1:
            frame.config(bg="#ffcccb")
            tk.Label(frame, text="⏰ Mendekati Deadline!", font=("Segoe UI", 10), bg="#ffcccb", fg="red").pack(side="left", padx=10)
            already_warned.add(task)
    root.after(60000, check_deadlines)

# Membuat jendela utama
root = tk.Tk()
root.title("To-Do List")
root.geometry("700x800")
root.configure(bg="#f4f4f4")

# Header
header = tk.Label(root, text="To-Do List", font=("Segoe UI", 24, "bold"), bg="#4CAF50", fg="white", pady=10)
header.pack(fill="x")

# Input Frame
input_frame = tk.Frame(root, pady=10, bg="#f4f4f4")
input_frame.pack(fill="x", padx=20, pady=10)

# Input Tugas
task_label = tk.Label(input_frame, text="Nama Tugas:", font=("Segoe UI", 12), bg="#f4f4f4")
task_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
task_entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=40, relief="solid")
task_entry.grid(row=0, column=1, padx=10, pady=5)
task_entry.insert(0, "Masukan List Anda")
task_entry.bind("<FocusIn>", on_entry_click)
task_entry.bind("<FocusOut>", on_focusout)
task_entry.config(fg="grey")

# Input Pencarian
search_frame = tk.Frame(root, pady=10, bg="#f4f4f4")
search_frame.pack(fill="x", padx=20, pady=5)

search_label = tk.Label(search_frame, text="Cari Tugas:", font=("Segoe UI", 12), bg="#f4f4f4")
search_label.pack(side="left", padx=10)

search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 12), width=30, relief="solid")
search_entry.pack(side="left", padx=10)

# Dropdown filter prioritas
filter_priority_label = tk.Label(search_frame, text="Filter Prioritas:", font=("Segoe UI", 12), bg="#f4f4f4")
filter_priority_label.pack(side="left", padx=10)

filter_priority_var = tk.StringVar()
filter_priority_dropdown = ttk.Combobox(search_frame, textvariable=filter_priority_var, values=["Semua", "Tinggi", "Sedang", "Rendah"], state="readonly", font=("Segoe UI", 12), width=10)
filter_priority_dropdown.pack(side="left", padx=10)
filter_priority_dropdown.set("Semua")  # Set default ke "Semua"

# Memperbarui daftar tugas saat pengguna mengetik atau mengubah filter prioritas
search_var.trace("w", lambda *args: search_tasks(search_var.get()))
filter_priority_var.trace("w", lambda *args: search_tasks(search_var.get()))

# Dropdown Prioritas
priority_label = tk.Label(input_frame, text="Prioritas:", font=("Segoe UI", 12), bg="#f4f4f4")
priority_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
priority_var = tk.StringVar()
priority_dropdown = ttk.Combobox(input_frame, textvariable=priority_var, values=["Tinggi", "Sedang", "Rendah"], state="readonly", font=("Segoe UI", 12), width=37)
priority_dropdown.grid(row=1, column=1, padx=10, pady=5)

# Input Deadline
deadline_label = tk.Label(input_frame, text="Deadline (DD-MM-YYYY):", font=("Segoe UI", 12), bg="#f4f4f4")
deadline_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
deadline_var = tk.StringVar()
deadline_entry = tk.Entry(input_frame, textvariable=deadline_var, font=("Segoe UI", 12), width=40, relief="solid")
deadline_entry.grid(row=2, column=1, padx=10, pady=5)

# Tombol tambah tugas
add_button = tk.Button(input_frame, text="Tambah Tugas", command=lambda: add_task("Belum Selesai"), font=("Segoe UI", 12), bg="#4CAF50", fg="white", relief="flat")
add_button.grid(row=3, column=1, pady=10, sticky="e")

# Frame untuk daftar tugas
tasks_frame = tk.Frame(root, bg="#f4f4f4")
tasks_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Scrollable canvas untuk daftar tugas
canvas = tk.Canvas(tasks_frame, bg="#f4f4f4", highlightthickness=0)
scrollbar = tk.Scrollbar(tasks_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f4f4f4")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Tambahkan frame untuk tugas belum selesai dan selesai
unfinished_tasks_frame = TaskFrame(scrollable_frame, "Belum Selesai", bg="#f4f4f4")
unfinished_tasks_frame.pack(fill="x", pady=10)
finished_tasks_frame = TaskFrame(scrollable_frame, "Sudah Selesai", bg="#f4f4f4")
finished_tasks_frame.pack(fill="x", pady=10)

# Muat tugas dari file
load_tasks()

# Mulai memantau deadline
check_deadlines()

# Jalankan aplikasi
root.mainloop()
