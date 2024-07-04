# FOODGRAM

### Описание проекта:

##### Foodgram - сайт, на котором пользователи публикуют рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

##### Проект находится по адресу: https://foodgram-project.zapto.org/

#### Foodgram предоставляет следующие возможности:

##### - регистрация, авторизация, просмотр и редактирование профиля, просмотр списка пользователей.
##### - создание, обновление, удаление, просмотр рецептов.
##### - добавление и удаление рецептов, скачивание списка покупок.
##### - добавление и удаление рецептов из избранного.
##### - подписка и отписка на пользователей, просмотр подписок.

#### Использованные технологии:

##### - Django (Python web-фреймворк)
##### - Django REST framework (Web-фреймворк для создания веб-сервисов и API на основе фреймворка Django.)
##### - Docker (Контейнеризация приложения)
##### - PostgreSQL (Реляционная база данных)
##### - Nginx (Веб-сервер и обратный прокси)
##### - Gunicorn: (WSGI-сервер для Python)

#### Инструкция по запуску на локальной машине:

##### 1. Клонируем репозиторий: git clone git@github.com:Eduard-Golovash/foodgram-project-react.git
##### 2. Переходим в директорию infra/ и создаем файл .env: cd infra/ touch .env
##### 3. Заполняем файл .env своими данными по образцу:
##### POSTGRES_USER=django_user
##### POSTGRES_PASSWORD=mysecretpassword
##### POSTGRES_DB=django
##### DB_HOST=db
##### DB_PORT=5432
##### 4. Создаем образы и запускаем контейнеры из директории infra/: docker-compose up -d build
##### 5. Проверяем, что контейнеры запустились: docker ps
##### 6. Делаем миграции: docker-compose exec backend python manage.py migrate
##### 7. Собираем статику: docker-compose exec backend python manage.py collectstatic
##### 8. Создаем суперюзера: docker-compose exec backend python manage.py createsuperuser
##### 9. Добавляем теги для рецептов через админ-панель проекта http://localhost/admin/, так как это поле является обязательным для сохранения рецепта и добавляется только админом.

#### Инструкция для разворачивания проекта на удаленном сервере:

##### 1. Клонируем репозиторий: git clone git@github.сom:Eduard-Golovash/foodgram-project-react.git
##### 2. Выполняем вход на удаленный сервер.
##### 3. Устанавливаем Docker и Docker Compose на сервер:
##### - apt install docker.io
##### - sudo apt install curl
##### - curl -fsSL https://get.docker.com -o get-docker.sh
##### - sh get-docker.sh
##### - sudo apt-get install docker-compose-plugin
##### 4. Редактируем конфигурацию сервера Nginx: локально изменяем файл infra/nginx.conf, заменив данные в строке server_name на IP-адрес удаленного сервера.
##### 5. Копируем на сервер файлы docker-compose.yml, nginx.conf из папки infra:
##### - scp infra/docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
##### - scp infra/nginx.conf <username>@<host>:/home/<username>/nginx.conf
##### 6. Создаем переменные окружения и добавляем их в Secrets GitHub Actions:
###### SECRET_KEY              # секретный ключ Django проекта
###### DOCKER_PASSWORD         # пароль от Docker Hub
###### DOCKER_USERNAME         # логин Docker Hub
###### HOST                    # публичный IP сервера
###### USER                    # имя пользователя на сервере
###### PASSPHRASE              # *если ssh-ключ защищен паролем
###### SSH_KEY                 # приватный ssh-ключ
###### TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
###### TELEGRAM_TOKEN          # токен бота, посылающего сообщение

###### DB_ENGINE               # django.db.backends.postgresql
###### POSTGRES_DB             # postgres
###### POSTGRES_USER           # postgres
###### POSTGRES_PASSWORD       # postgres
###### DB_HOST                 # db
###### DB_PORT                 # 5432 (порт по умолчанию)
##### 7. Запускаем приложение в контейнерах: docker-compose up -d --build
##### 8. Делаем миграции: docker-compose exec backend python manage.py migrate
##### 9. Создаем суперпользователя: docker-compose exec backend python manage.py createsuperuser
##### 10. Собираем статику: docker-compose exec backend python manage.py collectstatic
##### 11. Заполняем тестовыми данными: docker-compose exec backend python manage.py loaddata ingredients.json
##### 12. Команда для остановки приложения в контейнерах:
##### - docker-compose down -v      # с их удалением
##### - docker-compose stop         # без удаления

#### API Foodgram

##### - AUTH: получение/удаление токена авторизации.
##### - USERS: регистрация, просмотр/изменение профиля, подписка/отписка на пользователей.
##### - TAGS: создание и редактирование тегов (только администраторы).
##### - RECIPES: создание, просмотр, обновление, удаление рецептов. Возможность добавления в избранное и список покупок.
##### - INGREDIENTS: добавление, просмотр, обновление, удаление ингредиентов.

#### Примеры использования API

##### Регистрация пользователя:
###### POST /api/users/
###### Тело запроса:
###### {
######    "email": "vpupkin@yandex.ru",
######    "username": "vasya.pupkin",
######    "first_name": "Вася",
######    "last_name": "Пупкин",
######    "password": "Qwerty123"
###### }

##### Получение токена:
###### POST /api/auth/token/login/
###### Тело запроса:
###### {
######    "password": "Qwerty123",
######    "email": "vpupkin@yandex.ru"
###### }

##### Добавление рецепта:
###### POST /api/recipes/
###### Authorization: Token <TOKENVALUE>
###### Тело запроса:
###### {
######    "ingredients": [
######        {
######            "id": 1123,
######            "amount": 10
######        }
######    ],
######    "tags": [1, 2],
######    "image": "data:image/png;base64,...",
######    "name": "string",
######    "text": "string",
######    "cooking_time": 1
###### }

### Автор:

###### Головаш Эдуард
###### GitHub: Eduard-Golovash