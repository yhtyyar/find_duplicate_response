# Руководство по развертыванию приложения поиска дубликатов в логах

## Подготовка к развертыванию

### 1. Подготовка репозитория

Перед развертыванием убедитесь, что все изменения закоммичены:

```bash
# Проверьте статус репозитория
git status

# Добавьте все изменения
git add .

# Создайте коммит
git commit -m "Подготовка к развертыванию на сервере"

# Отправьте изменения в удаленный репозиторий
git push origin master
```

### 2. Структура проекта для развертывания

Проект уже имеет правильную структуру:
- `api.py` - основной файл для запуска REST API
- `controller.py` - для запуска CLI версии
- `model.py` - бизнес-логика
- `view.py` - отображение результатов
- `requirements.txt` - зависимости
- `res/` - примеры данных

### 3. Зависимости

Убедитесь, что в requirements.txt указаны только необходимые зависимости:
```
flask
```

## Развертывание на сервере

### Вариант 1: Развертывание как systemd сервис (Linux)

1. Скопируйте проект на сервер:
```bash
scp -r . user@server:/path/to/deployment/
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
cd /path/to/deployment/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Создайте systemd unit файл `/etc/systemd/system/duplicate-finder.service`:
```ini
[Unit]
Description=Duplicate Log Finder API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/deployment
ExecStart=/path/to/deployment/venv/bin/python api.py
Environment=PATH=/path/to/deployment/venv/bin
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl start duplicate-finder
sudo systemctl enable duplicate-finder
```

### Вариант 2: Использование Gunicorn (рекомендуется для production)

1. Установите Gunicorn:
```bash
pip install gunicorn
```

2. Создайте файл `wsgi.py`:
```python
from api import app

if __name__ == "__main__":
    app.run()
```

3. Запустите приложение через Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

4. Для запуска как сервис создайте systemd unit файл:
```ini
[Unit]
Description=Duplicate Log Finder API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/deployment
ExecStart=/path/to/deployment/venv/bin/gunicorn --bind 0.0.0.0:5000 wsgi:app
Environment=PATH=/path/to/deployment/venv/bin
Restart=always

[Install]
WantedBy=multi-user.target
```

### Вариант 3: Использование Docker

1. Создайте Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "api.py"]
```

2. Создайте docker-compose.yml:
```yaml
version: '3.8'
services:
  duplicate-finder:
    build: .
    ports:
      - "5000:5000"
    restart: always
```

3. Запустите приложение:
```bash
docker-compose up -d
```

## Настройка reverse proxy (nginx)

Для production рекомендуется использовать nginx как reverse proxy:

1. Установите nginx:
```bash
sudo apt install nginx
```

2. Создайте конфигурационный файл `/etc/nginx/sites-available/duplicate-finder`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

3. Активируйте сайт:
```bash
sudo ln -s /etc/nginx/sites-available/duplicate-finder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Мониторинг и логирование

1. Проверка статуса сервиса:
```bash
systemctl status duplicate-finder
```

2. Просмотр логов:
```bash
journalctl -u duplicate-finder -f
```

3. Логи приложения находятся в `/var/log/duplicate-finder/`

## Обновление приложения

1. Остановите сервис:
```bash
sudo systemctl stop duplicate-finder
```

2. Обновите код:
```bash
cd /path/to/deployment
git pull origin master
```

3. Обновите зависимости при необходимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Перезапустите сервис:
```bash
sudo systemctl start duplicate-finder
```

## Безопасность

1. Используйте HTTPS (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

2. Ограничьте доступ к API при необходимости через nginx:
```nginx
location / {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://127.0.0.1:5000;
    # ... остальные настройки
}
```

## Резервное копирование

Регулярно создавайте резервные копии:
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/deployment/
```