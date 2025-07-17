import sqlite3
import bcrypt
from cryptography.hazmat.primitives.asymmetric import rsa as crs
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from datetime import datetime, timezone, timedelta


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     username
                     TEXT
                     UNIQUE,
                     password
                     TEXT
                     NOT
                     NULL,
                     private_key
                     BLOB
                     NOT
                     NULL,
                     certificate
                     BLOB
                     NOT
                     NULL
                 )''')
    conn.commit()
    conn.close()


def create_user(username: str, password: str):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Verificar si el usuario ya existe
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False, "El usuario ya existe"

    # Generar salt y hash de la contraseña
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Generar par de claves RSA
    private_key = crs.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Crear certificado autofirmado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, username),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(timezone.utc)
    ).not_valid_after(
        datetime.now(timezone.utc) + timedelta(days=365)
    ).sign(private_key, hashes.SHA256())

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)

    # Insertar en la base de datos
    c.execute("INSERT INTO users (username, password, private_key, certificate) VALUES (?, ?, ?, ?)",
              (username, hashed_password, private_pem, cert_pem))
    conn.commit()
    conn.close()
    return True, "Usuario creado"


def get_user(username: str):
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user


# Inicializar la base de datos al importar
init_db()