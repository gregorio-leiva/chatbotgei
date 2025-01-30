from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
from .models import Conversation, ChatMessage
from decouple import config  # Para obtener las variables de entorno

@csrf_exempt
def chat_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()

            # Obtener o crear la conversación
            conversation = Conversation.objects.create(
                title=message[:50] + ('...' if len(message) > 50 else '')
            )

            # Guardar el mensaje del usuario
            ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            api_key = config('DEEPSEEK_API_KEY')
            if not api_key:
                return JsonResponse({'error': 'API key not configured'}, status=500)

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            # Aquí deberías obtener los mensajes anteriores en la conversación (si los hubiera)
            messages_for_api = [{"role": "assistant", "content": "Soy un asistente de Deepseek, estoy aquí para ayudarte."}]
            messages_for_api.append({"role": "user", "content": message})

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

            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return JsonResponse({'error': 'Error en la API de Deepseek'}, status=500)
            
            response_data = response.json()
            assistant_message = response_data['choices'][0]['message']['content']

            # Guardar el mensaje de la respuesta del asistente
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=assistant_message
            )
            
            return JsonResponse({
                'response': assistant_message,
                'conversation_id': conversation.id
            }, json_dumps_params={'ensure_ascii': False})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Error: {str(e)}"}, status=500)
    
    # Renderizar la página de chat en una solicitud GET
    return render(request, 'chatbot/chat.html')
