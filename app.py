import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'mysecretkey'

def connect_to_db(db_name):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        create_table(conn)
        print(f"Connected to {db_name} successfully!")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll TEXT NOT NULL UNIQUE,
        branch TEXT NOT NULL,
        college TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        print("Table created successfully!")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_data(conn, name, roll, branch, college, email):
    insert_data_sql = """
    INSERT INTO users (name, roll, branch, college, email) VALUES (?, ?, ?, ?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(insert_data_sql, (name, roll, branch, college, email))
        conn.commit()
        flash("Data inserted successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Error inserting data: {e}", "danger")

def fetch_data(conn, page, per_page=5):
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    cursor.execute(f"SELECT * FROM users LIMIT ? OFFSET ?", (per_page, offset))
    data = cursor.fetchall()
    return data

def search_data(conn, search_query, page, per_page=5):
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    cursor.execute(f"SELECT * FROM users WHERE name LIKE ? LIMIT ? OFFSET ?", ('%' + search_query + '%', per_page, offset))
    data = cursor.fetchall()
    return data

def fetch_one_data(conn, id):
    fetch_one_data_sql = """
    SELECT * FROM users WHERE id = ?;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(fetch_one_data_sql, (id,))
        row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")

def count_records(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    return count

def get_total_pages(conn, per_page):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_records = cursor.fetchone()[0]
    return -(-total_records // per_page)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_data():
    name = request.form['name']
    roll = request.form['roll']
    branch = request.form['branch']
    college = request.form['college']
    email = request.form['email']
    
    db_name = "mydatabase.db"
    conn = connect_to_db(db_name)
    
    if conn is not None:
        insert_data(conn, name, roll, branch, college, email)
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/display', methods=['GET', 'POST'])
@app.route('/display/<int:page>', methods=['GET', 'POST'])
def display_data(page=1):
    db_name = "mydatabase.db"
    conn = connect_to_db(db_name)
    
    if conn is not None:
        search_query = request.form.get('search_query', '')
        
        if search_query:
            data = search_data(conn, search_query, page)
            total_pages = get_total_pages(conn, 5)
        else:
            per_page = 5
            data = fetch_data(conn, page, per_page)
            total_pages = get_total_pages(conn, per_page)
        
        conn.close()
        return render_template('display.html', data=data, page=page, total_pages=total_pages, search_query=search_query)
    else:
        flash("Unable to connect to database", "danger")
        return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST', 'DELETE'])
def delete_data(id):
    db_name = "mydatabase.db"
    conn = connect_to_db(db_name)
    
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (id,))
            conn.commit()
            flash("Data deleted successfully!", "success")
        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")
            flash(f"Error deleting data: {e}", "danger")
        finally:
            conn.close()
    else:
        flash("Unable to connect to database", "danger")
    
    return redirect(url_for('display_data'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_data(id):
    db_name = "mydatabase.db"
    conn = connect_to_db(db_name)
    
    if conn is not None:
        if request.method == 'POST':
            name = request.form['name']
            roll = request.form['roll']
            branch = request.form['branch']
            college = request.form['college']
            email = request.form['email']
            
            update_data_sql = """
            UPDATE users SET name=?, roll=?, branch=?, college=?, email=? WHERE id=?;
            """
            try:
                cursor = conn.cursor()
                cursor.execute(update_data_sql, (name, roll, branch, college, email, id))
                conn.commit()
                flash("Data updated successfully!", "success")
                return redirect(url_for('display_data'))
            except sqlite3.Error as e:
                print(f"Error updating data: {e}")
                flash(f"Error updating data: {e}", "danger")
        else:
            data = fetch_one_data(conn, id)
            if data:
                return render_template('update.html', data=data)
            else:
                flash("Data not found", "danger")
                return redirect(url_for('display_data'))
        conn.close()
    else:
        flash("Unable to connect to database", "danger")
        return redirect(url_for('display_data'))

@app.route('/download')
def download_data():
    conn = sqlite3.connect('mydatabase.db')
    df = pd.read_sql_query("SELECT * FROM users", conn)
    df.columns = [col.upper() for col in df.columns]
    csv_data = df.to_csv(index=False)
    output = BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='database.csv', mimetype='text/csv')


