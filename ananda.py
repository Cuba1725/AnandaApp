import streamlit as st
from groq import Groq
import os
import sqlite3
import base64
from datetime import datetime
from dotenv import load_dotenv

# 1. CONFIGURACIÓN
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
st.set_page_config(page_title="Ananda: Mentor Akáshico", page_icon="📖", layout="wide")

# Gestión de Base de Datos
def init_db():
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, 
                  role TEXT, content TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def update_session_name(session_id, new_name):
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute("UPDATE sessions SET name = ? WHERE id = ?", (new_name, session_id))
    conn.commit()
    conn.close()

def get_sessions():
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM sessions ORDER BY date DESC")
    return c.fetchall()

def create_session(name="Nueva Consulta"):
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions (name, date) VALUES (?, ?)", (name, datetime.now()))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_message(session_id, role, content):
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (session_id, role, content, datetime.now()))
    conn.commit()
    conn.close()

def load_messages(session_id):
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    msgs = c.fetchall()
    conn.close()
    return [{"role": m[0], "content": m[1]} for m in msgs]

# Función para codificar imagen a Base64 (necesario para la IA Vision)
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

init_db()

# 2. PANEL LATERAL
with st.sidebar:
    st.title("📚 Mis Registros")
    if st.button("➕ Nueva Consulta"):
        st.session_state.current_session = create_session()
        st.rerun()
    st.divider()
    sessions = get_sessions()
    for s_id, s_name in sessions:
        if st.button(f"📖 {s_name}", key=f"sess_{s_id}"):
            st.session_state.current_session = s_id
            st.rerun()

# 3. LÓGICA DE SESIÓN
if "current_session" not in st.session_state:
    if sessions: st.session_state.current_session = sessions[0][0]
    else: st.session_state.current_session = create_session()

chat_history = load_messages(st.session_state.current_session)

system_prompt = {
    "role": "system", 
    "content": """Sos Ananda, mentora en Registros Akáshicos experta en decodificación simbólica y visual.
    
    PROTOCOLO DE RESPUESTA:
    1. SI HAY DIBUJO/IMAGEN: Analizá las formas, colores y la disposición de los elementos. Preguntá qué sintió la lectora mientras lo trazaba.
    2. INDAGACIÓN: Ante visiones nuevas, hacé 4 preguntas clave (entorno, sensaciones, otros elementos, contexto emocional).
    3. DEVOLUCIÓN: Ofrecé una interpretación integradora basada en la imagen o el relato.
    4. VALIDACIÓN: Preguntá siempre si la interpretación resuena.
    
    TONO: Voseo natural, madura, serena y concisa (máximo 2 párrafos)."""
}

st.title("📖 Ananda: Mentor de Registros")

# Mostrar mensajes
for msg in chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. ENTRADA DE USUARIO (Texto + Imagen)
with st.container():
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        uploaded_file = st.file_uploader("🖼️ Subir dibujo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    with col1:
        prompt = st.chat_input("¿Qué bajó en el registro?")

if prompt or uploaded_file:
    full_prompt = prompt if prompt else "Te comparto este dibujo de mi sesión, ¿qué podés percibir?"
    st.chat_message("user").write(full_prompt)
    if uploaded_file:
        st.image(uploaded_file, width=300)
    
    save_message(st.session_state.current_session, "user", full_prompt)
    
    # Generar Título si es el inicio
    if len(chat_history) == 0:
        try:
            client = Groq(api_key=api_key)
            title_gen = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Título de 3 palabras para: {full_prompt}"}],
                max_tokens=10
            )
            update_session_name(st.session_state.current_session, title_gen.choices[0].message.content.strip().replace('"', ''))
        except: pass

    # Respuesta con Visión si hay imagen
    try:
        client = Groq(api_key=api_key)
        if uploaded_file:
            # Usamos el modelo Vision de Llama
            base64_image = encode_image(uploaded_file)
            messages = [
                system_prompt,
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
            # Nota: Usamos llama-3.2-11b-vision-preview para procesamiento de imágenes
            model_to_use = "llama-3.2-11b-vision-preview"
        else:
            messages = [system_prompt] + chat_history + [{"role": "user", "content": full_prompt}]
            model_to_use = "llama-3.3-70b-versatile"

        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.5,
            max_tokens=500
        )
        ans = response.choices[0].message.content
        st.chat_message("assistant").write(ans)
        save_message(st.session_state.current_session, "assistant", ans)
        if len(chat_history) == 0: st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
