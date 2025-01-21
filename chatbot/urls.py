from django.urls import path
from . import views
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)

app_name = 'chatbot'

urlpatterns = [
    path('', views.login_view, name='chatbot_login'),
    path('register/', views.register_view, name='chatbot_register'),
    path('logout/', views.logout_view, name='chatbot_logout'),
    path('profile/', views.profile_view, name='chatbot_profile'),
    path('chat/', views.chat_home, name='chatbot_chat_home'),
    path('chat/message/', views.chat_message, name='chatbot_chat_message'),
    path('chat/history/<int:conversation_id>/', views.get_chat_history, name='chatbot_chat_history'),
    path('chat/delete/<int:conversation_id>/', views.delete_conversation, name='chatbot_delete_conversation'),
    
    # URLs para reseteo de contraseña
    path('password-reset/', 
         PasswordResetView.as_view(
             template_name='chatbot/password_reset.html',
             email_template_name='chatbot/password_reset_email.html',
             subject_template_name='chatbot/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         PasswordResetDoneView.as_view(
             template_name='chatbot/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='chatbot/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(
             template_name='chatbot/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
