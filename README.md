# Sistema de Firma Digital con Certificados X.509

Este sistema permite firmar y verificar documentos digitalmente utilizando certificados X.509 con tecnología RSA-2048. A continuación se detalla cómo instalar, configurar y utilizar el sistema desde cero.

## Requisitos Previos

- Python 3.7 o superior  
- Pip (gestor de paquetes de Python)  
- Navegador web moderno (Chrome, Firefox, Edge)

## Instalación y Configuración

### 1. Configurar el entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias (Se encuentran en la carpeta backend)

```bash
pip install -r requirements.txt
```

### 3. Generar claves y certificados

```bash
python generar_claves.py
```

Este comando generará:

- Clave privada: `claves/private.pem`  
- Certificado: `claves/certificado.pem`

### 4. Iniciar el servidor backend

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: [http://localhost:8000](http://localhost:8000)

## Estructura del Proyecto

```
├── claves/                   # Certificados y claves
│   ├── private.pem           # Clave privada de la CA
│   └── certificado.pem       # Certificado de la CA
├── index.html                # Interfaz de usuario
├── style.css                 # Estilos de la interfaz
├── db.py                     # Gestión de base de datos
├── generar_claves.py         # Script para generar claves
├── main.py                   # Servidor backend (API)
├── requirements.txt          # Dependencias de Python
└── users.db                  # Base de datos de usuarios (se crea automáticamente)
```

## Uso del Sistema

### 1. Registro de Usuarios

1. Abrir `index.html` en un navegador web  
2. Seleccionar la pestaña "Registrarse"  
3. Ingresar nombre de usuario y contraseña  
4. Hacer clic en "Registrarse"  
5. Descargar el certificado cuando se muestre el botón  

### 2. Inicio de Sesión

1. Seleccionar la pestaña "Iniciar Sesión"  
2. Ingresar nombre de usuario y contraseña  
3. Hacer clic en "Iniciar Sesión"

### 3. Funcionalidades del Dashboard

#### a) Firmar Documento Individual

- Seleccionar un archivo (PDF, XML, TXT)  
- Ingresar contraseña de firma  
- Hacer clic en "Firmar Documento"  
- Copiar la firma generada

#### b) Firmar Múltiples Documentos

- Seleccionar varios archivos  
- Ingresar contraseña de firma  
- Hacer clic en "Firmar Documentos"  
- Copiar las firmas generadas

#### c) Verificar Firma

- Seleccionar el documento firmado  
- Ingresar el nombre de usuario del firmante  
- Pegar la firma digital (en hexadecimal)  
- Hacer clic en "Verificar Firma"

#### d) Información del Certificado

- Ingresar nombre de usuario  
- Hacer clic en "Mostrar Detalles"  
- Ver información del certificado

### 4. Cerrar Sesión

- Hacer clic en "Cerrar Sesión" en la esquina superior derecha

## API Endpoints

| Endpoint                         | Método | Descripción                         |
|----------------------------------|--------|-------------------------------------|
| `/login`                         | POST   | Autenticar usuario                  |
| `/registrar`                     | POST   | Registrar nuevo usuario            |
| `/firmar`                        | POST   | Firmar documento individual        |
| `/firmar-lotes`                  | POST   | Firmar múltiples documentos        |
| `/verificar`                     | POST   | Verificar firma digital            |
| `/info-certificado/{username}`  | GET    | Obtener información del certificado |
| `/certificado/{username}`       | GET    | Descargar certificado PEM          |

## Solución de Problemas Comunes

### Error al iniciar sesión

**Solución:**

- Verificar que el servidor backend esté en ejecución  
- Comprobar que el nombre de usuario y contraseña sean correctos  
- Verificar que el usuario exista en la base de datos (`users.db`)

### Error al firmar documentos

**Solución:**

- Asegurarse de estar autenticado correctamente  
- Verificar que el archivo sea de un tipo soportado (PDF, XML, TXT)  
- Confirmar que se está usando la contraseña correcta

### Verificación de firma fallida

**Solución:**

- Comprobar que el documento no ha sido modificado después de firmarlo  
- Verificar que se haya copiado toda la firma hexadecimal  
- Confirmar que el nombre de usuario del firmante sea correcto

### Certificado inválido

**Solución:**

- Verificar la fecha de validez del certificado  
- Comprobar que el certificado no haya sido revocado  
- Asegurarse de usar el certificado correcto para el usuario

## Tecnologías Utilizadas

- **Frontend:** HTML5, CSS3, JavaScript  
- **Backend:** Python, FastAPI, Uvicorn  
- **Base de Datos:** SQLite  
- **Criptografía:** RSA-2048, SHA-256, Certificados X.509  
- **Gestión de Paquetes:** Pip

## Equipo de Desarrollo

- Luis Achig  
- Jessiel Chasiguano  
- Alejandro Chiliquinga  
- Alex Tituaña

© Derechos reservados
