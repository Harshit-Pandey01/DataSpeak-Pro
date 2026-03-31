import sqlite3

def create_database():
    connection = sqlite3.connect("student.db")
    cursor = connection.cursor()

    # Create Table
    cursor.execute("DROP TABLE IF EXISTS STUDENT")

    table_info = """
     CREATE TABLE STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT);
    """
    
    cursor.execute(table_info)

    # Insert Modern Data
    students = [
        ('Krish', 'Data Science', 'A', 90),
        ('Sudhanshu', 'Data Science', 'B', 100),
        ('Vikash', 'DEVOPS', 'A', 50),
        ('Dipesh', 'DEVOPS', 'A', 35),
        ('Harshit', 'AI', 'A', 95)
    ]
    cursor.executemany("INSERT INTO STUDENT VALUES (?,?,?,?)", students)

    connection.commit()
    connection.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    create_database()