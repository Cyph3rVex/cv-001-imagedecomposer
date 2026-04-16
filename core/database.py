import sqlite3
import os
from core.security import get_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "vault.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    
    # Aprovisionar Admin Maestro si la base de datos está vacía
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Credenciales por defecto (Solo Cypher y Oliboli_12)
        default_user = "Oliboli_12"
        default_pass = "VexProtocol2026"
        hashed_pw, salt = get_password_hash(default_pass)
        
        cursor.execute('''
            INSERT INTO users (username, hashed_password, salt)
            VALUES (?, ?, ?)
        ''', (default_user, hashed_pw, salt))
        conn.commit()
        print(f"[!] BÓVEDA INICIALIZADA: Admin '{default_user}' creado.")
        
    conn.close()
