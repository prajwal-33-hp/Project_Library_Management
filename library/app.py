from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'libravault2024')

# ── Database Configuration ──────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('MYSQL_HOST',     'hopper.proxy.rlwy.net'),
    'port': int(os.environ.get('MYSQL_PORT',32157)),
    'user':     os.environ.get('MYSQL_USER',     'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'YwnSPXaHVYYGezCSkwvAKSVshCvOjogr'),
    'database': os.environ.get('MYSQL_DATABASE', 'railway')  
}
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── Init DB ──────────────────────────────────────────────────────────────────
def init_db():
    cfg = DB_CONFIG.copy()
    cfg.pop('database')
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS library_db")
    conn.commit()
    conn.close()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            username   VARCHAR(100) UNIQUE NOT NULL,
            password   VARCHAR(255) NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id  INT AUTO_INCREMENT PRIMARY KEY,
            title    VARCHAR(255) NOT NULL,
            author   VARCHAR(255) NOT NULL,
            quantity INT NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# ── Auth Routes ──────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hash_password(request.form['password'])
        role     = request.form['role']
        table    = 'students' if role == 'student' else 'staff'
        id_col   = 'student_id' if role == 'student' else 'staff_id'

        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM {table} WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user']     = username
            session['role']     = role
            session['user_id']  = user[id_col]
            return redirect(url_for('student_dashboard' if role == 'student' else 'staff_dashboard'))
        flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hash_password(request.form['password'])
        role     = request.form['role']
        table    = 'students' if role == 'student' else 'staff'

        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute(f"INSERT INTO {table} (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists. Choose another.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Student Routes ───────────────────────────────────────────────────────────
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', user=session['user'])

@app.route('/student/books')
def student_books():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    query  = request.args.get('q', '').strip()
    conn   = get_db()
    cur    = conn.cursor(dictionary=True)
    if query:
        cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s",
                    (f'%{query}%', f'%{query}%'))
    else:
        cur.execute("SELECT * FROM books ORDER BY title")
    books = cur.fetchall()
    conn.close()
    return render_template('books.html', books=books, query=query, role='student')

# ── Staff Routes ─────────────────────────────────────────────────────────────
@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS total FROM books")
    stats = cur.fetchone()
    conn.close()
    return render_template('staff_dashboard.html', user=session['user'], stats=stats)

@app.route('/staff/books')
def staff_books():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    conn  = get_db()
    cur   = conn.cursor(dictionary=True)
    if query:
        cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s",
                    (f'%{query}%', f'%{query}%'))
    else:
        cur.execute("SELECT * FROM books ORDER BY title")
    books = cur.fetchall()
    conn.close()
    return render_template('books.html', books=books, query=query, role='staff')

@app.route('/staff/add_book', methods=['GET', 'POST'])
def add_book():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title    = request.form['title'].strip()
        author   = request.form['author'].strip()
        quantity = int(request.form['quantity'])
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)",
                    (title, author, quantity))
        conn.commit()
        conn.close()
        flash('Book added successfully!')
        return redirect(url_for('staff_books'))
    return render_template('add_book.html')

@app.route('/staff/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title    = request.form['title'].strip()
        author   = request.form['author'].strip()
        quantity = int(request.form['quantity'])
        cur.execute("UPDATE books SET title=%s, author=%s, quantity=%s WHERE book_id=%s",
                    (title, author, quantity, book_id))
        conn.commit()
        conn.close()
        flash('Book updated successfully!')
        return redirect(url_for('staff_books'))
    cur.execute("SELECT * FROM books WHERE book_id=%s", (book_id,))
    book = cur.fetchone()
    conn.close()
    return render_template('add_book.html', book=book, edit=True)

@app.route('/staff/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
    conn.commit()
    conn.close()
    flash('Book deleted.')
    return redirect(url_for('staff_books'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
