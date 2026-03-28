import os
import datetime
import requests
import logging
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, exceptions
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE FIREBASE ---
# 1. Descarga tu serviceAccountKey.json desde la consola de Firebase
# 2. Obtén tu Web API Key desde Project Settings > General
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

FIREBASE_WEB_API_KEY = "AIzaSyC5NdRNHCBsa-yLN__-MgJbOM-zhwKtUQ4"
AUTH_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

# --- HELPER PARA LOGGING (Simulado) ---
logging.basicConfig(filename="events.log", level=logging.INFO)

def log_event(event_type, uid, email, success, details=""):
    timestamp = datetime.datetime.utcnow().isoformat()
    message = f"[{timestamp}] {event_type} - UID: {uid} - Email: {email} - Success: {success} - {details}"
    logging.info(message)


# --- RUTAS ---

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """US2: Registro de nuevo usuario"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('Name')
    role = data.get('rol', 'user')

    # Validación básica
    errors = []
    if not email or "@" not in email: errors.append("Invalid email format")
    if not password or len(password) < 8: errors.append("Password must be at least 8 chars")
    
    if errors:
        return jsonify({"error": "VALIDATION_ERROR", "details": errors}), 400

    try:
        # Crear usuario en Firebase Auth
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=name,
            disabled=False
        )

        # Asignar Custom Claims (Rol)
        auth.set_custom_user_claims(user_record.uid, {'role': role})

        log_event("REGISTER", user_record.uid, email, True)
        
        return jsonify({
            "uid": user_record.uid,
            "email": user_record.email,
            "createdAt": datetime.datetime.now().isoformat()
        }), 201

    except auth.EmailAlreadyExistsError:
        return jsonify({"error": "EMAIL_ALREADY_EXISTS", "message": "Email already registered"}), 409
    except exceptions.FirebaseError as e:
        if 'WEAK_PASSWORD' in str(e):
            return jsonify({"error": "WEAK_PASSWORD", "message": "The password is too weak"}), 400
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """US1: Autenticación de usuario"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "VALIDATION_ERROR", "details": ["Email and password required"]}), 400

    # Petición a la API REST de Firebase para validar password y obtener ID Token
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(AUTH_LOGIN_URL, json=payload)
    res_data = response.json()

    if response.status_code != 200:
        error_msg = res_data.get('error', {}).get('message', '')
        
        if error_msg == "INVALID_PASSWORD":
            return jsonify({"error": "INVALID_CREDENTIALS", "message": "Wrong password"}), 401
        if error_msg == "EMAIL_NOT_FOUND":
            return jsonify({"error": "USER_NOT_FOUND", "message": "User not registered"}), 404
        if error_msg == "USER_DISABLED":
            return jsonify({"error": "USER_DISABLED", "message": "Account is disabled"}), 403
        
        return jsonify({"error": "AUTH_ERROR", "message": error_msg}), 400

    log_event("LOGIN", res_data['localId'], email, True)

    return jsonify({
        "idToken": res_data['idToken'],
        "refreshToken": res_data['refreshToken'],
        "expiresIn": int(res_data['expiresIn'])
    }), 200


@app.route('/api/v1/auth/logout', methods=['POST'])
def logout():
    """US3: Revocación de sesiones"""
    auth_header = request.headers.get('Authorization')
    uid = request.json.get('uid') if request.is_json else None

    # Intentar obtener UID del Token si no viene en el body
    if auth_header and auth_header.startswith('Bearer '):
        try:
            id_token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
        except Exception:
            return jsonify({"error": "UNAUTHORIZED", "message": "Invalid or expired token"}), 401

    if not uid:
        return jsonify({"error": "UNAUTHORIZED", "message": "No UID or Token provided"}), 401

    try:
        # Revocar todos los refresh tokens del usuario
        auth.revoke_refresh_tokens(uid)
        log_event("LOGOUT", uid, "N/A", True, "Tokens revoked")
        return jsonify({"message": "Session revoked successfully"}), 200

    except auth.UserNotFoundError:
        return jsonify({"error": "USER_NOT_FOUND", "message": "UID does not exist"}), 404
    except Exception as e:
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)