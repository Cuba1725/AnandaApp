import streamlit as st
from groq import Groq
import os
import random
from dotenv import load_dotenv

# 1. CONFIGURACIÓN E HISTORIAL
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Ananda: Mentora Akáshico", page_icon="📖")

# Inicializamos el historial si no existe
# --- ACTUALIZACIÓN DEL SYSTEM PROMPT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": """Sos Ananda, mentora experta en Registros Akáshicos. Tu función es acompañar a lectoras a profundizar en sus propias canalizaciones.

            MÉTODO DE TRABAJO (INDAGACIÓN):
            1. No des interpretaciones cerradas de entrada. Si el usuario te trae un símbolo o visión aislada (ej: "un pájaro azul"), tu prioridad es hacer preguntas de contexto.
            2. PREGUNTAS CLAVE: Preguntá sobre el entorno de la visión, sensaciones corporales, emociones presentes, o si hubo otros elementos (colores, sonidos, presencias).
            3. CO-CREACIÓN: Ayudá a que la lectora encuentre el significado por sí misma antes de proponer vos una decodificación metafísica.
            
            PERSONALIDAD:
            - Hablás de 'vos' de forma natural y profesional.
            - Sos serena, madura y evitás el lenguaje informal exagerado.
            - Tu objetivo es la claridad y el anclaje del mensaje.
            
            REGLA DE RESPUESTA:
            - Ante mensajes cortos o ambiguos, respondé siempre con 2 o 3 preguntas inquisitivas para abrir el registro antes de concluir algo."""
        }
    ]

# 2. PANEL LATERAL
with st.sidebar:
    st.title("📖 Herramientas del Lector")
    
    if st.button("✨ Oráculo de Frecuencia"):
        temas = ["Claridad", "Sutileza", "Anclaje", "Discernimiento", "Entrega"]
        tema_azar = random.choice(temas)
        prompt_or = f"Como mentora akáshica, da un consejo breve sobre: {tema_azar}. Usá voseo maduro, máximo 30 palabras."
        
        try:
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_or}],
                temperature=0.6,
                max_tokens=80
            )
            st.info(f"**{tema_azar}:**")
            st.write(resp.choices[0].message.content)
        except:
            st.error("Error de conexión.")
    
    st.divider()
    if st.button("🗑️ Borrar Sesión Actual"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# 3. INTERFAZ DE CHAT
st.title("📖 Ananda: Mentora de Registros")
st.caption("Escribí las visiones o mensajes que recibiste para que te ayude a decodificarlos.")

# Mostrar historial
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Qué mensaje bajó hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.6, 
            max_tokens=400, # Límite de palabras para evitar que sea larguera
            presence_penalty=0.5,
            frequency_penalty=0.8
        )
        
        respuesta = response.choices[0].message.content
        st.chat_message("assistant").write(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
    except Exception as e:
        st.error("Ananda está en silencio...")
