# Generated by Django 5.0 on 2025-01-14 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_remove_chatmessage_conversation_id_conversation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='font_size',
            field=models.CharField(choices=[('small', 'Pequeño'), ('medium', 'Mediano'), ('large', 'Grande')], default='medium', max_length=10),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='show_typing_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='theme',
            field=models.CharField(choices=[('light', 'Modo Claro'), ('dark', 'Modo Oscuro')], default='light', max_length=10),
        ),
    ]
