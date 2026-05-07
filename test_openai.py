import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. Cargar las variables de entorno
load_dotenv()

# 2. Obtener la API key de GROQ
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("[ERROR] No se encontro GROQ_API_KEY en tu archivo .env")
    sys.exit(1)

# 3. Inicializar el cliente apuntando a Groq
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

print("-" * 50)
print("🤖 Boti - Tu Asistente IA (Potenciado por Groq)")
print("Escribe 'salir' para terminar la conversacion.")
print("-" * 50)

# Aquí guardaremos el historial de la conversación para que la IA tenga contexto
historial = [
    {"role": "system", "content": "Eres un asistente de IA muy inteligente, amigable y experto en programación. Responde de forma clara y concisa en español."}
]

# 4. Bucle infinito para poder chatear
while True:
    # Pedimos al usuario que escriba algo
    user_input = input("\n👉 Tú: ")
    
    # Condición para salir del bucle
    if user_input.lower() in ['salir', 'exit', 'quit', 'adiós', 'adios']:
        print("🤖 IA: ¡Nos vemos! ¡Éxito con tu código!")
        break
        
    # Si el usuario no escribió nada, volvemos a preguntar
    if not user_input.strip():
        continue
        
    # Agregamos lo que el usuario escribió al historial
    historial.append({"role": "user", "content": user_input})
    
    try:
        # Llamamos a la API de Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=historial
        )
        
        # Obtenemos la respuesta
        respuesta_ia = response.choices[0].message.content
        
        # Imprimimos la respuesta de la IA
        print("\n🤖 IA: " + respuesta_ia)
        
        # Agregamos la respuesta al historial para que la recuerde en el siguiente mensaje
        historial.append({"role": "assistant", "content": respuesta_ia})
        
    except Exception as e:
        print("\n[ERROR] HUBO UN ERROR AL LLAMAR A LA API:")
        print(str(e))
