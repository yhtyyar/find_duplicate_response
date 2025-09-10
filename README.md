# HTTP Request Log Duplicate Finder

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

This application finds duplicate entries in CSV files of HTTP request logs based on URL, HTTP method, response code, and status.

## 🇷🇺 Русская версия ниже

## Features

- Read CSV files with HTTP request logs
- Identify duplicate records based on URL, HTTP method, response code, and status
- Color-coded visualization for better readability (CLI)
- REST API for programmatic access (using FastAPI)
- Enhanced visual grouping of duplicates
- Special highlighting for error codes (4xx and 5xx)
- Improved color scheme for better readability
- **Query parameter consideration when comparing URLs** - requests with different parameters are considered different
- Interactive API documentation with Swagger UI

## Project Structure

- `model.py` - Data processing logic
- `view.py` - Display functions
- `controller.py` - Main application logic (CLI)
- `api.py` - REST API implementation (using FastAPI)
- `res/` - Sample data files

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- python-multipart

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Run with default file
python controller.py

# Run with specific file
python controller.py path/to/your/file.csv
```

### REST API

```bash
# Start API server
python api.py

# API will be available at http://localhost:5000

# Health check
curl http://localhost:5000/health

# Find duplicates
curl -X POST -F "file=@path/to/your/file.csv" http://localhost:5000/find-duplicates

# Interactive API documentation
# Open http://localhost:5000/docs in your browser
```

## How It Works

1. The application reads CSV files with HTTP request logs
2. Identifies duplicate records based on the combination:
   - URL (including query parameters)
   - HTTP Method (GET, POST, etc.)
   - Response Code (200, 404, etc.)
   - Status (COMPLETE, ERROR, etc.)

### URL Processing Features

When comparing URLs, the application considers query parameters:
- `https://example.com/api?user=1&event=play` and `https://example.com/api?user=1&event=play` - duplicates
- `https://example.com/api?user=1&event=play` and `https://example.com/api?user=2&event=play` - different requests
- `https://example.com/api?user=1&event=play` and `https://example.com/api?event=play&user=1` - different requests (different parameter order)

## Output

The application displays:
- Total number of processed rows
- Number of duplicates found
- Detailed list of duplicate records with visual grouping

## API Endpoints

- `GET /health` - Service health check
- `POST /find-duplicates` - Find duplicates in uploaded CSV file
- `GET /` - Simple HTML interface for testing
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

The POST `/find-duplicates` endpoint expects a multipart/form-data request with a 'file' field containing the CSV file.

## Color Coding

- **Green**: Successful responses (2xx)
- **Yellow**: Redirect responses (3xx)
- **Red**: Client errors (4xx)
- **Purple**: Server errors (5xx)
- **Blue/Other colors**: Different duplicate groups for easy visual identification

CLI version uses a light color scheme for better readability.

## Deployment

See [deployment.md](deployment.md) for detailed deployment instructions.

---

# Поиск дубликатов в логах HTTP запросов

Это приложение находит дублирующиеся записи в CSV файлах логов HTTP запросов на основе URL, метода HTTP, кода ответа и статуса.

## Структура проекта

- `model.py` - Логика обработки данных
- `view.py` - Функции отображения
- `controller.py` - Основная логика приложения (CLI)
- `api.py` - Реализация REST API (с использованием FastAPI)
- `res/` - Примеры файлов данных

## Возможности

- Чтение CSV файлов с логами HTTP запросов
- Определение дублирующихся записей на основе URL, метода, кода ответа и статуса
- Цветная индикация для лучшей визуализации (CLI)
- REST API для программного доступа (с использованием FastAPI)
- Улучшенная визуальная группировка дубликатов
- Специальная подсветка для кодов ошибок (4xx и 5xx)
- Улучшенная цветовая схема для лучшей читаемости
- **Учет query-параметров при сравнении URL** - запросы с разными параметрами считаются разными
- Интерактивная документация API с Swagger UI

## Использование

### Командная строка

```bash
# Запуск с файлом по умолчанию
python controller.py

# Запуск с указанием конкретного файла
python controller.py path/to/your/file.csv
```

### REST API

```bash
# Запуск сервера API
python api.py

# API будет доступен по адресу http://localhost:5000

# Проверка состояния сервиса
curl http://localhost:5000/health

# Поиск дубликатов
curl -X POST -F "file=@path/to/your/file.csv" http://localhost:5000/find-duplicates

# Интерактивная документация API
# Откройте http://localhost:5000/docs в вашем браузере
```

## Требования

- Python 3.x
- FastAPI
- Uvicorn
- python-multipart

Установка зависимостей:
```bash
pip install -r requirements.txt
```

## Как это работает

1. Приложение читает CSV файл с логами HTTP запросов
2. Определяет дублирующиеся записи на основе комбинации:
   - URL (с учетом query-параметров)
   - Метод HTTP (GET, POST, и т.д.)
   - Код ответа (200, 404, и т.д.)
   - Статус (COMPLETE, ERROR, и т.д.)

### Особенности обработки URL

При сравнении URL приложение учитывает query-параметры:
- `https://example.com/api?user=1&event=play` и `https://example.com/api?user=1&event=play` - дубликаты
- `https://example.com/api?user=1&event=play` и `https://example.com/api?user=2&event=play` - разные запросы
- `https://example.com/api?user=1&event=play` и `https://example.com/api?event=play&user=1` - разные запросы (разный порядок параметров)

## Вывод

Приложение отображает:
- Общее количество обработанных строк
- Количество найденных дубликатов
- Подробный список дублирующихся записей с визуальной группировкой

## Конечные точки API

- `GET /health` - Проверка состояния сервиса
- `POST /find-duplicates` - Поиск дубликатов в загруженном CSV файле
- `GET /` - Простой HTML интерфейс для тестирования
- `GET /docs` - Интерактивная документация API (Swagger UI)
- `GET /redoc` - Альтернативная документация API (ReDoc)

Конечная точка POST `/find-duplicates` ожидает multipart/form-data запрос с полем 'file', содержащим CSV файл.

## Цветовая индикация

- **Зеленый**: Успешные ответы (2xx)
- **Желтый**: Перенаправления (3xx)
- **Красный**: Клиентские ошибки (4xx)
- **Фиолетовый**: Серверные ошибки (5xx)
- **Синий/Другие цвета**: Разные группы дубликатов для удобной визуальной идентификации

CLI версия использует светлую цветовую схему для лучшей читаемости.

## Развертывание

См. [deployment.md](deployment.md) для подробных инструкций по развертыванию.