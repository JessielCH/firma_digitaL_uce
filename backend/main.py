from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography import x509
from datetime import datetime, timezone
import db
import bcrypt
import sqlite3

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def verificar_certificado(cert):
    ahora = datetime.now(timezone.utc)
    if ahora < cert.not_valid_before.replace(tzinfo=timezone.utc):
        return False, "Certificado aún no válido"
    if ahora > cert.not_valid_after.replace(tzinfo=timezone.utc):
        return False, "Certificado expirado"
    return True, "Certificado válido"


@app.post("/registrar")
async def registrar_usuario(username: str = Form(...), password: str = Form(...)):
    success, message = db.create_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "success", "message": message}


@app.post("/firmar")
async def firmar_documento(
        file: UploadFile = File(...),
        username: str = Form(...),
        password: str = Form(...)
):
    # Obtener usuario
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Verificar contraseña
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Cargar clave privada y certificado del usuario
    private_key = load_pem_private_key(user['private_key'], password=None)
    certificado = x509.load_pem_x509_certificate(user['certificate'])

    contenido = await file.read()

    # Crear firma digital
    firma = private_key.sign(
        contenido,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Verificar certificado
    valido, mensaje_cert = verificar_certificado(certificado)

    return {
        "firma": firma.hex(),
        "certificado_valido": valido,
        "mensaje_certificado": mensaje_cert,
        "firmante": username,
        "valido_desde": certificado.not_valid_before.isoformat(),
        "valido_hasta": certificado.not_valid_after.isoformat()
    }


@app.post("/firmar-lotes")
async def firmar_lotes(
        files: list[UploadFile] = File(...),
        username: str = Form(...),
        password: str = Form(...)
):
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    private_key = load_pem_private_key(user['private_key'], password=None)
    certificado = x509.load_pem_x509_certificate(user['certificate'])
    valido, mensaje_cert = verificar_certificado(certificado)

    resultados = []
    for file in files:
        contenido = await file.read()
        firma = private_key.sign(
            contenido,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        resultados.append({
            "nombre": file.filename,
            "firma": firma.hex(),
            "tamano": len(contenido),
            "certificado_valido": valido,
            "mensaje_certificado": mensaje_cert
        })

    return {"resultados": resultados}


@app.post("/verificar")
async def verificar_firma(
        file: UploadFile = File(...),
        firma: str = Form(...),
        username: str = Form(...)
):
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    certificado = x509.load_pem_x509_certificate(user['certificate'])
    contenido = await file.read()
    firma_bytes = bytes.fromhex(firma)

    try:
        # Verificar firma usando el certificado del usuario
        certificado.public_key().verify(
            firma_bytes,
            contenido,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Verificar certificado
        valido, mensaje_cert = verificar_certificado(certificado)

        return {
            "valido": True,
            "firmante": username,
            "certificado_valido": valido,
            "mensaje_certificado": mensaje_cert
        }
    except Exception as e:
        print(f"Error en verificación: {e}")
        return {"valido": False}


@app.get("/info-certificado/{username}")
def obtener_info_certificado(username: str):
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    certificado = x509.load_pem_x509_certificate(user['certificate'])
    return {
        "emisor": certificado.issuer.rfc4514_string(),
        "sujeto": certificado.subject.rfc4514_string(),
        "valido_desde": certificado.not_valid_before.isoformat(),
        "valido_hasta": certificado.not_valid_after.isoformat(),
        "serial": str(certificado.serial_number),
        "algoritmo": certificado.signature_algorithm_oid._name
    }


@app.get("/certificado/{username}")
async def obtener_certificado_pem(username: str):
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(content=user['certificate'], media_type="application/x-pem-file")


# Agregar este nuevo endpoint para login
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Verificar contraseña
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {"status": "success", "message": "Login exitoso"}