Загрузка CSV-файла (POST /api/upload):
Bash

curl -X POST -F "file=@data.csv" http://localhost:5000/api/upload

Возвращает: 201 Created с file_id и метаданными. Если файл — картинка .png, вернет 415 Unsupported Media Type.

Получение Pandas-статистики (GET /api/data/stats):
Bash

curl -X GET http://localhost:5000/api/data/stats

Возвращает: 200 OK с рассчитанными матрицами корреляции, средними и медианами по колонкам.

Очистка данных (GET /api/data/clean):
Bash

curl -X GET http://localhost:5000/api/data/clean

Возвращает: 200 OK со сводкой: сколько дубликатов было удалено и сколько пустых полей заполнено.

Заполнить все данные в файле .env:
# Формат: postgresql://пользователь:пароль@хост:порт/имя_базы
DATABASE_URL;
FLASK_APP;
FLASK_DEBUG;