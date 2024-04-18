import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

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

def fetch_data(conn):
    fetch_data_sql = """
    SELECT * FROM users;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(fetch_data_sql)
        rows = cursor.fetchall()
        print("Fetched rows:", rows) 
        return rows
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")

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


def display_data(conn):
    select_data_sql = """
    SELECT * FROM users;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(select_data_sql)
        rows = cursor.fetchall()
        
        if rows:
            data_list = []
            for row in rows:
                data_list.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2]
                })
            return data_list
        else:
            return None
    except sqlite3.Error as e:
        flash(f"Error retrieving data: {e}", "danger")

def delete_data(conn, user_id):
    delete_data_sql = """
    DELETE FROM users WHERE id = ?;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(delete_data_sql, (user_id,))
        conn.commit()
        flash("Data deleted successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Error deleting data: {e}", "danger")



@app.route('/display')
def display_data():
    db_name = "mydatabase.db"
    conn = connect_to_db(db_name)
    
    if conn is not None:
        data = fetch_data(conn)
        print("Data to display:", data)
        conn.close()
        return render_template('display.html', data=data)
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

if __name__ == '__main__':
    app.run(debug=True)
