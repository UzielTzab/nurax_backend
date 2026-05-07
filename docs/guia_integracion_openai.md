# Guía de Integración: Consumir API de OpenAI (ChatGPT) en Django

Esta guía te llevará paso a paso para configurar tu cuenta en OpenAI, instalar las herramientas necesarias en tu backend de Django y crear un endpoint (API) que pueda comunicarse con el modelo de ChatGPT.

---

## Paso 1: Configuración en OpenAI (Obtener tu API Key)

Para poder comunicarte con los servidores de OpenAI, necesitas una clave de acceso (API Key).

1. **Crear una cuenta:**
   - Dirígete a [platform.openai.com](https://platform.openai.com/) y crea una cuenta o inicia sesión.

2. **Configurar facturación (Billing):**
   - OpenAI requiere que tengas saldo o una tarjeta de crédito vinculada para usar su API (no es gratis, aunque es muy barato por uso).
   - Ve a **Settings > Billing** (o el icono del engranaje) y añade un método de pago o algo de saldo.

3. **Generar la API Key:**
   - En el menú lateral izquierdo, busca **"API keys"** (suele estar bajo una sección de Dashboard o en las opciones de tu perfil).
   - Haz clic en **"Create new secret key"**.
   - Ponle un nombre (ej. `nurax-backend`).
   - **¡Cópiala inmediatamente!** (No podrás volver a verla entera una vez que cierres la ventana). Debería verse algo como `sk-proj-...`.

---

## Paso 2: Configuración en Django

Ahora prepararemos tu proyecto `nurax_backend` para comunicarse con la API.

### 2.1 Instalar dependencias

Abre tu terminal en la carpeta del backend y activa tu entorno virtual (si tienes uno). Luego instala la librería oficial de OpenAI y `python-dotenv` para manejar tu clave de forma segura.

```bash
pip install openai python-dotenv
```

### 2.2 Configurar variables de entorno

**Nunca** pongas tu API Key directamente en el código fuente. Usa un archivo `.env`.

1. Crea o abre un archivo llamado `.env` en la raíz de tu proyecto Django (al mismo nivel que `manage.py`).
2. Añade tu API Key:

```env
OPENAI_API_KEY=sk-proj-aqui-tu-api-key-secreta
```

### 2.3 Cargar la variable en `settings.py`

En tu archivo de configuración de Django (`nurax_backend/settings.py` o similar), asegúrate de cargar las variables de entorno. Normalmente si estás usando `django-environ` o `python-dotenv` sería algo así:

```python
import os
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

# Guardar la API key en settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

---

## Paso 3: Crear el Servicio de OpenAI

Es una buena práctica crear un archivo dedicado para la lógica de la IA.

1. Dentro de tu aplicación principal (ej. `api`, `core`, etc.), crea un archivo llamado `ai_service.py`.

```python
# ai_service.py
from django.conf import settings
from openai import OpenAI

def get_chatgpt_response(prompt_text):
    # Inicializar el cliente usando la API Key de settings
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        # Llamar al modelo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Puedes usar "gpt-4o" o "gpt-4o-mini"
            messages=[
                # El "system" define la personalidad o el contexto de la IA
                {"role": "system", "content": "Eres un asistente virtual útil y conciso para el sistema Nurax."},
                # El "user" es el mensaje del usuario (el prompt)
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7, # Nivel de creatividad (0 a 1)
        )
        
        # Extraer el texto de la respuesta
        return response.choices[0].message.content
        
    except Exception as e:
        # Manejo básico de errores
        return f"Error al conectar con OpenAI: {str(e)}"
```

---

## Paso 4: Crear la Vista o Endpoint (Django REST Framework)

Ahora creamos una vista que tu frontend en Vue pueda consumir.

### 4.1 La Vista (`views.py`)

Abre el archivo `views.py` de tu app y añade:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ai_service import get_chatgpt_response

class AskAIView(APIView):
    def post(self, request):
        prompt = request.data.get('prompt', '')
        
        if not prompt:
            return Response({"error": "El prompt es requerido"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Llamamos al servicio que creamos
        ai_response = get_chatgpt_response(prompt)
        
        # Retornamos la respuesta al frontend
        return Response({
            "prompt": prompt,
            "response": ai_response
        }, status=status.HTTP_200_OK)
```

### 4.2 La URL (`urls.py`)

No olvides registrar tu vista en tus `urls.py`:

```python
from django.urls import path
from .views import AskAIView

urlpatterns = [
    # Tus otras URLs...
    path('ask-ai/', AskAIView.as_view(), name='ask_ai'),
]
```

---

## Paso 5: Consumo desde Vue (Frontend)

Una vez que tengas el endpoint funcionando en tu backend, desde tu frontend en Vue puedes hacer la petición así:

```javascript
// Ejemplo de llamada usando fetch o axios en Vue
const preguntarA_IA = async () => {
    try {
        const respuesta = await fetch('http://localhost:8000/api/ask-ai/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Asegúrate de enviar tu token de auth (JWT) si la vista está protegida
            },
            body: JSON.stringify({
                prompt: "¿Cuál es el mejor lenguaje para el backend?"
            })
        });
        
        const data = await respuesta.json();
        console.log("Respuesta de la IA:", data.response);
    } catch (error) {
        console.error("Error:", error);
    }
}
```

## Resumen y Recomendaciones Finales

- **No compartas tu API Key** en repositorios públicos (GitHub, etc.). Siempre asegúrate de que `.env` esté en tu `.gitignore`.
- La librería de `openai` cambió mucho a partir de la versión `1.0.0`. Esta guía asume que usas la versión más reciente (ej. `v1.x.x`).
- Considera usar **Celery** o algún mecanismo asíncrono si vas a enviar prompts muy largos, ya que la API de OpenAI a veces puede tardar un par de segundos en responder y bloquear la petición HTTP en Django.
