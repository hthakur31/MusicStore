from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            price REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            song_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM songs")
    songs = c.fetchall()
    conn.close()
    return render_template('index.html', songs=songs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "Username already exists!"
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        price = request.form['price']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO songs (title, artist, price) VALUES (?, ?, ?)", (title, artist, price))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_song.html')

@app.route('/purchase/<int:song_id>')
def purchase(song_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO purchases (user_id, song_id) VALUES (?, ?)", (session['user_id'], song_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/history')
def purchase_history():
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT songs.title, songs.artist, songs.price 
        FROM purchases 
        JOIN songs ON purchases.song_id = songs.id 
        WHERE purchases.user_id = ?
    ''', (session['user_id'],))
    purchases = c.fetchall()
    conn.close()
    return render_template('purchase_history.html', purchases=purchases)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
