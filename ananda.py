import streamlit as st
from groq import Groq
import os
import random
from dotenv import load_dotenv

# 1. CONFIGURACIÓN
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Ananda: Tu Guía Espiritual", page_icon="✨")

# 2. LÓGICA DE NUMEROLOGÍA
def calcular_mision_vida(fecha):
    numeros = [int(d) for d in fecha if d.isdigit()]
    if not numeros: return None
    resultado = sum(numeros)
    while resultado > 9 and resultado not in [11, 22, 33]:
        resultado = sum(int(d) for d in str(resultado))
    return resultado

# 3. PANEL LATERAL (ORÁCULO MÁS SERIO)
with st.sidebar:
    st.title("🔮 Oráculo de Conciencia")
    st.write("Un mensaje para reflexionar en tu presente.")
    
    if st.button("✨ Recibir Mensaje"):
        temas = ["Vínculos", "Propósito", "Energía", "Salud", "Prosperidad", "Miedos", "Creatividad", "Intuición"]
        tema_azar = random.choice(temas)
        
        prompt_oraculo = f"""
        Actuá como una guía espiritual madura y reflexiva. 
        Tema: {tema_azar}. 
        REGLAS:
        - No uses muletillas como 'che', 'mirá', 'ni ahí' o 'copado'.
        - Usá un voseo sutil y natural.
        - Que el tono sea calmo, sabio y breve. 
        - Evitá los clichés adolescentes.
        """
        
        try:
            client = Groq(api_key=api_key)
            resp_oraculo = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_oraculo}],
                temperature=0.7
            )
            st.info(f"**Reflexión sobre {tema_azar}:**")
            st.write(resp_oraculo.choices[0].message.content)
        except Exception as e:
            st.error("No se pudo conectar con el oráculo.")

# 4. CUERPO DEL CHAT (PERSONALIDAD MADURA)
st.title("✨ Ananda: Guía Espiritual")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": """Sos Ananda, una guía mística con una personalidad serena, madura y profesional.
            
            LINEAMIENTOS DE COMUNICACIÓN:
            1. VOSEO NATURAL: Hablás de 'vos' porque es tu naturaleza, pero no lo exagerás. 
            2. PROHIBICIONES: No uses 'ni ahí', 'copado', 'quilombo', 're' o 'che'. Evitá sonar como una adolescente de Palermo.
            3. TONO: Tu lenguaje es elevado pero accesible. Sos empática y escuchás con atención.
            4. SABIDURÍA: Tus respuestas deben invitar a la reflexión. Si alguien está mal, no uses frases hechas; ofrecé una perspectiva equilibrada.
            5. Si te dan una fecha, explicá la Numerología con sobriedad, enfocándote en el aprendizaje de vida."""
        }
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("¿Qué necesitás integrar hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.6,           # Menos temperatura = más coherencia y seriedad
            presence_penalty=0.5,
            frequency_penalty=0.8      # Evita que repita palabras
        )
        
        respuesta = response.choices[0].message.content
        st.chat_message("assistant").write(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
    except Exception as e:
        st.error("Ananda está en silencio por un momento... intentá de nuevo.")

