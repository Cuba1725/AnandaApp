import streamlit as st
from groq import Groq
import os
import random
from dotenv import load_dotenv

# 1. CONFIGURACIÓN INICIAL
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

# 3. PANEL LATERAL (EL ORÁCULO RECARGADO)
with st.sidebar:
    st.title("🔮 Herramientas Místicas")
    st.write("¿Qué te dice el universo hoy?")
    
    if st.button("✨ Sacar Carta del Oráculo"):
        # Temas ampliados para evitar la repetición
        temas = [
            "Amor y Vínculos", "Laburo y Proyectos", "Energía Personal", 
            "Salud y Cuerpo", "Abundancia", "Miedos y Trabas", 
            "Creatividad", "Familia", "Viajes e Ideas", "Intuición", "Yoga y Meditación"
        ]
        tema_azar = random.choice(temas)
        
        prompt_oraculo = f"""
        Sos un oráculo místico, directo y con mucha onda porteña. 
        Tema: {tema_azar}. 
        REGLAS:
        - PROHIBIDO: 'Mirá', 'Che', 'Susurros', 'Chispas divinas', 'Armonía'. 
        - Tirame una posta real, algo que pueda hacer hoy. 
        - Usá voseo argentino, pero sin sonar repetitivo.
        - Máximo 2 o 3 frases cortas. Que se note que tenés personalidad.
        """
        
        try:
            client = Groq(api_key=api_key)
            resp_oraculo = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_oraculo}],
                temperature=1.0 # Más variedad
            )
            
            st.success(f"**Sobre tu {tema_azar}:**")
            st.write(resp_oraculo.choices[0].message.content)
        except Exception as e:
            st.error("Se cortó la conexión mística... revisá tu conexión.")

# 4. CUERPO DEL CHAT (PERSONALIDAD ANTI-ROBOT)
st.title("✨ Ananda: Guía Espiritual")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": """Sos Ananda, una guía espiritual de Buenos Aires, canchera y directa. 
            REGLAS DE ORO:
            1. VARIÁ EL COMIENZO: No empieces mensajes con 'Mirá' o 'Che'. Si ya usaste uno, cambiá radicalmente.
            2. LENGUAJE REAL: Usá 'un toque', 're', 'posta', 'ni ahí', 'quilombo', 'copado'. 
            3. MENOS POESÍA, MÁS POSTA: Si alguien está mal, no le digas 'fluye con el cosmos', decile 'es un bajón, pero tratá de encararlo por este lado'.
            4. Si te pasan una fecha, calculá la misión de vida (numerología) y explicala sin vueltas."""
        }
    ]

# Mostrar historial
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# Entrada de usuario
if prompt := st.chat_input("¿En qué te puedo ayudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=1.0,           # Creatividad a tope
            presence_penalty=1.0,      # Obliga a cambiar de tema/palabras
            frequency_penalty=1.0      # Penaliza si repite palabras (como 'Mira')
        )
        
        respuesta = response.choices[0].message.content
        st.chat_message("assistant").write(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
    except Exception as e:
        st.error("Ananda está meditando... intentá de nuevo en un toque.")