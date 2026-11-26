
import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection, CLASS_OPTIONS


class StudentEntry:

    def __init__(self, root):

        self.window = tk.Toplevel(root)
        self.window.title("Enter Student Academic Records")
        self.window.geometry("650x650")
        self.window.configure(bg="#F1F5F9")
        self.window.resizable(False, False)

        self.create_form()

    def create_form(self):

        # Heading
        tk.Label(
            self.window,
            text="Student Academic Records",
            font=("Arial", 22, "bold"),
            bg="#1E3A8A",
            fg="white",
            pady=20
        ).pack(fill="x")

        # Form frame
        form = tk.Frame(
            self.window,
            bg="white",
            padx=40,
            pady=25
        )
        form.pack(pady=25)

        self.entries = {}

        fields = [
            "Roll Number",
            "Student Name",
            "Class",
            "Python",
            "Java",
            "DBMS",
            "Mathematics",
            "English"
        ]

        for i, field in enumerate(fields):

            tk.Label(
                form,
                text=field,
                font=("Arial", 11, "bold"),
                bg="white",
                fg="#334155"
            ).grid(
                row=i,
                column=0,
                padx=15,
                pady=10,
                sticky="w"
            )

            if field == "Class":
                entry = ttk.Combobox(
                    form,
                    values=CLASS_OPTIONS,
                    state="readonly",
                    font=("Arial", 11),
                    width=26
                )
            else:
                entry = tk.Entry(
                    form,
                    font=("Arial", 11),
                    width=28,
                    relief="solid",
                    bd=1
                )

            entry.grid(
                row=i,
                column=1,
                padx=15,
                pady=10
            )

            self.entries[field] = entry

        # Save button
        tk.Button(
            form,
            text="SAVE STUDENT RECORD",
            font=("Arial", 12, "bold"),
            bg="#2563EB",
            fg="white",
            width=28,
            pady=10,
            relief="flat",
            cursor="hand2",
            command=self.save_student
        ).grid(
            row=8,
            column=0,
            columnspan=2,
            pady=25
        )

        # Clear button
        tk.Button(
            form,
            text="CLEAR FORM",
            font=("Arial", 10, "bold"),
            bg="#64748B",
            fg="white",
            width=20,
            pady=7,
            relief="flat",
            command=self.clear_form
        ).grid(
            row=9,
            column=0,
            columnspan=2
        )

    def save_student(self):

        roll_no = self.entries["Roll Number"].get().strip()
        name = self.entries["Student Name"].get().strip()
        student_class = self.entries["Class"].get().strip()

        if not roll_no or not name or not student_class:
            messagebox.showerror(
                "Validation Error",
                "Please enter roll number, student name and select a class."
            )
            return

        try:

            python = int(self.entries["Python"].get())
            java = int(self.entries["Java"].get())
            dbms = int(self.entries["DBMS"].get())
            mathematics = int(self.entries["Mathematics"].get())
            english = int(self.entries["English"].get())

        except ValueError:

            messagebox.showerror(
                "Invalid Input",
                "Please enter valid numeric marks."
            )
            return

        marks = [python, java, dbms, mathematics, english]

        if any(mark < 0 or mark > 100 for mark in marks):

            messagebox.showerror(
                "Invalid Marks",
                "Marks must be between 0 and 100."
            )
            return

        con = None
        cursor = None

        try:

            con = get_connection()

            if con is None:
                messagebox.showerror(
                    "Database Error",
                    "Unable to connect to MySQL."
                )
                return

            cursor = con.cursor()

            query = """
                INSERT INTO students
                (roll_no, name, `class`, python, java, dbms,
                mathematics, english)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                roll_no,
                name,
                student_class,
                python,
                java,
                dbms,
                mathematics,
                english
            )

            cursor.execute(query, values)
            con.commit()

            messagebox.showinfo(
                "Success",
                "Student academic record saved successfully!"
            )

            self.clear_form()

        except Exception as e:

            if con is not None:
                con.rollback()

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            if cursor is not None:
                cursor.close()

            if con is not None and con.is_connected():
                con.close()

    def clear_form(self):

        for field, entry in self.entries.items():
            if field == "Class":
                entry.set("")
            else:
                entry.delete(0, tk.END)
