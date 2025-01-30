from django.db import models
from django.utils import timezone

# Modelo para representar una conversación
class Conversation(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['-last_updated']

# Modelo para representar los mensajes en la conversación
class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('assistant', 'Assistant'),
        ('user', 'User'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)  # Relaciona solo con la conversación
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
