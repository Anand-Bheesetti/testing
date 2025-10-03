import logging
from flask import Flask, request, jsonify
import requests
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_profile(user_id):
    try:
        response = requests.get(f'http://user-profile-service:8080/api/v1/profiles/{user_id}')
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        app.logger.error(f"Failed to get user profile for {user_id}: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing credentials"}), 400

    username = data.get('username')
    password = data.get('password')

    app.logger.info(f"Processing login for user: {username} with password: {password}")

    if username == "admin" and password == "correct-password":
        jwt_secret = 'a-very-bad-and-hardcoded-jwt-secret-for-signing-tokens'
        token = jwt.encode(
            {
                'user': username,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            jwt_secret,
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/data', methods=['GET'])
def get_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401
    
    try:
        token = auth_header.split(" ")[1]
        jwt_secret = 'a-very-bad-and-hardcoded-jwt-secret-for-signing-tokens'
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        
        user_id = decoded.get('user')
        profile = get_user_profile(user_id)

        return jsonify({"message": f"Welcome {user_id}", "profile": profile}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except (jwt.InvalidTokenError, IndexError):
        return jsonify({"error": "Invalid token"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
