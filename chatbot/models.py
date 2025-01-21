from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-last_updated']

class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'chatbot_chatmessage'
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        # Asegurarse de que el contenido sea UTF-8
        if isinstance(self.content, str):
            self.content = self.content.encode('utf-8').decode('utf-8')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Modo Claro'),
        ('dark', 'Modo Oscuro'),
    ]
    
    FONT_SIZE_CHOICES = [
        ('small', 'Pequeño'),
        ('medium', 'Mediano'),
        ('large', 'Grande'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    font_size = models.CharField(max_length=10, choices=FONT_SIZE_CHOICES, default='medium')
    email_notifications = models.BooleanField(default=True)
    show_typing_status = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def get_profile_picture_url(self):
        """
        Retorna la URL de la imagen de perfil o la imagen por defecto
        """
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/chatbot/images/default.png'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
