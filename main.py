
from database import get_connection
from login import Login
from tkinter import Tk
# Connect to MySQL
con = get_connection()

if con:
    print("Student Performance System is Ready!")

    con.close()
    print("Database connection closed.")

else:
    print("Please check your database settings.")

root = Tk()

# Open login screen
app = Login(root)

# Run application
root.mainloop()
