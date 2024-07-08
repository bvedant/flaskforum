from flask import Flask, request, g, redirect, url_for, render_template, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['DATABASE'] = 'app/forum.db'
app.config['SECRET_KEY'] = 'your_secret_key'

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, title, created_at FROM topics ORDER BY id DESC')
    topics = cur.fetchall()
    return render_template('index.html', topics=topics)

@app.route('/topic/<int:topic_id>')
def topic(topic_id):
    db = get_db()
    cur = db.execute('SELECT id, title, content, created_at FROM topics WHERE id = ?', (topic_id,))
    topic = cur.fetchone()
    cur = db.execute('SELECT content, created_at FROM comments WHERE topic_id = ?', (topic_id,))
    comments = cur.fetchall()
    return render_template('topic.html', topic=topic, comments=comments)

@app.route('/new', methods=['GET', 'POST'])
def new_topic():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        db.execute('INSERT INTO topics (title, content) VALUES (?, ?)', (title, content))
        db.commit()
        flash('New topic was successfully posted')
        return redirect(url_for('index'))
    return render_template('new_topic.html')

@app.route('/topic/<int:topic_id>/comment', methods=['POST'])
def comment(topic_id):
    content = request.form['content']
    db = get_db()
    db.execute('INSERT INTO comments (topic_id, content) VALUES (?, ?)', (topic_id, content))
    db.commit()
    flash('Your comment was successfully posted')
    return redirect(url_for('topic', topic_id=topic_id))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
