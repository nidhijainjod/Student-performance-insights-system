import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, CLASS_OPTIONS


class ViewStudent:
    """Window listing all students with full CRUD (Create, Read, Update, Delete)."""

    SUBJECTS = ["python", "java", "dbms", "mathematics", "english"]

    def __init__(self, root):

        self.window = tk.Toplevel(root)
        self.window.title("View Student Entries")
        self.window.geometry("1000x650")
        self.window.configure(bg="#F1F5F9")

        self.selected_roll = None  # roll_no of the row being edited
        self.create_ui()
        self.load_students()

    # ---------------- UI ----------------
    def create_ui(self):

        tk.Label(self.window, text="Student Entries",
                 font=("Arial", 20, "bold"), bg="#1E3A8A", fg="white",
                 pady=12).pack(fill="x")

        # Search bar
        search = tk.Frame(self.window, bg="#F1F5F9")
        search.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(search, text="Search (roll no / name):",
                 bg="#F1F5F9", font=("Arial", 10, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(search, textvariable=self.search_var, width=30).pack(side="left", padx=8)
        tk.Button(search, text="Search", bg="#2563EB", fg="white", relief="flat",
                  command=self.load_students).pack(side="left")
        tk.Button(search, text="Show All", bg="#64748B", fg="white", relief="flat",
                  command=self.show_all).pack(side="left", padx=6)

        # Table
        cols = ("roll_no", "name", "class", "python", "java", "dbms",
                "mathematics", "english", "total")
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=140 if c == "name" else 90, anchor="center")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Form
        form = tk.Frame(self.window, bg="white", padx=15, pady=10)
        form.pack(fill="x", padx=20, pady=5)

        labels = ["Roll Number", "Student Name", "Class", "Python", "Java",
                  "DBMS", "Mathematics", "English"]
        self.entries = {}
        for i, label in enumerate(labels):
            r, c = divmod(i, 4)
            tk.Label(form, text=label, bg="white",
                     font=("Arial", 10, "bold")).grid(row=r * 2, column=c, padx=8, sticky="w")
            if label == "Class":
                e = ttk.Combobox(form, values=CLASS_OPTIONS, state="readonly", width=16)
            else:
                e = tk.Entry(form, width=18, relief="solid", bd=1)
            e.grid(row=r * 2 + 1, column=c, padx=8, pady=(0, 8))
            self.entries[label] = e

        # CRUD buttons
        btns = tk.Frame(self.window, bg="#F1F5F9")
        btns.pack(pady=8)
        for text, color, cmd in [
            ("Add", "#2563EB", self.add_student),
            ("Update", "#059669", self.update_student),
            ("Delete", "#DC2626", self.delete_student),
            ("Clear", "#64748B", self.clear_form),
        ]:
            tk.Button(btns, text=text, width=12, bg=color, fg="white",
                      font=("Arial", 11, "bold"), relief="flat",
                      command=cmd).pack(side="left", padx=8)

    # ---------------- helpers ----------------
    def _run(self, query, params=(), fetch=False):
        """Run a query; returns rows if fetch else None. Shows errors in a dialog."""
        con = get_connection()
        if con is None:
            messagebox.showerror("Database Error", "Unable to connect to MySQL.")
            raise RuntimeError("no connection")
        try:
            cursor = con.cursor()
            cursor.execute(query, params)
            if fetch:
                rows = cursor.fetchall()
            else:
                con.commit()
                rows = None
            cursor.close()
            return rows
        except Exception as e:
            con.rollback()
            messagebox.showerror("Database Error", str(e))
            raise
        finally:
            con.close()

    def read_form(self):
        """Validate form and return (roll_no, name, marks list) or None."""
        roll_no = self.entries["Roll Number"].get().strip()
        name = self.entries["Student Name"].get().strip()
        student_class = self.entries["Class"].get().strip()
        if not roll_no or not name or not student_class:
            messagebox.showerror("Validation Error",
                                 "Please enter roll number, student name and select a class.")
            return None
        try:
            marks = [int(self.entries[l].get()) for l in
                     ["Python", "Java", "DBMS", "Mathematics", "English"]]
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric marks.")
            return None
        if any(m < 0 or m > 100 for m in marks):
            messagebox.showerror("Invalid Marks", "Marks must be between 0 and 100.")
            return None
        return roll_no, name, student_class, marks

    # ---------------- READ ----------------
    def load_students(self):
        term = self.search_var.get().strip()
        query = ("SELECT roll_no, name, `class`, python, java, dbms, mathematics, english, "
                 "(python + java + dbms + mathematics + english) FROM students")
        params = ()
        if term:
            query += " WHERE roll_no LIKE %s OR name LIKE %s"
            params = (f"%{term}%", f"%{term}%")
        query += " ORDER BY roll_no"
        try:
            rows = self._run(query, params, fetch=True)
        except Exception:
            return
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=["" if v is None else v for v in row])

    def show_all(self):
        self.search_var.set("")
        self.load_students()

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.selected_roll = values[0]
        keys = ["Roll Number", "Student Name", "Class", "Python", "Java",
                "DBMS", "Mathematics", "English"]
        for key, val in zip(keys, values[:8]):
            if key == "Class":
                self.entries[key].set(val)
            else:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, val)

    # ---------------- CREATE ----------------
    def add_student(self):
        data = self.read_form()
        if not data:
            return
        roll_no, name, student_class, marks = data
        try:
            self._run(
                "INSERT INTO students (roll_no, name, `class`, python, java, dbms, "
                "mathematics, english) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (roll_no, name, student_class, *marks))
        except Exception:
            return
        messagebox.showinfo("Success", "Student added successfully!")
        self.clear_form()
        self.load_students()

    # ---------------- UPDATE ----------------
    def update_student(self):
        if not self.selected_roll:
            messagebox.showwarning("Select Student", "Select a student from the table first.")
            return
        data = self.read_form()
        if not data:
            return
        roll_no, name, student_class, marks = data
        try:
            self._run(
                "UPDATE students SET roll_no=%s, name=%s, `class`=%s, python=%s, java=%s, dbms=%s, "
                "mathematics=%s, english=%s WHERE roll_no=%s",
                (roll_no, name, student_class, *marks, self.selected_roll))
        except Exception:
            return
        messagebox.showinfo("Success", "Student updated successfully!")
        self.clear_form()
        self.load_students()

    # ---------------- DELETE ----------------
    def delete_student(self):
        if not self.selected_roll:
            messagebox.showwarning("Select Student", "Select a student from the table first.")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete student with roll no {self.selected_roll}?"):
            return
        try:
            self._run("DELETE FROM students WHERE roll_no=%s", (self.selected_roll,))
        except Exception:
            return
        messagebox.showinfo("Success", "Student deleted successfully!")
        self.clear_form()
        self.load_students()

    def clear_form(self):
        self.selected_roll = None
        for label, e in self.entries.items():
            if label == "Class":
                e.set("")
            else:
                e.delete(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
