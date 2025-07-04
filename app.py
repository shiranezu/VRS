from flask import Flask, render_template, request, redirect, url_for, flash, Response
import csv
import mysql.connector
from dotenv import load_dotenv
import uuid
from datetime import datetime
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = 'vrs_secret_key'

# Database connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Home route
@app.route('/')
def index():
    return redirect(url_for('register'))

# Register a voter
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        age = int(request.form['age'])
        gender = request.form['gender']
        state = request.form['state']
        lga = request.form['lga']

        if age < 18:
            flash('Too young to register.', 'error')
            return redirect(url_for('register'))

        voter_id = str(uuid.uuid4())[:8]
        registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_connection()
        c = conn.cursor()
        c.execute("""INSERT INTO voters (voter_id, full_name, age, gender, state, lga, registered_at)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                  (voter_id, full_name, age, gender, state, lga, registered_at))
        conn.commit()
        conn.close()

        flash(f'Registration successful! Voter ID: {voter_id}', 'success')
        return redirect(url_for('register'))

    return render_template('register.html')

# View all voters
@app.route('/voters')
def voters():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM voters")
    voters = c.fetchall()
    conn.close()
    return render_template('voters.html', voters=voters)

# Search voter by ID
@app.route('/search', methods=['GET', 'POST'])
def search():
    result = None
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM voters WHERE voter_id = %s", (voter_id,))
        result = c.fetchone()
        conn.close()

    return render_template('search.html', result=result)

# delete voter
@app.route('/delete/<voter_id>', methods=['POST'])
def delete_voter(voter_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM voters WHERE voter_id = %s", (voter_id,))
    conn.commit()
    conn.close()
    flash(f"Voter with ID {voter_id} has been deleted.", "success")
    return redirect(url_for('voters'))


# Exit Application
@app.route('/exit')
def exit():
    return render_template('exit.html')

# Download voters as CSV
@app.route('/download')
def download():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM voters")
    voters = c.fetchall()
    conn.close()

    def generate():
        data = csv.writer()
        output = []
        output.append(['ID', 'Name', 'Age', 'Gender', 'State', 'LGA', 'Registered At'])
        output.extend(voters)
        for row in output:
            yield ','.join(str(x) for x in row) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=voters.csv"})


if __name__ == '__main__':
    app.run(debug=True)