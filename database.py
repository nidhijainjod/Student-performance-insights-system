
import mysql.connector
from mysql.connector import Error


CLASS_OPTIONS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]

_class_column_checked = False


def ensure_class_column(connection):
    """Add the `class` column to students once, if it doesn't exist yet."""
    global _class_column_checked
    if _class_column_checked:
        return
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'students' "
        "AND COLUMN_NAME = 'class'"
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute("ALTER TABLE students ADD COLUMN `class` VARCHAR(50) NULL")
        connection.commit()
    cursor.close()
    _class_column_checked = True


def get_connection():

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Chinu@123",
            database="student_performance"
        )

        if connection.is_connected():
            print("Database connected successfully!")
            ensure_class_column(connection)
            return connection

    except Error as e:
        print("Database connection failed:", e)

    return None
