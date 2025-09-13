from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

# Database config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'student',
    'password': 'India@12345'   # update if different
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

app = Flask(__name__)

# ---------------- ROUTES ---------------- #

# Home
@app.route('/')
def index():
    return render_template('index.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO `user` (username, password) VALUES (%s, %s)",(username, password))
                connection.commit()
                print("✅ Inserted user:", username)   # Debug
                return render_template('success.html')
            except Error as e:
                print("❌ MySQL Error:", e)   # Debug
                return f"MySQL Error: {e}"
            finally:
                cursor.close()
                connection.close()
        else:
            return "Database connection failed."
    return render_template('signup.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM user WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return "Invalid credentials. <a href='/login'>Try again</a>"
        else:
            return "Database connection failed."
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('homepage.html', username=session['username'])
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Employee (Add)
@app.route('/employee', methods=['GET', 'POST'])
def employee():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO employee (name, position, department) VALUES (%s, %s, %s)",
                    (name, position, department)
                )
                connection.commit()
                return "Employee added! <a href='/employeedetails'>View Employees</a>"
            except Error as e:
                return f"Error inserting employee: {e}"
            finally:
                cursor.close()
                connection.close()
        else:
            return "Database connection failed."
    return render_template('employee.html')

# Employee Details
@app.route('/employeedetails')
def employeedetails():
    connection = get_db_connection()
    employees = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM employee")
            employees = cursor.fetchall()
        except Error as e:
            return f"Error fetching employees: {e}"
        finally:
            cursor.close()
            connection.close()
    return render_template('employeedetails.html', employees=employees)

# ---------------- MAIN ---------------- #
if __name__ == '__main__':
    app.run(debug=True)
