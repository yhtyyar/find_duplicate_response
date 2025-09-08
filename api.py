"""
REST API для приложения поиска дубликатов.
"""

import io
import logging
from flask import Flask, request, jsonify, render_template_string
import model

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния сервиса."""
    return jsonify({"status": "healthy"}), 200


@app.route('/find-duplicates', methods=['POST'])
def find_duplicates():
    """
    Поиск дубликатов в загруженном CSV файле.
    
    Ожидаемый вход:
    - multipart/form-data с полем 'file', содержащим CSV файл
    
    Возвращает:
    - JSON ответ с результатами обработки
    """
    # Проверка наличия файла
    if 'file' not in request.files:
        return jsonify({"error": "Файл не предоставлен"}), 400
    
    file = request.files['file']
    
    # Проверка имени файла
    if file.filename == '':
        return jsonify({"error": "Пустое имя файла"}), 400
    
    try:
        # Чтение содержимого файла
        content = file.read().decode('utf-8')
        
        # Использование StringIO для работы со строкой как с файлом
        csv_file = io.StringIO(content)
        
        # Обработка CSV данных
        rows = model.read_csv_from_string(csv_file)
        
        # Проверка на пустые данные
        if not rows:
            return jsonify({"error": "Файл пуст"}), 400

        total = len(rows)
        duplicates_info = model.find_duplicates(rows)
        stats = model.get_stats(rows)
        duplicates_count = sum(v - 1 for v in duplicates_info.values())

        # Группировка дублирующихся строк
        duplicates_full = {}
        for row in rows:
            # Используем ту же функцию создания ключа, что и в модели, для правильной группировки
            key = model._create_comparison_key(row)
            if key in duplicates_info:
                if key not in duplicates_full:
                    duplicates_full[key] = []
                duplicates_full[key].append(row)

        # Подготовка ответа с информацией о группах дубликатов
        result = {
            "total_rows": total,
            "duplicates_count": duplicates_count,
            "duplicates": duplicates_full,
            "statistics": stats,
            "duplicate_groups": len(duplicates_full)  # Количество различных групп дубликатов
        }
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Ошибка данных: {str(e)}")
        return jsonify({"error": f"Ошибка данных: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return jsonify({"error": f"Неожиданная ошибка: {str(e)}"}), 500


@app.route('/', methods=['GET'])
def index():
    """Простой HTML интерфейс для тестирования API."""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Поиск дубликатов в логах</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #f5f5f5;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        input[type="file"] { 
            margin-bottom: 10px; 
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button { 
            background-color: #4CAF50; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            cursor: pointer; 
            border-radius: 4px;
            font-size: 16px;
        }
        button:hover { 
            background-color: #45a049; 
        }
        #result { 
            margin-top: 20px; 
            padding: 15px; 
            border-radius: 4px;
            background-color: #f9f9f9;
            display: none;
            overflow-x: auto;
        }
        .error { 
            background-color: #ffebee; 
            color: #c62828;
            border-left: 4px solid #f44336;
        }
        .success { 
            background-color: #e8f5e9; 
            color: #2e7d32;
            border-left: 4px solid #4CAF50;
        }
        .warning { 
            background-color: #fff3e0; 
            color: #ef6c00;
            border-left: 4px solid #ff9800;
        }
        .duplicate-group {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 4px;
        }
        .duplicate-group-0 { background-color: #e3f2fd; } /* Светло-синий */
        .duplicate-group-1 { background-color: #e8f5e8; } /* Светло-зеленый */
        .duplicate-group-2 { background-color: #fff8e1; } /* Светло-желтый */
        .duplicate-group-3 { background-color: #f3e5f5; } /* Светло-фиолетовый */
        .duplicate-group-4 { background-color: #e0f7fa; } /* Светло-голубой */
        .duplicate-group-5 { background-color: #ffebee; } /* Светло-красный */
        .duplicate-group-6 { background-color: #fafafa; } /* Светло-серый */
        .duplicate-group-7 { background-color: #fff3e0; } /* Светло-оранжевый */
        
        .error-4xx { background-color: #ffebee; border-left: 4px solid #f44336; }
        .error-5xx { background-color: #f3e5f5; border-left: 4px solid #9c27b0; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f5f5f5;
        }
        .error-code-4xx { color: #f44336; font-weight: bold; }
        .error-code-5xx { color: #9c27b0; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Поиск дубликатов в логах HTTP запросов</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label for="csvFile">Загрузить CSV файл:</label><br>
                <input type="file" id="csvFile" name="file" accept=".csv" required>
            </div>
            <button type="submit">Найти дубликаты</button>
        </form>
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('csvFile');
            const resultDiv = document.getElementById('result');
            
            if (fileInput.files.length === 0) {
                showResult('Пожалуйста, выберите файл', 'error');
                return;
            }
            
            formData.append('file', fileInput.files[0]);
            
            // Показ сообщения о загрузке
            showResult('Обработка... Пожалуйста, подождите.', 'warning');
            
            fetch('/find-duplicates', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showResult('Ошибка: ' + data.error, 'error');
                } else {
                    showResult(formatResult(data), 'success');
                }
            })
            .catch(error => {
                showResult('Ошибка сети: ' + error, 'error');
            });
        });
        
        function showResult(message, type) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<pre>' + message + '</pre>';
            resultDiv.className = type;
            resultDiv.style.display = 'block';
        }
        
        function formatResult(data) {
            let result = '=== Статистика обработки ===\\n';
            result += 'Обработано строк: ' + data.total_rows + '\\n';
            result += 'Найдено дубликатов: ' + data.duplicates_count + '\\n';
            result += 'Групп дубликатов: ' + data.duplicate_groups + '\\n\\n';
            
            if (data.duplicates_count > 0) {
                result += '=== Дублирующиеся строки ===\\n';
                result += 'Код ответа    | Время начала              | Метод   | URL\\n';
                result += '-'.repeat(200) + '\\n';
                
                let groupIndex = 0;
                for (const [key, rows] of Object.entries(data.duplicates)) {
                    for (const row of rows) {
                        const code = row['Response Code'] || '';
                        let codeDisplay = code;
                        
                        // Добавление специального форматирования для кодов ошибок
                        if (code.startsWith('4')) {
                            codeDisplay = code + ' [Ошибка 4xx]';
                        } else if (code.startsWith('5')) {
                            codeDisplay = code + ' [Ошибка 5xx]';
                        }
                        
                        result += 
                            codeDisplay.padEnd(15) + ' | ' +
                            (row['Request Start Time'] || '').substring(0, 25).padEnd(25) + ' | ' +
                            (row['Method'] || '').padEnd(7) + ' | ' +
                            (row['URL'] || '').substring(0, 150) + '\\n';
                    }
                    result += '\\n'; // Разделение групп пустой строкой
                    groupIndex = (groupIndex + 1) % 8;
                }
                result += '\\n';
            }
            
            return result;
        }
    </script>
</body>
</html>
""")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)