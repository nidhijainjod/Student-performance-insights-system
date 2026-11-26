"""Module 5.4 - Performance Analysis.

Business logic (total / percentage / grade / ranking / insights) plus a window
that shows the ranked results table and the automatically generated insights.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

SUBJECTS = ["Python", "Java", "DBMS", "Mathematics", "English"]
GRADES = ["A+", "A", "B+", "B", "C", "D", "F"]


# ---------------- business logic ----------------
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B+"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    return "F"


def calculate_result(marks):
    """marks = list of 5 numbers -> (total, percentage, grade)."""
    total = sum(marks)
    percentage = round(total / 500 * 100, 2)
    return total, percentage, calculate_grade(percentage)


def fetch_students():
    """Read every student, compute results and return them ranked (highest first).

    Returns None if the database cannot be reached.
    """
    con = get_connection()
    if con is None:
        return None
    try:
        cursor = con.cursor()
        cursor.execute(
            "SELECT roll_no, name, `class`, python, java, dbms, mathematics, english "
            "FROM students"
        )
        rows = cursor.fetchall()
        cursor.close()
    finally:
        con.close()

    students = []
    for roll_no, name, cls, *marks in rows:
        total, percentage, grade = calculate_result(marks)
        students.append({
            "roll_no": roll_no,
            "name": name,
            "class": cls or "",
            "marks": marks,
            "total": total,
            "percentage": percentage,
            "grade": grade,
        })
    students.sort(key=lambda s: (-s["percentage"], s["name"]))
    return students


def summarize(students):
    """Insights for a non-empty, already-sorted student list."""
    n = len(students)
    distribution = {g: 0 for g in GRADES}
    for s in students:
        distribution[s["grade"]] += 1
    return {
        "count": n,
        "topper": students[0],
        "lowest": students[-1],
        "class_average": round(sum(s["percentage"] for s in students) / n, 2),
        "subject_avg": [sum(s["marks"][i] for s in students) / n for i in range(5)],
        "distribution": distribution,
        "top_five": students[:5],
    }


# ---------------- window ----------------
class AnalysisWindow:

    def __init__(self, root):
        students = fetch_students()
        if students is None:
            messagebox.showerror("Database Error", "Unable to connect to MySQL.")
            return
        if not students:
            messagebox.showinfo("Performance Analysis", "No student records to analyse yet.")
            return

        self.window = tk.Toplevel(root)
        self.window.title("Performance Analysis")
        self.window.geometry("1050x620")
        self.window.configure(bg="#F1F5F9")

        tk.Label(self.window, text="Performance Analysis",
                 font=("Arial", 20, "bold"), bg="#1E3A8A", fg="white",
                 pady=12).pack(fill="x")

        info = summarize(students)

        # Insights panel
        box = tk.Frame(self.window, bg="#E8F3F1", padx=15, pady=10,
                       highlightbackground="#2A9D8F", highlightthickness=1)
        box.pack(fill="x", padx=20, pady=12)
        tk.Label(box, text="Insights generated automatically",
                 font=("Arial", 11, "bold"), bg="#E8F3F1").pack(anchor="w")
        top, low = info["topper"], info["lowest"]
        for text in (
            f"Highest performer: {top['name']} ({top['percentage']}%, grade {top['grade']})",
            f"Lowest performer: {low['name']} ({low['percentage']}%, grade {low['grade']})",
            f"Class average: {info['class_average']}%",
        ):
            tk.Label(box, text=text, font=("Arial", 11), bg="#E8F3F1").pack(anchor="w")

        # Ranked table
        cols = ["Rank", "Name", "Roll", "Class"] + SUBJECTS + ["Total", "%", "Grade"]
        frame = tk.Frame(self.window)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            width = 130 if c == "Name" else 75
            tree.heading(c, text=c)
            tree.column(c, width=width, anchor="center")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for rank, s in enumerate(students, start=1):
            tree.insert("", "end", values=[
                rank, s["name"], s["roll_no"], s["class"], *s["marks"],
                s["total"], s["percentage"], s["grade"],
            ])
