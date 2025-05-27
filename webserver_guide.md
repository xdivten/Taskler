Общие

1. Создаем юзера
adduser www-data
sudo usermod -aG www-data www-data

2. Клонируем проект
cd /var/www
sudo git clone LINK_TO_PROJECT

3. Настраиваем права для www-data
sudo chown -R www-data:www-data /var/www/
sudo chmod -R 755 /var/www
sudo chmod go-rwx /var/www
sudo chmod go+x /var/www
sudo chgrp -R www-data /var/www
sudo chmod -R go-rwx /var/www
sudo chmod -R g+rwx /var/www

4. Открывыем порт
sudo ufw allow 8000

5. Переходим в проект, создаем venv, пробуем запустить проект
python3.10 -m venv .venv
source .venv/bin/activate
python3.10 manage.py runserver 0.0.0.0:8000

проверяем public_id:8000
открывает - ок, если нет дебажим
собираем статику python manage.py collectstatic

6. ставим gunicorn, проверяем работу
gunicorn --bind 0.0.0.0:8000 app_name.wsgi

7. Обновляем settings.py
ALLOWED_HOSTS = ['HOST IP', 'DOMAIN NAIM', 'localhost']

8. выходим из окружения
deactivate

Gunicorn

9. Настраиваем gunicorn
sudo nano /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target


sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/repo/djangoprojectname
ExecStart=/var/www/repo/.venv/bin/gunicorn \
          --workers n*2+1 \
          --bind unix:/run/gunicorn.sock \
          app_name.wsgi:application

[Install]
WantedBy=multi-user.target

10. Запускаем сокет и проверяем
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
file /run/gunicorn.sock

если последние команды не показали ок дебажим
sudo journalctl -u gunicorn.socket

11. Активируем сокет
sudo systemctl status gunicorn

скорее всего написано Active: inactive (dead) - ок

12. Ставим соединение с сокетом
curl --unix-socket /run/gunicorn.sock localhost
если 400 можно попробовать вместо localhost public_ip

sudo systemctl status gunicorn
Active: active (running) - ок, если нет дебажим
sudo journalctl -u gunicorn

13. Перезапускаем gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

Nginx

14. Создаем конфигурацию для проекта
sudo nano /etc/nginx/sites-available/djangoprojectname

что-то типа
server {
    listen 80;
    server_name server_domain_or_IP;
    server_rokens off; # безопасность, пишем

    location /admin/ { # безопасность, закрываем админку
        allow admin1_ip;
        allow admin2_ip;
        deny all;
    }

    location ~* \.(htaccess|git|svn|env|ini|log|conf|bak|swp)$ { # безопасность, закрываем важные файлы
            deny all;
    }

    location /static/ {
        alias /var/www/djangoprojectname/static/;
    }

    location /media/ {
        alias /var/www/djangoprojectname/media/;
    }

    location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/project_access.log;
    error_log /var/log/nginx/project_error.log;
}

В разделе sever_name можно указать несколько адресов через пробел.
проверяем

15. Создаем символическую ссылку
sudo ln -s /etc/nginx/sites-available/project /etc/nginx/sites-enabled/

16. Удаляем стандартный конфиг
sudo rm /etc/nginx/sites-enabled/default

17. Проверяем синтакатсис
    sudo nginx -t
если не ок, исправляем
можем проверить логи
sudo tail -f /var/log/nginx/project_error.log

15. даем права и перезапускаем сервисы
sudo ufw allow 'Nginx Full'
sudo systemctl restart nginx
sudo systemctl restart gunicorn

заходим на public_ip:80


https

16. Заходим в окружение и ставим certbot
sudo /var/www/repo/.venv/bin/pip install certbot certbot-nginx

17. Подготавливаем команду certbot
sudo ln -s /var/www/repo/.venv/bin/certbot /usr/bin/certbot

18. ставим сертификат
sudo certbot --nginx
