# Documentación del Proyecto ChatBotGei

## 1. Introducción
Este proyecto es un chatbotgei diseñado para proporcionar respuestas automáticas a preguntas frecuentes y asistir a los usuarios en la navegación de un sitio web.

## 2. Estructura de Datos
La estructura de datos del chatbotgei se compone de varios modelos que representan las entidades principales en el sistema:

- **Conversation**
  ```python
  class Conversation(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      title = models.CharField(max_length=200)
      timestamp = models.DateTimeField(auto_now_add=True)
  ```

- **ChatMessage**
  ```python
  class ChatMessage(models.Model):
      conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
      role = models.CharField(max_length=50)
      content = models.TextField()
      timestamp = models.DateTimeField(auto_now_add=True)
  ```

## 3. Arquitectura del Sistema
- **Backend**: Django 4.2
- **Base de Datos**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript

## 4. Estructura del Proyecto
```plaintext
ChatBotGEI/
├── chatbot/                 # Aplicación principal
│   ├── migrations/         # Migraciones de la base de datos
│   ├── static/             # Archivos estáticos
│   │   └── chatbot/        # CSS y JS específicos del chatbot
│   ├── templates/          # Plantillas HTML
│   │   └── chatbot/      
│   │       ├── base.html    # Plantilla base
│   │       ├── chat.html    # Interfaz del chat
│   │       ├── login.html   # Página de login
│   │       └── register.html # Página de registro
│   ├── __init__.py
│   ├── admin.py            # Configuración del admin de Django
│   ├── apps.py             # Configuración de la aplicación
│   ├── forms.py            # Formularios
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Lógica de la aplicación
│   ├── urls.py             # URLs de la aplicación
│   └── tests.py            # Pruebas de la aplicación
├── chatbot_project/        # Configuración del proyecto
│   ├── __init__.py
│   ├── settings.py         # Configuración del proyecto Django
│   ├── urls.py             # URLs del proyecto
│   └── wsgi.py             # Punto de entrada WSGI
├── requirements.txt        # Dependencias
└── manage.py               # Script de gestión



## 5. Instalación
1. Clona el repositorio:
 
   git clone https://github.com/gregorio-leiva/chatbotgei.git

2. Navega al directorio del proyecto:

   cd chatbotgei

3. Crea y activa un entorno virtual:
   python -m venv venv
   .\venv\Scripts\activate  # Para Windows

4. Instala las dependencias:
   pip install -r requirements.txt

## 6. Uso
Para ejecutar el chatbot, utiliza el siguiente comando:

python manage.py runserver

Luego, abre tu navegador y visita `http://localhost:8000` para interactuar con el chatbot.

## 7. Contribuciones
Las contribuciones son bienvenidas. Por favor, sigue estos pasos:
1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
3. Realiza tus cambios y haz un commit (`git commit -m 'Agregada nueva característica'`).
4. Haz un push a la rama (`git push origin feature/nueva-caracteristica`).
5. Abre un Pull Request.
