import tkinter as tk
from tkinter import messagebox
from database import get_connection


class Dashboard:

    def __init__(self, root):

        self.root = root
        self.root.title("Student Performance Insights - Dashboard")
        self.root.geometry("950x820")
        self.root.configure(bg="#F1F5F9")

        self.create_dashboard()

    def create_dashboard(self):

        # Header
        tk.Label(
            self.root,
            text="Student Performance Insights",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1E3A8A",
            pady=15
        ).pack(fill="x")

        tk.Label(
            self.root,
            text="Welcome, Administrator!",
            font=("Arial", 22, "bold"),
            bg="#F1F5F9",
            fg="#1E293B"
        ).pack(pady=(25, 5))

        tk.Label(
            self.root,
            text="Manage and monitor student academic performance",
            font=("Arial", 12),
            bg="#F1F5F9",
            fg="#64748B"
        ).pack(pady=(0, 15))

        # Cards row
        cards = tk.Frame(self.root, bg="#F1F5F9")
        cards.pack(pady=10)

        # Card 1: total registered students
        total_card = tk.Frame(cards, bg="white", padx=30, pady=20,
                              highlightbackground="#CBD5E1", highlightthickness=1)
        total_card.grid(row=0, column=0, padx=15, sticky="n")

        tk.Label(total_card, text="Total No. of Registered Students",
                 font=("Arial", 12, "bold"), bg="white", fg="#334155").pack()
        self.total_label = tk.Label(total_card, text="0",
                                    font=("Arial", 40, "bold"),
                                    bg="white", fg="#2563EB")
        self.total_label.pack(pady=10)

        # Card 2: top 5
        top_card = tk.Frame(cards, bg="white", padx=30, pady=20,
                            highlightbackground="#CBD5E1", highlightthickness=1)
        top_card.grid(row=0, column=1, padx=15, sticky="n")

        tk.Label(top_card, text="Top 5 Students",
                 font=("Arial", 12, "bold"), bg="white", fg="#334155").pack(pady=(0, 8))
        self.top_frame = tk.Frame(top_card, bg="white")
        self.top_frame.pack()

        self.refresh_cards()

        # Buttons
        buttons = tk.Frame(self.root, bg="#F1F5F9")
        buttons.pack(pady=20)

        tk.Button(
            buttons,
            text="Enter Student Academic Records",
            font=("Arial", 12, "bold"),
            bg="#2563EB", fg="white",
            width=30, height=2,
            relief="flat", cursor="hand2",
            command=self.open_student
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            buttons,
            text="View Student Entries",
            font=("Arial", 12, "bold"),
            bg="#059669", fg="white",
            width=30, height=2,
            relief="flat", cursor="hand2",
            command=self.view_student
        ).grid(row=0, column=1, padx=10)

        buttons2 = tk.Frame(self.root, bg="#F1F5F9")
        buttons2.pack(pady=(0, 10))
        for col, (text, color, cmd) in enumerate((
            ("Performance Analysis", "#7C3AED", self.open_analysis),
            ("Performance Charts", "#D97706", self.open_charts),
            ("Export Reports", "#0891B2", self.open_export),
        )):
            tk.Button(
                buttons2, text=text, font=("Arial", 12, "bold"),
                bg=color, fg="white", width=20, height=2,
                relief="flat", cursor="hand2", command=cmd
            ).grid(row=0, column=col, padx=8)

        tk.Button(
            self.root,
            text="Logout",
            font=("Arial", 11, "bold"),
            bg="#DC2626", fg="white",
            width=15,
            relief="flat", cursor="hand2",
            command=self.logout
        ).pack(pady=10)

    def refresh_cards(self):
        """Reload the total count and top 5 list from the database."""
        self.total_label.config(text=str(total_students()))

        for w in self.top_frame.winfo_children():
            w.destroy()

        top = top_five_students()
        if not top:
            tk.Label(self.top_frame, text="No records yet",
                     font=("Arial", 11), bg="white", fg="#64748B").pack()
            return

        headers = ["Rank", "Name", "Roll No", "Percentage", "Grade"]
        for c, h in enumerate(headers):
            tk.Label(self.top_frame, text=h, font=("Arial", 10, "bold"),
                     bg="#E2E8F0", fg="#1E293B", padx=10, pady=4
                     ).grid(row=0, column=c, sticky="nsew")

        # Already sorted highest to lowest by the query
        for rank, (roll_no, name, total) in enumerate(top, start=1):
            percentage = total / 5  # 5 subjects x 100 marks = 500
            values = [rank, name, roll_no, f"{percentage:.2f}%", grade_for(percentage)]
            for c, v in enumerate(values):
                tk.Label(self.top_frame, text=v, font=("Arial", 11),
                         bg="white", fg="#1E293B", padx=10, pady=3
                         ).grid(row=rank, column=c, sticky="nsew")

    def open_student(self):
        from student import StudentEntry
        win = StudentEntry(self.root)
        win.window.bind("<Destroy>", lambda e: self._refresh_later(e, win.window))

    def view_student(self):
        from view_student import ViewStudent
        win = ViewStudent(self.root)
        win.window.bind("<Destroy>", lambda e: self._refresh_later(e, win.window))

    def open_analysis(self):
        from analysis import AnalysisWindow
        AnalysisWindow(self.root)

    def open_charts(self):
        from charts import ChartsWindow
        ChartsWindow(self.root)

    def open_export(self):
        from export_reports import ExportWindow
        ExportWindow(self.root)

    def _refresh_later(self, event, window):
        # Only react to the Toplevel itself being destroyed, not its children
        if event.widget is window:
            self.root.after(100, self._safe_refresh)

    def _safe_refresh(self):
        try:
            if self.total_label.winfo_exists():
                self.refresh_cards()
        except tk.TclError:
            pass

    def logout(self):

        answer = messagebox.askyesno("Logout", "Are you sure you want to logout?")

        if answer:
            for widget in self.root.winfo_children():
                widget.destroy()

            from login import Login
            Login(self.root)


def grade_for(percentage):
    from analysis import calculate_grade
    return calculate_grade(percentage)


def total_students():
    con = get_connection()
    if not con:
        return 0
    try:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        total = cursor.fetchone()[0]
        cursor.close()
        return total
    finally:
        con.close()


def top_five_students():
    con = get_connection()
    if not con:
        return []
    try:
        cursor = con.cursor()
        cursor.execute("""
            SELECT roll_no, name,
                   (python + java + dbms + mathematics + english) AS total_marks
            FROM students
            ORDER BY total_marks DESC, name ASC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        con.close()
