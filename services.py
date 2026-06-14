import os
import pandas as pd
from werkzeug.utils import secure_filename
from repositories import DataRepository

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

class DataService:
    @staticmethod
    def allowed_file(filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @classmethod
    def process_upload(cls, file, upload_folder: str):
        if not file or file.filename == '':
            return {"error": "Файл не выбран"}, 400
            
        if not cls.allowed_file(file.filename):
            return {"error": "Неподдерживаемый тип файла. Разрешены только CSV и Excel"}, 415

        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        file_type = 'excel' if file_ext in ['xlsx', 'xls'] else 'csv'
        
        # Создаем папку, если её нет
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Валидация: проверяем, может ли Pandas прочитать этот файл
        try:
            if file_type == 'csv':
                pd.read_csv(filepath, nrows=5)
            else:
                pd.read_excel(filepath, nrows=5)
        except Exception:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {"error": "Файл поврежден или имеет неверную внутреннюю структуру"}, 400

        # Сохраняем метаданные в PostgreSQL
        db_file = DataRepository.save_file_metadata(filename, file_type)
        
        return {
            "message": "Файл успешно загружен и зарегистрирован",
            "file_id": db_file.id,
            "filename": db_file.filename
        }, 201

    @staticmethod
    def load_dataframe(filepath: str, file_type: str) -> pd.DataFrame:
        if file_type == 'excel':
            return pd.read_excel(filepath)
        return pd.read_csv(filepath)

    @classmethod
    def calculate_stats(cls, upload_folder: str):
        last_file = DataRepository.get_last_file()
        if not last_file:
            return {"error": "Нет загруженных файлов для анализа"}, 404

        filepath = os.path.join(upload_folder, last_file.filename)
        if not os.path.exists(filepath):
            return {"error": f"Файл {last_file.filename} не найден на сервере"}, 404

        df = cls.load_dataframe(filepath, last_file.file_type)
        
        # Отбираем только числовые колонки для анализа
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return {"error": "В файле отсутствуют числовые данные для анализа"}, 400

        # Расчет метрик с помощью Pandas
        stats = {
            "mean": numeric_df.mean().to_dict(),
            "median": numeric_df.median().to_dict(),
            "correlation": numeric_df.corr().to_dict()
        }

        # Сохраняем результаты в PostgreSQL
        DataRepository.save_analysis(last_file.id, 'stats', stats)
        
        return {
            "file_id": last_file.id,
            "filename": last_file.filename,
            "statistics": stats
        }, 200

    @classmethod
    def clean_data(cls, upload_folder: str):
        last_file = DataRepository.get_last_file()
        if not last_file:
            return {"error": "Нет загруженных файлов для очистки"}, 404

        filepath = os.path.join(upload_folder, last_file.filename)
        if not os.path.exists(filepath):
            return {"error": "Файл не найден на сервере"}, 404

        df = cls.load_dataframe(filepath, last_file.file_type)

        # Фиксируем исходное состояние
        initial_rows = len(df)
        initial_nulls = int(df.isnull().sum().sum())

        # Очистка Pandas: удаление дубликатов и заполнение/удаление пропусков
        df_cleaned = df.drop_duplicates()
        
        # Заполняем пропуски в числовых колонках средним, в текстовых - строкой 'Unknown'
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype in ['int64', 'float64']:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
            else:
                df_cleaned[col] = df_cleaned[col].fillna('Unknown')

        final_rows = len(df_cleaned)
        removed_duplicates = initial_rows - final_rows

        # Перезаписываем очищенный файл
        if last_file.file_type == 'excel':
            df_cleaned.to_excel(filepath, index=False)
        else:
            df_cleaned.to_csv(filepath, index=False)

        result_summary = {
            "initial_rows": initial_rows,
            "removed_duplicates": removed_duplicates,
            "fixed_null_values": initial_nulls,
            "final_rows": final_rows
        }

        # Сохраняем логи очистки в БД
        DataRepository.save_analysis(last_file.id, 'clean', result_summary)

        return {
            "file_id": last_file.id,
            "filename": last_file.filename,
            "summary": result_summary
        }, 200