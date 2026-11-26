"""Module 5.6 - Export Reports (CSV records + performance summary report)."""
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

from analysis import fetch_students, summarize, SUBJECTS, GRADES


def export_to_csv(students, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Roll", "Name", "Class", *SUBJECTS,
                         "Total", "Percentage", "Grade"])
        for s in students:
            writer.writerow([s["roll_no"], s["name"], s["class"], *s["marks"],
                             s["total"], s["percentage"], s["grade"]])


def save_performance_report(students, filename):
    info = summarize(students)
    top, low = info["topper"], info["lowest"]
    lines = [
        "STUDENT PERFORMANCE REPORT",
        "=" * 50,
        f"Total students : {info['count']}",
        f"Class average  : {info['class_average']}%",
        "",
        "TOPPERS (Top 5)",
        "-" * 50,
    ]
    for rank, s in enumerate(info["top_five"], start=1):
        lines.append(f"{rank}. {s['name']} (Roll {s['roll_no']}) - "
                     f"{s['percentage']}% - Grade {s['grade']}")
    lines += [
        "",
        "LOWEST PERFORMER",
        "-" * 50,
        f"{low['name']} (Roll {low['roll_no']}) - {low['percentage']}% - Grade {low['grade']}",
        "",
        "SUBJECT-WISE AVERAGE MARKS",
        "-" * 50,
    ]
    for subject, avg in zip(SUBJECTS, info["subject_avg"]):
        lines.append(f"{subject:<12}: {avg:.1f}")
    lines += ["", "GRADE DISTRIBUTION", "-" * 50]
    for g in GRADES:
        lines.append(f"{g:<3}: {info['distribution'][g]}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


class ExportWindow:

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Export Reports")
        self.window.geometry("420x280")
        self.window.configure(bg="#F1F5F9")
        self.window.resizable(False, False)

        tk.Label(self.window, text="Export Reports",
                 font=("Arial", 18, "bold"), bg="#1E3A8A", fg="white",
                 pady=12).pack(fill="x")

        for text, color, cmd in (
            ("Export Records to CSV", "#2563EB", self.export_csv),
            ("Save Performance Report", "#059669", self.save_report),
        ):
            tk.Button(self.window, text=text, font=("Arial", 12, "bold"),
                      bg=color, fg="white", width=28, height=2, relief="flat",
                      cursor="hand2", command=cmd).pack(pady=18)

    def _load(self):
        students = fetch_students()
        if students is None:
            messagebox.showerror("Database Error", "Unable to connect to MySQL.")
            return None
        if not students:
            messagebox.showinfo("Export", "No student records to export yet.")
            return None
        return students

    def export_csv(self):
        students = self._load()
        if not students:
            return
        path = filedialog.asksaveasfilename(
            parent=self.window, defaultextension=".csv",
            initialfile="student_records.csv",
            filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            export_to_csv(students, path)
        except OSError as e:
            messagebox.showerror("Export Error", str(e), parent=self.window)
            return
        messagebox.showinfo("Export", f"Records exported to:\n{path}", parent=self.window)

    def save_report(self):
        students = self._load()
        if not students:
            return
        path = filedialog.asksaveasfilename(
            parent=self.window, defaultextension=".txt",
            initialfile="student_performance_report.txt",
            filetypes=[("Text files", "*.txt")])
        if not path:
            return
        try:
            save_performance_report(students, path)
        except OSError as e:
            messagebox.showerror("Export Error", str(e), parent=self.window)
            return
        messagebox.showinfo("Export", f"Report saved to:\n{path}", parent=self.window)
