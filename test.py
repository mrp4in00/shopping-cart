import psycopg2

conn = psycopg2.connect(
    host='postgres',
    database='mylogin',
    user='postgres',
    password='root',
    port=5432
)

cur = conn.cursor()

try:
    cur.execute("INSERT INTO persona (username, password) VALUES (%s, %s)", ('testuser', 'testpass'))
    conn.commit()
    print("Usuario insertado correctamente")
except Exception as e:
    print("Error:", e)

cur.execute("SELECT * FROM persona")
rows = cur.fetchall()
print("Usuarios en tabla persona:")
for row in rows:
    print(row)

cur.close()
conn.close()

