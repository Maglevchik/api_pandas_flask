from flask import Flask
from config import Config
from models import db
from routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация БД
    db.init_app(app)

    # Регистрация роутов
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        # Создаем таблицы в PostgreSQL, если их еще нет
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)