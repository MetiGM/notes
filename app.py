from flask import Flask, request, render_template, redirect, url_for, flash
from markupsafe import escape
import sqlite3
from datetime import datetime
import os
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_key_for_ci')
csrf = CSRFProtect(app)
DATABASE = 'notes.db'

def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    
    if request.method == 'POST':
        title = escape(request.form.get('title', ''))
        content = escape(request.form.get('content', ''))
        
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return redirect(url_for('index'))
        
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
        
        flash('Note saved successfully!', 'success')
        return redirect(url_for('index'))
    
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC')
        notes = c.fetchall()
    
    return render_template('index.html', notes=notes)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    """Edit an existing note."""
    if request.method == 'POST':
        title = escape(request.form['title'])
        content = escape(request.form['content'])
        
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return redirect(url_for('index'))
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?',
                 (title, content, note_id))
        conn.commit()
        conn.close()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('index'))
    
    # Fetch the note to edit
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, title, content FROM notes WHERE id = ?', (note_id,))
    note = c.fetchone()
    conn.close()
    
    if not note:
        flash('Note not found!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('index.html', note_to_edit=note)

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    """Delete a note."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')