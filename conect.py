from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_segura'  # Necesaria para usar sesiones

# Configuración de conexión a la base de datos
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'mylogin')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_PORT = os.getenv('DB_PORT', '5432')

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print("WARNING - NO CONNECT TO DATA BASE:", e)
        return None

def exist_user(username):
    conn = connect_to_db()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT * FROM persona WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    print(f"exist_user result for '{username}': {user}")
    return user

def authenticate_user(username, password):
    user = exist_user(username)
    if user and password == user[2]:  # Comparación simple de contraseña
        return user
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            session['username'] = username  # Guardamos en sesión
            return redirect(url_for('menu'))  # Redirige a la página de menú
        else:
            return render_template('index.html', error='Usuario o contraseña inválidos')
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def vista_registroLogin():
    if request.method == 'POST':
        print("POST a /registro recibido")
        conector = connect_to_db()
        if conector:
            try:
                username = request.form.get('username')
                password = request.form.get('password')
                print(f"Intento registro: {username}, {password}")
                userTMP = exist_user(username)
                if userTMP is None:
                    cursor = conector.cursor()
                    cursor.execute("INSERT INTO persona (username, password) VALUES (%s, %s)", (username, password))
                    conector.commit()
                    cursor.close()
                    print("Usuario registrado, redirigiendo a login")
                    return redirect(url_for('login'))
                else:
                    print("Usuario ya existe")
                    return render_template('registro.html', errormio='Usuario existente')
            except Exception as e:
                print("Error insertando usuario:", e)
                return render_template('registro.html', errormio='Error en el servidor')
        else:
            print("No se pudo conectar a la base de datos")
            return render_template('registro.html', errormio='Error en el servidor')
    print("GET a /registro")
    return render_template('registro.html')


@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))

    products = [
        {'id': 1, 'name': 'Producto A', 'price': 100, 'description': 'Descripción del producto A'},
        {'id': 2, 'name': 'Producto B', 'price': 150, 'description': 'Descripción del producto B'},
        {'id': 3, 'name': 'Producto C', 'price': 200, 'description': 'Descripción del producto C'},
    ]

    return render_template('menu.html', username=session['username'], products=products)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

