import sqlite3
conn = sqlite3.connect("clinica.sqbpro")  # o simplemente "clinica.db" si la moviste
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
