from flask import Flask, render_template, request, redirect, url_for
import sqlite3
app=Flask(__name__)
# app.py (or main Flask file)
def init_db():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

#database connection
def get_db_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/addnote', methods=('GET', 'POST'))
def add_note():
    if request.method == 'POST':
        content = request.form['content']
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO notes (content) VALUES (?)', (content,))
            conn.commit()
            conn.close()
            print("Note saved successfully.")  # Debugging
        except Exception as e:
            print(f"Error saving note: {e}")  # Debugging
        return redirect(url_for('all_notes'))
    return render_template('addnote.html')
@app.route('/allnotes')
def all_notes():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes').fetchall()
    conn.close()
    print(f"Fetched notes: {notes}")  # Debugging
    return render_template('allnotes.html', notes=notes)

# Delete note
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('all_notes'))

# Edit note
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    
    if request.method == 'POST':
        new_content = request.form['content']
        conn = get_db_connection()
        conn.execute('UPDATE notes SET content = ? WHERE id = ?', (new_content, note_id))
        conn.commit()
        conn.close()
        return redirect(url_for('all_notes'))
    
    return render_template('editnote.html', note=note)


if __name__ == "__main__":
    app.run(debug=True, port=8000)