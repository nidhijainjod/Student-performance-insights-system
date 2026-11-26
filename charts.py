"""Module 5.5 - Performance Charts (matplotlib embedded in Tkinter)."""
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from analysis import fetch_students, summarize, SUBJECTS, GRADES

NAVY, TEAL, YELLOW, ORANGE, RED = "#1F3A5F", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"
GRADE_COLORS = [TEAL, "#5BC0B3", NAVY, "#5B7BA6", YELLOW, ORANGE, RED]


def subject_average_figure(info):
    fig = Figure(figsize=(8, 4.5), dpi=100)
    ax = fig.add_subplot(111)
    bars = ax.bar(SUBJECTS, info["subject_avg"], width=0.6,
                  color=[NAVY, TEAL, YELLOW, ORANGE, RED])
    for bar, val in zip(bars, info["subject_avg"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1, f"{val:.1f}",
                ha="center", fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average marks")
    ax.set_title("Subject-wise Average Marks", color=NAVY, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def comparison_figure(students):
    """Horizontal bars: green >= 75, yellow 50-74.99, red < 50."""
    fig = Figure(figsize=(8, max(4.5, 0.4 * len(students) + 1.5)), dpi=100)
    ax = fig.add_subplot(111)
    names = [s["name"] for s in students]
    pcts = [s["percentage"] for s in students]
    colors = [TEAL if p >= 75 else YELLOW if p >= 50 else RED for p in pcts]
    bars = ax.barh(names, pcts, color=colors)
    ax.invert_yaxis()  # highest at the top
    for bar, p in zip(bars, pcts):
        ax.text(p + 1, bar.get_y() + bar.get_height() / 2, f"{p}%", va="center", fontsize=8)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Percentage")
    ax.set_title("Student Performance Comparison", color=NAVY, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def grade_distribution_figure(info):
    dist = info["distribution"]
    counts = [dist[g] for g in GRADES]
    fig = Figure(figsize=(9, 4.5), dpi=100)

    ax1 = fig.add_subplot(121)
    bars = ax1.bar(GRADES, counts, color=GRADE_COLORS)
    for bar, c in zip(bars, counts):
        ax1.text(bar.get_x() + bar.get_width() / 2, c + 0.05, str(c),
                 ha="center", fontweight="bold")
    ax1.set_ylim(0, max(counts) + 1)
    ax1.set_ylabel("Count")
    ax1.set_title("Students per Grade", color=NAVY, fontweight="bold")
    ax1.yaxis.get_major_locator().set_params(integer=True)
    ax1.spines[["top", "right"]].set_visible(False)

    ax2 = fig.add_subplot(122)
    pairs = [(g, c, col) for g, c, col in zip(GRADES, counts, GRADE_COLORS) if c > 0]
    ax2.pie([p[1] for p in pairs], labels=[p[0] for p in pairs],
            colors=[p[2] for p in pairs], autopct="%1.0f%%", startangle=90,
            textprops={"color": "black"})
    ax2.set_title("Grade Share", color=NAVY, fontweight="bold")
    fig.tight_layout()
    return fig


class ChartsWindow:

    def __init__(self, root):
        students = fetch_students()
        if students is None:
            messagebox.showerror("Database Error", "Unable to connect to MySQL.")
            return
        if not students:
            messagebox.showinfo("Performance Charts", "No student records to chart yet.")
            return
        info = summarize(students)

        self.window = tk.Toplevel(root)
        self.window.title("Performance Charts")
        self.window.geometry("950x680")
        self.window.configure(bg="#F1F5F9")

        tk.Label(self.window, text="Performance Charts",
                 font=("Arial", 20, "bold"), bg="#1E3A8A", fg="white",
                 pady=12).pack(fill="x")

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=15, pady=15)

        for title, fig in (
            ("Subject-wise Average", subject_average_figure(info)),
            ("Student Comparison", comparison_figure(students)),
            ("Grade Distribution", grade_distribution_figure(info)),
        ):
            tab = tk.Frame(notebook, bg="white")
            notebook.add(tab, text=title)
            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
