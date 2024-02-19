from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Replace these with your PostgreSQL database credentials
DB_HOST = 'localhost'
DB_NAME = 'mylogin'
DB_USER = 'postgres'
DB_PASSWORD = 'root'
DB_PORT ='5432'

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
        print("wARNING- NO CONNECT TO DATA BASE:", e)
    return conn

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
@app.route('/registro',methods=['GET','POST'])
def vista_registroLogin():
    if request.method == 'POST':
        conector = connect_to_db()
        if conector != None:
            username = request.form['username']
            password = request.form['password']
            cursor = conector.cursor()
            cursor.execute("INSERT INTO persona (username, password) VALUES (%s, %s)", (username,password))
            conector.commit()
            cursor.close()
        return redirect(url_for('/'))
    return render_template('registro.html')


def authenticate_user(username, password):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM persona WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None


@app.route('/success')
def success():
    return 'Login successful!'

if __name__ == '__main__':
    app.run(debug=True)