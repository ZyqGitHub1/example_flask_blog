import os
import config
import sqlite3
from hashlib import md5
from werkzeug import check_password_hash, generate_password_hash
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

#app.config.from_object("config")

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir,"user.db")

app.config.update(dict(
    DATABASE=db_path,
    DEBUG=True,
    SECRET_KEY='development key'
))

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    if not session.get('logged_in'):
        abort(401)
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        username1 = request.form['username']
        password1 = request.form['password']
        cur = db.execute('select password from user where username = ?',[username1])
        password = cur.fetchall()[0][0]
        if username1 is None:
            error = 'Invalid username'
        elif not check_password_hash(password,password1):
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        db = get_db()
        new_username = request.form['username']
        new_password1 = request.form['password1']
        new_password2 = request.form['password2']
        if new_password1 != new_password2:
            error = 'The two passwords do not match'
        else:
            md5_password = generate_password_hash(new_password1)
            db.execute('insert into user (username, password) values (?, ?)',[new_username,md5_password])
            db.commit()
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(debug = True)