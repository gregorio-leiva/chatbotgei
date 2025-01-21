from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests
from .models import ChatMessage, UserProfile, Conversation
from decouple import config
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chatbot:chatbot_chat_home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear perfil de usuario
            UserProfile.objects.create(user=user)
            
            # Enviar correo de bienvenida
            subject = '¡Bienvenido a ChatBot!'
            message = render_to_string('chatbot/email/welcome.html', {
                'user': user,
            })
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=message,
                )
            except Exception as e:
                print(f"Error al enviar el correo: {str(e)}")
            
            # Iniciar sesión automáticamente
            login(request, user)
            return redirect('chatbot:chatbot_chat_home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'chatbot/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('chatbot:chatbot_chat_home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chatbot:chatbot_chat_home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'chatbot/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('chatbot:chatbot_login')

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Actualizar información básica del usuario
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.save()

        # Actualizar información del perfil
        profile.bio = request.POST.get('bio', profile.bio)
        profile.theme = request.POST.get('theme', profile.theme)
        profile.font_size = request.POST.get('font_size', profile.font_size)
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.show_typing_status = request.POST.get('show_typing_status') == 'on'

        # Manejar la foto de perfil
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()

        # Respuesta para solicitudes AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('chatbot:chatbot_profile')
    
    return render(request, 'chatbot/profile.html', {
        'profile': profile,
        'user': request.user,
        'theme_choices': UserProfile.THEME_CHOICES,
        'font_size_choices': UserProfile.FONT_SIZE_CHOICES
    })

@login_required
def chat_home(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-last_updated')
    
    # Información de depuración
    debug_info = {
        'user_info': {
            'username': request.user.username,
            'email': request.user.email,
            'is_authenticated': str(request.user.is_authenticated),  
            'session_id': request.session.session_key
        },
        'api_info': {
            'api_key_exists': str(bool(config('DEEPSEEK_API_KEY', default=None))),  
            'api_key_length': len(config('DEEPSEEK_API_KEY', default='')) if config('DEEPSEEK_API_KEY', default=None) else 0,
            'api_endpoint': 'https://api.deepseek.com/v1/chat/completions',
            'model': 'deepseek-chat'
        },
        'system_info': {
            'debug_mode': str(config('DEBUG', default=False, cast=bool)),  
            'database': config('DB_NAME', default=''),
            'total_conversations': conversations.count()
        }
    }
    
    print("\n[DEBUG] Información de depuración:")
    print(json.dumps(debug_info, indent=2))
    
    return render(request, 'chatbot/chat.html', {
        'conversations': conversations,
        'debug_info': json.dumps(debug_info)  
    })

@login_required
def get_chat_history(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        messages = conversation.messages.all()
        messages_data = [{'role': msg.role, 'content': msg.content} for msg in messages]
        return JsonResponse({'messages': messages_data})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)

@login_required
def delete_conversation(request, conversation_id):
    if request.method == 'POST':
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            conversation.delete()
            return JsonResponse({'status': 'success'})
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversation not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
@csrf_exempt
def chat_message(request):
    if request.method == 'POST':
        try:
            print("\n[INFO] === Inicio de Procesamiento de Mensaje ===")
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
            
            # Debug: Información de la solicitud
            request_info = {
                'method': request.method,
                'content_type': request.content_type,
                'user': request.user.username,
                'message_length': len(message),
                'conversation_id': conversation_id,
                'headers': dict(request.headers)
            }
            print("\n[DEBUG] Información de la solicitud:")
            print(json.dumps(request_info, indent=2))

            # Debug: Información de la API
            api_info = {
                'api_key_exists': bool(config('DEEPSEEK_API_KEY', default=None)),
                'api_key_prefix': config('DEEPSEEK_API_KEY', default='')[:10] + '...' if config('DEEPSEEK_API_KEY', default=None) else None,
                'api_endpoint': 'https://api.deepseek.com/v1/chat/completions',
                'model': 'deepseek-chat'
            }
            print("\n[DEBUG] Información de la API:")
            print(json.dumps(api_info, indent=2))

            print("\n[INFO] Recibiendo mensaje...")
            print(f"[DEBUG] Mensaje recibido: {message}")
            print(f"[DEBUG] ID de conversación: {conversation_id}")

            # Obtener o crear la conversación
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id, user=request.user)
                    print(f"[INFO] Usando conversación existente: {conversation_id}")
                except Conversation.DoesNotExist:
                    print(f"[ERROR] Conversación {conversation_id} no encontrada")
                    return JsonResponse({'error': 'Conversation not found'}, status=404)
            else:
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=message[:50] + ('...' if len(message) > 50 else '')
                )
                print(f"[INFO] Nueva conversación creada: {conversation.id}")

            # Guardar el mensaje del usuario
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            print(f"[INFO] Mensaje del usuario guardado con ID: {user_message.id}")

            # Obtener la API key
            api_key = config('DEEPSEEK_API_KEY')
            if not api_key:
                print("\n[ERROR] API key no configurada")
                return JsonResponse({'error': 'API key not configured'}, status=500)

            print("\n[INFO] Preparando solicitud a la API...")
            print(f"[DEBUG] API Key: {api_key[:10]}...")
            
            # Hacer la solicitud a la API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Construir el historial de mensajes
            conversation_messages = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')
            messages_for_api = [{"role": "assistant", "content": "Soy un asistente de Deepseek, estoy aquí para ayudarte."}]
            
            # Agregar los últimos 5 mensajes del historial
            for chat_message in conversation_messages.reverse()[:5][::-1]:
                messages_for_api.append({
                    "role": chat_message.role,
                    "content": chat_message.content
                })
            
            # Agregar el mensaje actual
            messages_for_api.append({"role": "user", "content": message})
            
            print(f"[DEBUG] Número de mensajes en el contexto: {len(messages_for_api)}")
            
            payload = {
                "model": "deepseek-chat",
                "messages": messages_for_api,
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.95,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 0
            }

            print("\n[INFO] Enviando solicitud a la API...")
            print(f"[DEBUG] URL: https://api.deepseek.com/v1/chat/completions")
            print(f"[DEBUG] Headers: {headers}")
            print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
            
            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.encoding = 'utf-8'  # Forzar codificación UTF-8
                
                print(f"\n[INFO] Respuesta recibida. Status: {response.status_code}")
                print(f"[DEBUG] Headers de respuesta: {dict(response.headers)}")
                print(f"[DEBUG] Contenido de respuesta: {response.text[:500]}...")
                
                if response.status_code == 401:
                    print(f"[ERROR] Error de autenticación. Verifica la API key.")
                    return JsonResponse({
                        'error': 'Error de autenticación. Por favor, verifica la API key.'
                    }, status=500, json_dumps_params={'ensure_ascii': False})
                elif response.status_code != 200:
                    error_message = f"API Error: {response.status_code}"
                    try:
                        error_details = response.json()
                        print(f"[ERROR] Detalles del error: {error_details}")
                        if isinstance(error_details, dict):
                            error_message = error_details.get('error', {}).get('message', error_message)
                        else:
                            error_message = str(error_details)
                    except:
                        print(f"[ERROR] No se pudo parsear la respuesta de error: {response.text}")
                    return JsonResponse({
                        'error': error_message
                    }, status=500, json_dumps_params={'ensure_ascii': False})

                try:
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        assistant_message = response_data['choices'][0]['message']['content']
                        # Asegurarse de que el mensaje se pueda codificar correctamente
                        assistant_message = assistant_message.encode('utf-8', errors='ignore').decode('utf-8')
                    else:
                        print("[ERROR] Formato de respuesta inesperado")
                        print(f"[DEBUG] Respuesta completa: {response_data}")
                        return JsonResponse({
                            'error': 'Formato de respuesta inesperado de la API'
                        }, status=500, json_dumps_params={'ensure_ascii': False})
                except Exception as e:
                    print(f"[ERROR] Error al procesar la respuesta JSON: {str(e)}")
                    return JsonResponse({
                        'error': str(e)
                    }, status=500, json_dumps_params={'ensure_ascii': False})
                
                print(f"\n[INFO] Respuesta del asistente recibida")
                print(f"[DEBUG] Longitud de la respuesta: {len(assistant_message)} caracteres")

                try:
                    # Guardar la respuesta del asistente
                    ChatMessage.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=assistant_message
                    )

                    # Actualizar el timestamp de la conversación
                    conversation.save()
                    print("\n[INFO] Respuesta guardada en la base de datos")

                    return JsonResponse({
                        'response': assistant_message,
                        'conversation_id': conversation.id
                    }, json_dumps_params={'ensure_ascii': False})

                except Exception as e:
                    print(f"[ERROR] Error al guardar la respuesta: {str(e)}")
                    return JsonResponse({
                        'error': f"Error al guardar la respuesta: {str(e)}"
                    }, status=500, json_dumps_params={'ensure_ascii': False})
            except requests.exceptions.RequestException as e:
                print(f"\n[ERROR] Error en la solicitud HTTP: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError as e:
            print(f"\n[ERROR] Error de JSON: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"\n[ERROR] Error inesperado: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
