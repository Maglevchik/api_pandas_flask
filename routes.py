from flask import Blueprint, request, jsonify, current_app
from services import DataService

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "В запросе отсутствует поле 'file'"}), 400
        
    file = request.files['file']
    result, status_code = DataService.process_upload(file, current_app.config['UPLOAD_FOLDER'])
    return jsonify(result), status_code

@api_bp.route('/data/stats', methods=['GET'])
def get_stats():
    result, status_code = DataService.calculate_stats(current_app.config['UPLOAD_FOLDER'])
    return jsonify(result), status_code

@api_bp.route('/data/clean', methods=['GET'])
def clean_data():
    result, status_code = DataService.clean_data(current_app.config['UPLOAD_FOLDER'])
    return jsonify(result), status_code

# Глобальный перехватчик ошибок для красивого REST API
@api_bp.app_errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "Файл слишком большой. Максимальный размер - 16МБ"}), 413