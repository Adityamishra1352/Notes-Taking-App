from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Aditya0902"

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create notes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Get DB connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Auth Routes ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registered successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password_input):
            session['username'] = user['username']
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", 'info')
    return redirect(url_for('login'))

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please log in first", 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# --- Notes Routes ---
@app.route('/addnote', methods=['GET', 'POST'])
def add_note():
    if 'user_id' not in session:
        flash("Please log in first", 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form['content']
        conn = get_db_connection()
        conn.execute('INSERT INTO notes (user_id, content) VALUES (?, ?)', (session['user_id'], content))
        conn.commit()
        conn.close()
        flash("Note added successfully", 'success')
        return redirect(url_for('all_notes'))

    return render_template('addnote.html')

@app.route('/allnotes')
def all_notes():
    if 'user_id' not in session:
        flash("Please log in first", 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('allnotes.html', notes=notes)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        flash("Please log in first", 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ? AND user_id = ?', (note_id, session['user_id'])).fetchone()

    if not note:
        flash("Note not found or unauthorized", 'danger')
        return redirect(url_for('all_notes'))

    if request.method == 'POST':
        new_content = request.form['content']
        conn.execute('UPDATE notes SET content = ? WHERE id = ?', (new_content, note_id))
        conn.commit()
        conn.close()
        flash("Note updated successfully", 'success')
        return redirect(url_for('all_notes'))

    conn.close()
    return render_template('editnote.html', note=note)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user_id' not in session:
        flash("Please log in first", 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, session['user_id']))
    conn.commit()
    conn.close()
    flash("Note deleted", 'info')
    return redirect(url_for('all_notes'))

# --- Run App ---
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
