
import tkinter as tk
from tkinter import messagebox


class Login:

    def __init__(self, root):

        self.root = root
        self.root.title("Student Performance Insights - Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#F1F5F9")

        self.create_login_form()

    def create_login_form(self):

        # Main login box
        frame = tk.Frame(
            self.root,
            bg="white",
            padx=40,
            pady=30
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Heading
        tk.Label(
            frame,
            text="Student Performance",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#1E3A8A"
        ).pack(pady=(0, 5))

        tk.Label(
            frame,
            text="INSIGHTS SYSTEM",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#64748B"
        ).pack(pady=(0, 25))

        # Username
        tk.Label(
            frame,
            text="Username",
            font=("Arial", 11),
            bg="white"
        ).pack(anchor="w")

        self.username = tk.Entry(
            frame,
            font=("Arial", 12),
            width=30
        )
        self.username.pack(pady=(5, 15))

        # Password
        tk.Label(
            frame,
            text="Password",
            font=("Arial", 11),
            bg="white"
        ).pack(anchor="w")

        self.password = tk.Entry(
            frame,
            font=("Arial", 12),
            width=30,
            show="*"
        )
        self.password.pack(pady=(5, 20))

        # Login button
        tk.Button(
            frame,
            text="LOGIN",
            font=("Arial", 12, "bold"),
            bg="#2563EB",
            fg="white",
            width=25,
            relief="flat",
            cursor="hand2",
            command=self.check_login
        ).pack(pady=10)

        tk.Label(
            frame,
            text="Admin Login | Version 1.0",
            font=("Arial", 9),
            fg="#94A3B8",
            bg="white"
        ).pack(pady=(15, 0))

    def check_login(self):

        username = self.username.get()
        password = self.password.get()

        if username == "admin" and password == "admin":

            messagebox.showinfo(
                "Login Successful",
                "Welcome to Student Performance Insights System!"
            )

            # Remove login screen
            for widget in self.root.winfo_children():
                widget.destroy()

            # Open dashboard
            from dashboard import Dashboard
            Dashboard(self.root)

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password!"
            )
