from models import db, UploadedFile, DataAnalysis

class DataRepository:
    @staticmethod
    def save_file_metadata(filename: str, file_type: str) -> UploadedFile:
        new_file = UploadedFile(filename=filename, file_type=file_type)
        db.session.add(new_file)
        db.session.commit()
        return new_file

    @staticmethod
    def get_last_file() -> UploadedFile:
        return UploadedFile.query.order_by(UploadedFile.id.desc()).first()

    @staticmethod
    def save_analysis(file_id: int, analysis_type: str, result_data: dict) -> DataAnalysis:
        analysis = DataAnalysis(file_id=file_id, analysis_type=analysis_type, result_json=result_data)
        db.session.add(analysis)
        db.session.commit()
        return analysis