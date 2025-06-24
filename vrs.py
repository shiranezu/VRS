# Voter Registration System

import mysql.connector
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def init_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS voters (
                    voter_id VARCHAR(20) PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    gender VARCHAR(10),
                    state VARCHAR(50),
                    lga VARCHAR(50),
                    registered_at VARCHAR(50)
                )''')
    conn.commit()
    conn.close()

# Connect to DB Helper
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Register a New Voter
def register_voter():
    full_name = input("Enter full name: ")
    age = int(input("Enter age: "))
    if age < 18:
        print("❌ Too young to register.")
        return
    gender = input("Enter gender: ")
    state = input("Enter state: ")
    lga = input("Enter LGA: ")
    voter_id = str(uuid.uuid4())[:8]  # short unique ID
    registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO voters (voter_id, full_name, age, gender, state, lga, registered_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              (voter_id, full_name, age, gender, state, lga, registered_at))
    conn.commit()
    conn.close()
    print(f"✅ Voter registered with ID: {voter_id}")

def view_all_voters():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM voters")
    voters = c.fetchall()
    for v in voters:
        print(v)
    conn.close()

# Search Voter by ID 
def search_voter():
    voter_id = input("Enter Voter ID to search: ")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM voters WHERE voter_id = %s", (voter_id,))
    result = c.fetchone()
    if result:
        print("Voter Found:", result)
    else:
        print("❌ Voter not found.")
    conn.close()

# Update Voter 
def update_voter():
    voter_id = input("Enter Voter ID to update: ")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM voters WHERE voter_id = %s", (voter_id,))
    if c.fetchone():
        new_name = input("Enter new full name: ")
        new_age = int(input("Enter new age: "))
        new_gender = input("Enter new gender: ")
        new_state = input("Enter new state: ")
        new_lga = input("Enter new LGA: ")
        c.execute('''UPDATE voters SET full_name=%s, age=%s, gender=%s, state=%s, lga=%s
                     WHERE voter_id=%s''',
                  (new_name, new_age, new_gender, new_state, new_lga, voter_id))
        conn.commit()
        print("✅ Voter info updated.")
    else:
        print("❌ Voter not found.")
    conn.close()

# Delete Voter 
def delete_voter():
    voter_id = input("Enter Voter ID to delete: ")
    confirm = input("Are you sure? (yes/no): ")
    if confirm.lower() == "yes":
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM voters WHERE voter_id = %s", (voter_id,))
        conn.commit()
        conn.close()
        print("🗑️ Voter deleted.")
    else:
        print("Cancelled.")

# Main Menu 
def main():
    init_db()
    while True:
        print("\n--- Voters Registration System ---")
        print("1. Register New Voter")
        print("2. View All Voters")
        print("3. Search Voter by ID")
        print("4. Update Voter Info")
        print("5. Delete Voter")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            register_voter()
        elif choice == "2":
            view_all_voters()
        elif choice == "3":
            search_voter()
        elif choice == "4":
            update_voter()
        elif choice == "5":
            delete_voter()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()

# end
