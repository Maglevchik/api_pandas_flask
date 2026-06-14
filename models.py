from flask_sqlalchemy import SQLAlchemy # type: ignore
import datetime

db = SQLAlchemy()

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # csv или excel
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Связь с результатами анализа
    analyses = db.relationship('DataAnalysis', backref='file', lazy=True, cascade="all, delete-orphan")

class DataAnalysis(db.Model):
    __tablename__ = 'data_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # stats или clean
    result_json = db.Column(db.JSON, nullable=False)          # Результаты работы Pandas
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)