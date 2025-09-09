# Руководство по развертыванию приложения на сервере

## Подготовка к развертыванию

### 1. Проверка готовности репозитория

Репозиторий полностью готов к развертыванию на сервере:
- Все исходные файлы находятся в репозитории
- Созданы файлы для развертывания в различных средах (Docker, systemd)
- Обновлены зависимости в requirements.txt
- Создана документация по развертыванию

### 2. Структура проекта

```
duplicate-log-finder/
├── api.py                 # REST API сервер
├── controller.py          # CLI приложение
├── model.py              # Бизнес-логика
├── view.py               # Отображение результатов
├── requirements.txt       # Зависимости
├── setup.py             # Установочный файл
├── .gitignore           # Игнорируемые файлы
├── Dockerfile           # Docker конфигурация
├── docker-compose.yml   # Docker Compose конфигурация
├── wsgi.py             # WSGI точка входа для Gunicorn
├── README.md           # Документация (англ/рус)
├── deployment.md       # Подробное руководство по развертыванию
├── GITHUB_SETUP.md     # Руководство по настройке GitHub
├── res/                # Примеры данных
│   ├── double_requests.csv
│   ├── requests_07_08_06.06.2025.csv
│   └── requests_08_26_06.06.2025.csv
└── tests/              # Тесты
    ├── test_api_url_length.py
    ├── test_csv_reading.py
    ├── test_enhanced_url_comparison.py
    ├── test_model.py
    └── test_url_display.py
```

## Варианты развертывания

### Вариант 1: Развертывание через Docker (рекомендуется)

1. Установите Docker и Docker Compose на сервере
2. Скопируйте репозиторий на сервер:
   ```bash
   git clone https://github.com/YOUR_USERNAME/duplicate-log-finder.git
   cd duplicate-log-finder
   ```
3. Запустите приложение:
   ```bash
   docker-compose up -d
   ```

### Вариант 2: Развертывание через systemd (Linux)

1. Скопируйте репозиторий на сервер
2. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Создайте systemd unit файл (см. deployment.md)
4. Запустите сервис

### Вариант 3: Развертывание через Gunicorn (рекомендуется для production)

1. Установите зависимости:
   ```bash
   pip install gunicorn
   ```
2. Запустите приложение:
   ```bash
   gunicorn --bind 0.0.0.0:5000 wsgi:app
   ```

## Проверка развертывания

После развертывания проверьте работоспособность:

1. Проверка здоровья сервиса:
   ```bash
   curl http://your-server-ip:5000/health
   ```

2. Тестирование функциональности:
   ```bash
   curl -X POST -F "file=@res/requests_08_26_06.06.2025.csv" http://your-server-ip:5000/find-duplicates
   ```

## Мониторинг

- Логи приложения: `journalctl -u duplicate-finder -f` (для systemd)
- Docker логи: `docker-compose logs -f`
- Проверка статуса: `systemctl status duplicate-finder` (для systemd)

## Обновление

Для обновления приложения:

1. Остановите сервис
2. Получите обновления:
   ```bash
   git pull origin master
   ```
3. Обновите зависимости при необходимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Перезапустите сервис

## Безопасность

1. Используйте HTTPS (Let's Encrypt)
2. Ограничьте доступ к API при необходимости
3. Регулярно обновляйте зависимости
4. Используйте reverse proxy (nginx) для дополнительной безопасности

## Резервное копирование

Регулярно создавайте резервные копии:
- Кода приложения
- Логов
- Конфигурационных файлов

## Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурацию сети и порты
4. Обратитесь к документации в deployment.md