# Слэнг для родителей

Сайт-словарь подросткового слэнга. Flask + MySQL.

## Быстрый старт

1. Клонировать:
   git clone <url>
   cd slang-for-parents

2. Виртуальное окружение:
   python -m venv .venv
   .venv\Scripts\activate      (Windows)
   source .venv/bin/activate   (Linux/macOS)

3. Зависимости:
   pip install -r requirements.txt

4. Настроить `.env`:
   cp .env.example .env
   → вписать пароль MySQL, SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD.

5. База данных:
   mysql -u root -p < db/schema.sql
   mysql -u root -p < db/seed.sql

6. Фон:
   положить `background.jpg` в `static/images/`.

7. Запуск:
   python app.py
   → открыть http://127.0.0.1:5000

## Страницы

| URL | Назначение |
|---|---|
| `/` | Главная |
| `/dictionary` | Словарь |
| `/word/<id>` | Слово |
| `/quiz` | Викторина (20 вопросов) |
| `/fill-blank` | Пропуски (20 заданий) |
| `/suggest` | Предложить слово |
| `/admin/login` | Вход админа |
| `/admin` | Админ-панель |

## Как пользоваться

- **Родитель**: заходит на главную → словарь → викторина → пропуски.
- **Админ**: заходит на `/admin/login`, логинится (данные из `.env`). В панели видит предложки и кнопки «Одобрить/Отклонить/Редактировать», а также может добавлять вопросы и задания с пропусками.
- **Подросток**: через кнопку «Предложить своё» (или `/suggest`) отправляет слово — оно падает в админку.

## Стек

Python 3.10+ · Flask 3 · MySQL 8 / MariaDB 10.4+ · HTML5 · CSS3 · Vanilla JS