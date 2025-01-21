# Documentación del ChatBot con DeepSeek AI

## 1. Descripción General del Proyecto

El ChatBot es una aplicación web desarrollada con Django que integra la API de DeepSeek para proporcionar conversaciones inteligentes y contextuales. El sistema permite a los usuarios mantener múltiples conversaciones, con un historial completo y una interfaz moderna.

## 2. Arquitectura del Sistema

### 2.1 Tecnologías Utilizadas
- **Backend**: Django 5.0
- **Base de Datos**: PostgreSQL
- **API**: DeepSeek
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Autenticación**: Django Authentication System

### 2.2 Estructura de Directorios
```
ChatBot/
├── chatbot/                 # Aplicación principal
│   ├── migrations/         # Migraciones de la base de datos
│   ├── templates/         # Plantillas HTML
│   │   └── chatbot/      
│   │       ├── base.html    # Plantilla base
│   │       ├── chat.html    # Interfaz del chat
│   │       ├── login.html   # Página de login
│   │       └── register.html # Página de registro
│   ├── static/           
│   │   └── chatbot/     
│   │       ├── css/      # Estilos CSS
│   │       └── js/       # Scripts JavaScript
│   ├── models.py         # Modelos de datos
│   ├── views.py          # Lógica de la aplicación
│   ├── urls.py          # URLs de la aplicación
│   └── forms.py         # Formularios
├── chatbot_project/      # Configuración del proyecto
├── requirements.txt      # Dependencias
└── manage.py            # Script de gestión
```

## 3. Modelos de Datos

### 3.1 User Profile
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme_preference = models.CharField(max_length=20)
    language_preference = models.CharField(max_length=10)
```

### 3.2 Conversation
```python
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
```

### 3.3 ChatMessage
```python
class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

## 3.4 Estructura de la Base de Datos

### 3.4.1 Diagrama Entidad-Relación
```
User ──┐
       ├── UserProfile
       │
       ├── Conversation ──┐
       │                  │
       └─────────────────┴── ChatMessage
```

### 3.4.2 Creación de la Base de Datos
```sql
-- Crear la base de datos
CREATE DATABASE iwie_chatbot
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

-- Conectar a la base de datos
\c iwie_chatbot

-- Crear tabla de usuarios (complementa la tabla auth_user de Django)
CREATE TABLE user_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    theme_preference VARCHAR(20) DEFAULT 'light',
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de conversaciones
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de mensajes
CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT true,
    tokens_used INTEGER DEFAULT 0
);

-- Crear índices para optimizar consultas
CREATE INDEX idx_conversation_user ON conversation(user_id);
CREATE INDEX idx_conversation_timestamp ON conversation(timestamp);
CREATE INDEX idx_message_conversation ON chat_message(conversation_id);
CREATE INDEX idx_message_timestamp ON chat_message(timestamp);

-- Crear vistas para consultas comunes
CREATE VIEW recent_conversations AS
SELECT 
    c.id,
    c.title,
    c.user_id,
    c.timestamp,
    cm.content as last_message,
    cm.timestamp as last_message_time
FROM conversation c
LEFT JOIN LATERAL (
    SELECT content, timestamp
    FROM chat_message
    WHERE conversation_id = c.id
    ORDER BY timestamp DESC
    LIMIT 1
) cm ON true
ORDER BY cm.timestamp DESC NULLS LAST;

-- Triggers para actualizar timestamps
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation
    SET last_message_at = NEW.timestamp
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversation_last_message
AFTER INSERT ON chat_message
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

### 3.4.3 Consultas Útiles

#### Obtener conversaciones recientes de un usuario
```sql
SELECT * FROM recent_conversations
WHERE user_id = [user_id]
LIMIT 10;
```

#### Obtener mensajes de una conversación
```sql
SELECT 
    cm.id,
    cm.role,
    cm.content,
    cm.timestamp,
    cm.tokens_used
FROM chat_message cm
WHERE cm.conversation_id = [conversation_id]
ORDER BY cm.timestamp ASC;
```

#### Estadísticas de uso
```sql
SELECT 
    u.username,
    COUNT(DISTINCT c.id) as total_conversations,
    COUNT(cm.id) as total_messages,
    SUM(cm.tokens_used) as total_tokens
FROM auth_user u
LEFT JOIN conversation c ON u.id = c.user_id
LEFT JOIN chat_message cm ON c.id = cm.conversation_id
GROUP BY u.id, u.username;
```

### 3.4.4 Respaldo y Restauración

#### Backup de la base de datos
```bash
pg_dump -U postgres -d iwie_chatbot > backup_chatbot_$(date +%Y%m%d).sql
```

#### Restaurar la base de datos
```bash
psql -U postgres -d iwie_chatbot < backup_chatbot_YYYYMMDD.sql
```

### 3.4.5 Mantenimiento

#### Limpieza de conversaciones antiguas
```sql
-- Archivar conversaciones inactivas por más de 30 días
UPDATE conversation
SET is_active = false
WHERE last_message_at < NOW() - INTERVAL '30 days';

-- Eliminar conversaciones inactivas por más de 90 días
DELETE FROM conversation
WHERE last_message_at < NOW() - INTERVAL '90 days';
```

#### Optimización de la base de datos
```sql
-- Analizar y actualizar estadísticas
ANALYZE conversation;
ANALYZE chat_message;

-- Vacuuming para recuperar espacio
VACUUM FULL conversation;
VACUUM FULL chat_message;
```

## 4. API y Endpoints

### 4.1 Endpoints de Autenticación
- `GET/POST /login/`: Inicio de sesión
- `GET/POST /register/`: Registro de usuario
- `POST /logout/`: Cierre de sesión

### 4.2 Endpoints de Chat
- `GET /chat/`: Vista principal del chat
- `POST /chat/message/`: Enviar mensaje
- `GET /chat/conversation/<id>/`: Cargar conversación
- `POST /chat/conversation/new/`: Nueva conversación

### 4.3 Integración con DeepSeek
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": messages_for_api,
    "temperature": 0.7,
    "max_tokens": 2000
}
```

## 5. Funcionalidades Principales

### 5.1 Sistema de Chat
- Conversaciones en tiempo real
- Múltiples hilos de conversación
- Historial persistente
- Cambio dinámico entre conversaciones

### 5.2 Gestión de Usuarios
- Registro de usuarios
- Autenticación
- Preferencias de usuario
- Historial personal

### 5.3 Interfaz de Usuario
- Diseño responsivo
- Temas claros/oscuros
- Indicadores de estado
- Navegación intuitiva

## 6. Seguridad

### 6.1 Medidas Implementadas
- Protección CSRF
- Autenticación obligatoria
- Sanitización de datos
- Validación de entrada
- Manejo seguro de API keys

### 6.2 Manejo de Sesiones
- Sesiones persistentes
- Timeouts configurables
- Protección contra hijacking

## 7. Manejo de Errores

### 7.1 Tipos de Errores
- Errores de autenticación
- Errores de API
- Errores de base de datos
- Errores de validación

### 7.2 Sistema de Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'chatbot': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 8. Configuración del Entorno

### 8.1 Variables de Entorno (.env)
```
DB_NAME=iwie_chatbot
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DEEPSEEK_API_KEY=your_api_key
```

### 8.2 Dependencias
```
Django==5.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
python-decouple==3.8
requests==2.31.0
```

## 8.3 Configuración y Ejecución del Proyecto

### 8.3.1 Instalación de PostgreSQL
1. Descargar PostgreSQL:
   ```bash
   # Windows: Descargar el instalador de https://www.postgresql.org/download/windows/
   # Durante la instalación:
   # - Anotar la contraseña del usuario postgres
   # - Mantener el puerto por defecto (5432)
   # - Instalar pgAdmin 4 (opcional pero recomendado)
   ```

2. Verificar la instalación:
   ```bash
   # Abrir CMD como administrador
   psql -U postgres -c "SELECT version();"
   # Debería mostrar la versión de PostgreSQL
   ```

### 8.3.2 Crear y Configurar la Base de Datos
1. Crear la base de datos:
   ```bash
   # Conectar a PostgreSQL
   psql -U postgres

   # Crear la base de datos
   CREATE DATABASE iwie_chatbot;

   # Verificar la creación
   \l
   
   # Salir de psql
   \q
   ```

2. Configurar el archivo `.env`:
   ```bash
   # Crear archivo .env en la raíz del proyecto
   echo DB_NAME=iwie_chatbot > .env
   echo DB_USER=postgres >> .env
   echo DB_PASSWORD=tu_contraseña >> .env
   echo DB_HOST=localhost >> .env
   echo DB_PORT=5432 >> .env
   echo DEEPSEEK_API_KEY=tu_api_key >> .env
   ```

### 8.3.3 Configuración del Entorno Virtual
1. Instalar virtualenv si no está instalado:
   ```bash
   pip install virtualenv
   ```

2. Crear y activar el entorno virtual:
   ```bash
   # Crear entorno virtual
   python -m venv venv

   # Activar entorno virtual
   # Windows
   venv\Scripts\activate

   # Verificar activación (debería mostrar el entorno virtual)
   where python
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### 8.3.4 Configuración de Django
1. Aplicar migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   # Seguir las instrucciones para crear el usuario administrador
   ```

3. Recolectar archivos estáticos:
   ```bash
   python manage.py collectstatic
   ```

### 8.3.5 Iniciar el Proyecto
1. Verificar configuración:
   ```bash
   # Verificar que PostgreSQL esté corriendo
   # Windows: Verificar en Servicios que "postgresql-x64-XX" esté activo
   
   # Verificar conexión a la base de datos
   python manage.py dbshell
   # Si conecta correctamente, salir con \q
   ```

2. Iniciar el servidor:
   ```bash
   python manage.py runserver
   ```

3. Verificar el funcionamiento:
   - Abrir http://localhost:8000/admin
   - Iniciar sesión con el superusuario creado
   - Verificar acceso al panel de administración

### 8.3.6 Solución de Problemas Comunes

#### Error de conexión a PostgreSQL
```bash
# Verificar servicio de PostgreSQL
# Windows
net start postgresql-x64-XX

# Verificar archivo pg_hba.conf
# Ubicación típica: C:\Program Files\PostgreSQL\XX\data\pg_hba.conf
# Asegurarse que tenga estas líneas:
# host    all             all             127.0.0.1/32            scram-sha-256
# host    all             all             ::1/128                 scram-sha-256
```

#### Error de migraciones
```bash
# Resetear migraciones (¡CUIDADO! Esto borrará todos los datos)
python manage.py reset_db  # Requiere django-extensions
python manage.py makemigrations
python manage.py migrate
```

#### Error de archivos estáticos
```bash
# Limpiar archivos estáticos
python manage.py collectstatic --clear
python manage.py collectstatic --no-input
```

### 8.3.7 Comandos Útiles

#### Backup rápido
```bash
# Backup de la base de datos
pg_dump -U postgres iwie_chatbot > backup.sql

# Backup de archivos media
xcopy /E /I media backup\media
```

#### Verificar estado del proyecto
```bash
# Verificar migraciones pendientes
python manage.py showmigrations

# Verificar URLs configuradas
python manage.py show_urls

# Verificar configuración
python manage.py check
```

#### Reiniciar el proyecto
```bash
# Windows
taskkill /F /IM python.exe
python manage.py runserver
```

### 8.3.8 Monitoreo en Producción
```bash
# Verificar logs de Django
python manage.py shell
>>> from django.conf import settings
>>> print(settings.LOGGING)

# Verificar conexiones a la base de datos
SELECT * FROM pg_stat_activity WHERE datname = 'iwie_chatbot';
```

## 9. Guía de Desarrollo

### 9.1 Configuración Local
1. Clonar repositorio
2. Crear entorno virtual
3. Instalar dependencias
4. Configurar .env
5. Migrar base de datos
6. Iniciar servidor

### 9.2 Convenciones de Código
- PEP 8 para Python
- BEM para CSS
- ESLint para JavaScript

## 10. Solución de Problemas

### 10.1 Problemas Comunes
1. **Error de Conexión API**
   - Verificar API key
   - Comprobar conexión
   - Revisar logs

2. **Problemas de Base de Datos**
   - Verificar credenciales
   - Comprobar servicio PostgreSQL
   - Revisar permisos

3. **Errores de Codificación**
   - Configurar UTF-8
   - Validar entrada de usuario
   - Revisar respuestas API

### 10.2 Debugging
- Logs detallados en consola
- Información de depuración en desarrollo
- Manejo de excepciones documentado

## 11. Mantenimiento

### 11.1 Tareas Regulares
- Backup de base de datos
- Actualización de dependencias
- Monitoreo de logs
- Limpieza de datos antiguos

### 11.2 Mejoras Futuras
- Implementación de WebSockets
- Mejoras en el sistema de caché
- Optimización de consultas
- Expansión de funcionalidades AI

## 12. Contacto y Soporte

Para soporte técnico o consultas:
- Crear un issue en el repositorio
- Documentar el problema detalladamente
- Incluir logs relevantes
- Especificar entorno de desarrollo

## Mejoras en el Perfil de Usuario (20/01/2025)

### Gestión de Imágenes de Perfil
- Implementada la propiedad `get_profile_picture_url` en el modelo `UserProfile`
- Si el usuario no tiene imagen, se usa una imagen por defecto desde `media/profile_pics/default.jpg`
- Configurado el almacenamiento local para desarrollo (`FileSystemStorage`)

### Interfaz de Usuario
- Agregado botón "Volver" en la página de perfil
- Implementada detección de cambios no guardados
- Agregadas alertas y confirmaciones para prevenir pérdida de datos

### Sistema de Protección de Cambios
1. **Detección de Modificaciones**
   - Variable `formModified` que rastrea cambios en el formulario
   - Event listeners en todos los campos (inputs, textareas, selects)
   - Detección de cambios en:
     - Información básica (nombre, apellido, bio)
     - Preferencias (tema, tamaño de fuente)
     - Foto de perfil
     - Configuraciones de notificaciones

2. **Alertas y Confirmaciones**
   - Al hacer clic en "Volver" con cambios sin guardar:
     - Muestra diálogo de confirmación
     - Opciones: "Guardar y salir" o "Salir sin guardar"
   - Al intentar cerrar/recargar la página:
     - Muestra advertencia estándar del navegador
     - Previene pérdida accidental de cambios

3. **Manejo del Formulario**
   - Envío asíncrono de datos (AJAX)
   - Reseteo de estado `formModified` tras guardar exitosamente
   - Recarga de página para aplicar cambios guardados

### Archivos Modificados
- `models.py`: Actualización del modelo UserProfile
- `views.py`: Mejoras en la vista de perfil
- `profile.html`: Nuevo botón y sistema de protección de cambios
- `settings.py`: Configuración de almacenamiento local

### Notas de Implementación
- El sistema usa `beforeunload` para detectar intentos de salir de la página
- Las alertas son nativas del navegador para mejor compatibilidad
- La detección de cambios es en tiempo real para mejor experiencia de usuario

### Próximas Mejoras Sugeridas
- Agregar notificaciones más amigables usando toasts o alerts personalizados
- Implementar guardado automático de borradores
- Agregar opción de recortar/redimensionar foto de perfil


## Estado Actual del Sistema (20/01/2025)

### Sistema de Autenticación
El sistema de autenticación ha sido implementado exitosamente con las siguientes funcionalidades:

1. **Registro de Usuarios**
   - Formulario de registro completamente funcional
   - Validación de datos en tiempo real
   - Creación automática de perfil de usuario al registrarse

2. **Inicio de Sesión**
   - Sistema de login 
   - Manejo de sesiones de usuario
   - Redirección inteligente post-login

3. **Recuperación de Contraseña**
   - Funcionalidad implementada pero pendiente de configuración
   - Requiere configuración del servidor SMTP para envío de correos
   - Estado: En desarrollo

### Gestión de Perfiles

1. **Imagen de Perfil**
   - Sistema implementado con imagen predeterminada
   - Ubicación: `media/profile_pics/default.jpg`
   - Capacidad de personalización por usuario
   - Almacenamiento configurable (local/AWS S3)

3. **Protección de Datos**
   - Sistema de alertas para cambios no guardados
   - Confirmación antes de abandonar cambios
   - Prevención de pérdida accidental de datos

### Características Destacadas
- **Imagen Predeterminada**: Todos los usuarios nuevos inician con una imagen de perfil por defecto, manteniendo una apariencia profesional desde el primer momento.
- **Guardado Seguro**: Sistema de alertas que previene la pérdida accidental de cambios en el perfil.
- **Navegación Intuitiva**: Botón "Volver" con confirmación de guardado de cambios pendientes.

### Próximos Pasos
1. **Prioridad Alta**
   - Configurar sistema de recuperación de contraseña
   - Implementar envío de correos electrónicos
   - Mejorar validaciones de seguridad

2. **Mejoras Futuras**
   - Implementar edición de imagen de perfil con recorte
   - Agregar opciones adicionales de personalización
   - Optimizar el rendimiento de carga de imágenes



## Sistema de Correos Electrónicos

### Configuración de Zoho Mail
El sistema utiliza Zoho Mail como servidor SMTP para el envío de correos electrónicos. La configuración se encuentra en `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### Funcionalidades Implementadas

1. **Registro de Usuario con Email**
   - Se ha agregado un campo obligatorio de correo electrónico en el formulario de registro
   - Al registrarse, el usuario recibe un correo de bienvenida
   - La plantilla del correo de bienvenida se encuentra en `templates/chatbot/email/welcome.html`

2. **Recuperación de Contraseña**
   - Los usuarios pueden restablecer su contraseña a través de su correo electrónico
   - El proceso incluye:
     1. Solicitud de restablecimiento con el correo registrado
     2. Envío de correo con link de restablecimiento
     3. Página para crear nueva contraseña
   - Las plantillas relacionadas se encuentran en:
     - `templates/chatbot/password_reset.html`
     - `templates/chatbot/password_reset_email.html`
     - `templates/chatbot/password_reset_subject.txt`

### Archivos Modificados

1. **forms.py**
   - Nuevo formulario `CustomUserCreationForm` que incluye campo de email

2. **views.py**
   - Actualización de `register_view` para manejar el registro con email
   - Implementación del envío de correo de bienvenida

3. **urls.py**
   - Rutas para el proceso de recuperación de contraseña

### Notas de Seguridad
- Las credenciales de correo se manejan a través de variables de entorno
- Se utiliza SSL para la conexión con el servidor SMTP
- Los tokens de restablecimiento de contraseña son de un solo uso y tienen tiempo de expiración

## Sistema de Imágenes de Perfil

### Estructura de Archivos
- La imagen por defecto `default.png` se encuentra en:
  ```
  chatbot/static/chatbot/images/default.png
  ```
- Las imágenes subidas por los usuarios se almacenan en:
  ```
  media/profile_pics/
  ```

### Implementación

1. **Modelo UserProfile**
   ```python
   class UserProfile(models.Model):
       user = models.OneToOneField(User, on_delete=models.CASCADE)
       profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)

       @property
       def get_profile_picture_url(self):
           if self.profile_picture and hasattr(self.profile_picture, 'url'):
               return self.profile_picture.url
           return '/static/chatbot/images/default.png'
   ```

2. **Template Profile**
   ```html
   <div class="profile-picture-container">
       <img src="{{ user.userprofile.get_profile_picture_url }}" 
            alt="Profile Picture" 
            class="profile-picture" 
            id="profile-picture-preview">
       <div class="profile-picture-overlay">
           <label for="id_profile_picture" class="btn btn-light btn-sm">
               <i class="fas fa-camera"></i> Cambiar foto
           </label>
       </div>
       <input type="file" name="profile_picture" 
              accept="image/*" 
              id="id_profile_picture" 
              style="display: none;" 
              onchange="previewImage(this);">
   </div>
   ```

### Características
- Vista previa instantánea al seleccionar una nueva imagen
- Imagen por defecto para usuarios nuevos o sin foto
- Almacenamiento separado para imágenes estáticas y subidas por usuarios
- Validación de tipo de archivo (solo imágenes)
- Interfaz intuitiva para cambio de foto

### Estilos CSS
```css
.profile-picture-container {
    position: relative;
    width: 150px;
    height: 150px;
    margin: 0 auto;
}

.profile-picture {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

.profile-picture-overlay {
    position: absolute;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    width: 100%;
    height: 0;
    transition: .5s ease;
    border-bottom-left-radius: 50%;
    border-bottom-right-radius: 50%;
}

.profile-picture-container:hover .profile-picture-overlay {
    height: 50%;
}
```

### JavaScript
```javascript
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile-picture-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}
```

### Notas Importantes
1. La imagen por defecto está en el directorio estático para mejor rendimiento
2. Las imágenes de usuario se almacenan en el directorio media para mejor gestión
3. El sistema maneja automáticamente casos donde:
   - Un usuario nuevo se registra
   - Un usuario no ha subido una imagen
   - Hay problemas con la imagen subida
