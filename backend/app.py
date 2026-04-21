from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Habilitar CORS para que el frontend en otro puerto pueda hacer fetch
CORS(app)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener credenciales de la BD desde variables de entorno
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'teamboard_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

def get_db_connection():
    """Crea una conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Error conectando a BD: {e}")
        return None

# ============ ENDPOINTS OBLIGATORIOS ============

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check: Docker usa este endpoint en el HEALTHCHECK
    Devuelve 200 si el servicio está activo
    """
    return jsonify({
        'status': 'healthy',
        'service': 'backend'
    }), 200

@app.route('/api/team', methods=['GET'])
def get_team():
    """
    Devuelve la lista de integrantes del equipo desde la BD
    El frontend hace fetch() a este endpoint y construye la tabla
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, nombre, apellido, legajo, feature, servicio, estado FROM members ORDER BY id')
        members = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convertir a lista de dicts (RealDictCursor ya lo hace)
        return jsonify(members), 200
    except Exception as e:
        logger.error(f"Error en GET /api/team: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/info', methods=['GET'])
def info():
    """
    Metadata del servicio
    """
    return jsonify({
        'service': 'backend',
        'version': '1.0.0',
        'description': 'TeamBoard API REST',
        'endpoints': {
            '/api/health': 'Health check del servicio',
            '/api/team': 'Lista de integrantes del equipo',
            '/api/info': 'Metadata del servicio'
        }
    }), 200

# ============ MANEJO DE ERRORES ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# ============ MAIN ============

if __name__ == '__main__':
    # En desarrollo
    # app.run(host='0.0.0.0', port=5000, debug=True)
    
    # En producción (dentro del contenedor)
    # Se ejecuta con gunicorn (ver Dockerfile)
    app.run(host='0.0.0.0', port=5000, debug=False)