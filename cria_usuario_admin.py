import sqlite3

conn = sqlite3.connect('marmita.db')
cursor = conn.cursor()

# Altere nome, login e senha conforme preferir
nome = "Administrador"
login = "admin"
senha = "123456"

cursor.execute("""
    INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)
""", (nome, login, senha))
conn.commit()
conn.close()

print("Usuário criado!")
