import os
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa as crs
from cryptography.x509.oid import NameOID
from datetime import datetime, timezone, timedelta

# Crear directorio para claves
os.makedirs("claves", exist_ok=True)

# Generar par de claves RSA de 2048 bits
private_key = crs.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Guardar clave privada
with open("claves/private.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Crear certificado autofirmado
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FirmaDigital Inc"),
    x509.NameAttribute(NameOID.COMMON_NAME, "firmadigital.com"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    public_key
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.now(timezone.utc)
).not_valid_after(
    datetime.now(timezone.utc) + timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName("localhost")]),
    critical=False,
).sign(private_key, hashes.SHA256())

# Guardar certificado
with open("claves/certificado.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("✅ Claves y certificado generados correctamente")