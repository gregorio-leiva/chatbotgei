# DeepSeek Chatbot

A Django-based chatbot application using DeepSeek AI for intelligent conversations.

## Requirements
- Python 3.12.6
- PostgreSQL
- Django 5.0

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your database credentials and DeepSeek API key:
```
DB_NAME=chatbot_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DEEPSEEK_API_KEY=your_api_key
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Features
- Real-time chat interface
- DeepSeek AI integration
- PostgreSQL database for message storage
