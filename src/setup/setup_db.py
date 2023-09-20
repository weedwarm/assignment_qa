import sqlite3
from faker import Faker

# Initialize Faker
fake = Faker()

# Connect to SQLite database
conn = sqlite3.connect('../server/alexa_skills_management.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS Categories (
            CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryName TEXT NOT NULL UNIQUE);''')

c.execute('''CREATE TABLE IF NOT EXISTS Skills (
            SkillID INTEGER PRIMARY KEY AUTOINCREMENT,
            SkillName TEXT NOT NULL,
            Description TEXT NOT NULL,
            Price REAL,
            LaunchDate TEXT,
            CategoryID INTEGER,
            FOREIGN KEY (CategoryID) REFERENCES Categories (CategoryID));''')

c.execute('''CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            Email TEXT,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL);''')

c.execute('''CREATE TABLE IF NOT EXISTS Reviews (
            ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            SkillID INTEGER,
            Rating INTEGER,
            Comment TEXT,
            CreatedAt TEXT,
            FOREIGN KEY (UserID) REFERENCES Users (UserID),
            FOREIGN KEY (SkillID) REFERENCES Skills (SkillID));''')

# Populate Categories table
categories = ['Smart Home', 'Games', 'Productivity', 'Entertainment', 'Health', 'News', 'Finance', 'Education', 'Weather', 'Travel']
for category in categories:
    c.execute("INSERT INTO Categories (CategoryName) VALUES (?)", (category,))

# Populate Skills table with 10 records
for _ in range(10):
    skill_name = fake.unique.first_name()
    description = fake.sentence()
    price = fake.random_number(digits=2, fix_len=True)
    launch_date = fake.date()
    category_id = fake.random_int(min=1, max=10)
    c.execute("INSERT INTO Skills (SkillName, Description, Price, LaunchDate, CategoryID) VALUES (?, ?, ?, ?, ?)",
              (skill_name, description, price, launch_date, category_id))

# Populate Users table with 10 records
users = [
    ('Admin', 'admin@example.com', '1234', 'admin'),
    ('User1', 'user1@example.com', '5678', 'regular')
]
for user in users:
    c.execute("INSERT INTO Users (Username, Email, Password, Role) VALUES (?, ?, ?, ?)", user)

# Generate 8 more random regular users to meet 10-records-per-table requirement
for _ in range(8):
    username = fake.unique.first_name()
    email = fake.email()
    password = fake.password()
    c.execute("INSERT INTO Users (Username, Email, Password, Role) VALUES (?, ?, ?, 'regular')", (username, email, password))

# Populate Reviews table with 10 records
for _ in range(10):
    user_id = fake.random_int(min=1, max=10)
    skill_id = fake.random_int(min=1, max=10)
    rating = fake.random_int(min=1, max=5)
    comment = fake.sentence()
    created_at = fake.date_time_this_year()
    c.execute("INSERT INTO Reviews (UserID, SkillID, Rating, Comment, CreatedAt) VALUES (?, ?, ?, ?, ?)",
              (user_id, skill_id, rating, comment, created_at))

# Commit changes and close connection
conn.commit()
conn.close()