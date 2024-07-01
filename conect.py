from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import bcrypt
import os

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'mylogin')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_PORT = os.getenv('DB_PORT', '5432')

def connect_to_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
    except psycopg2.Error as e:
        print("WARNING - NO CONNECT TO DATA BASE:", e)
    return conn

def exist_user(username):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM persona WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user is not None:
        return user
    else:
        return None

def authenticate_user(username, password):
    user = exist_user(username)
    if user:
        if check_password(password, user[1]):
            return user
    return None

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            return redirect(url_for('success'))
        else:
            return render_template('index.html', error='Invalid username or password')
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def vista_registroLogin():
    if request.method == 'POST':
        conector = connect_to_db()
        if conector:
            username = request.form['username']
            password = request.form['password']
            userTMP = exist_user(username)
            if userTMP is None:
                cursor = conector.cursor()
                cursor.execute("INSERT INTO persona (username, password) VALUES (%s, %s)", (username, hash_password(password).decode('utf-8')))
                conector.commit()
                cursor.close()
                return redirect(url_for('login'))
            else:
                return render_template('registro.html', errormio='Usuario Existente')
    return render_template('registro.html')

@app.route('/success')
def success():
    return 'Login successful!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
