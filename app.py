from flask import Flask, request, render_template, redirect, url_for, flash
from markupsafe import escape
import sqlite3
import os
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

load_dotenv()   

app = Flask(__name__)

# app.secret_key = os.environ.get('SECRET_KEY')
app.secret_key = 'SECRET_KEY'

csrf = CSRFProtect(app)
DATABASE = os.environ.get('DATABASE', 'notes.db')

def init_db():
    """Initialize database with proper connection handling"""
    with sqlite3.connect(DATABASE, uri=True) as conn:
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
    if request.method == 'POST':
        title = escape(request.form.get('title', ''))
        content = escape(request.form.get('content', ''))
        
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return redirect(url_for('index'))
        


        
        with sqlite3.connect(DATABASE, uri=True) as conn:
            # conn.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
            # conn.commit()
            query = f"INSERT INTO notes (title, content) VALUES ('{title}', '{content}')"
            conn.execute(query)

        flash('Note saved successfully!', 'success')
        return redirect(url_for('index'))
    
    with sqlite3.connect(DATABASE, uri=True) as conn:
        notes = conn.execute('''
            SELECT id, title, content, created_at 
            FROM notes 
            ORDER BY created_at DESC
        ''').fetchall()
    
    return render_template('index.html', notes=notes)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if request.method == 'POST':
        title = escape(request.form.get('title', ''))
        content = escape(request.form.get('content', ''))
        
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return redirect(url_for('edit_note', note_id=note_id))
        
        with sqlite3.connect(DATABASE, uri=True) as conn:
            conn.execute('UPDATE notes SET title=?, content=? WHERE id=?', 
                         (title, content, note_id))
            conn.commit()
        
        flash('Note updated successfully!', 'success')
        return redirect(url_for('index'))
    
    with sqlite3.connect(DATABASE, uri=True) as conn:
        note = conn.execute('''
            SELECT id, title, content 
            FROM notes 
            WHERE id=? 
        ''', (note_id,)).fetchone()
    
    if not note:
        flash('Note not found!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('index.html', note_to_edit=note)

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    with sqlite3.connect(DATABASE, uri=True) as conn:
        conn.execute('DELETE FROM notes WHERE id=?', (note_id,))
        conn.commit()
    
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'  
    response.headers['Content-Security-Policy'] = "default-src 'self';"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains' 
    response.headers['Referrer-Policy'] = 'no-referrer'  
    response.headers['X-Content-Type-Options'] = 'nosniff'  
    return response


if __name__ == '__main__':
    init_db()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
