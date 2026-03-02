import streamlit as st
from groq import Groq
import os
import sqlite3
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
    sessions = c.fetchall()
    conn.close()
    return sessions

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
    if sessions:
        st.session_state.current_session = sessions[0][0]
    else:
        st.session_state.current_session = create_session()

chat_history = load_messages(st.session_state.current_session)

# SYSTEM PROMPT AJUSTADO AL "PUNTO MEDIO"
system_prompt = {
    "role": "system", 
    "content": """Sos Ananda, mentora en Registros Akáshicos. 
    Tu objetivo es ayudar a interpretar visiones de forma responsable.
    
    PROTOCOLO DE RESPUESTA:
    1. INDAGACIÓN: Ante una visión nueva, debés hacer exactamente 4 preguntas clave (entorno, sensaciones, otros elementos, contexto emocional).
    2. DEVOLUCIÓN: Una vez que el usuario responda, ofrecé una interpretación integradora. 
    3. VALIDACIÓN: Al final de tu devolución, preguntá siempre si esto le hace sentido o resuena con lo que sintió en el registro.
    
    TONO: Hablás de 'vos' natural. Sos madura, serena y concisa (máximo 2 párrafos)."""
}

st.title("📖 Ananda: Mentor de Registros")

for msg in chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("¿Qué bajó en el registro?"):
    st.chat_message("user").write(prompt)
    save_message(st.session_state.current_session, "user", prompt)
    
    # 4. GENERACIÓN DE TÍTULO AUTOMÁTICO (Si es el primer mensaje)
    if len(chat_history) == 0:
        try:
            client = Groq(api_key=api_key)
            title_gen = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Generá un título de 3 palabras para esta consulta akáshica: {prompt}"}],
                max_tokens=10
            )
            nuevo_titulo = title_gen.choices[0].message.content.replace('"', '')
            update_session_name(st.session_state.current_session, nuevo_titulo)
        except:
            pass

    # RESPUESTA DE ANANDA
    api_messages = [system_prompt] + chat_history + [{"role": "user", "content": prompt}]
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            temperature=0.5,
            max_tokens=500
        )
        ans = response.choices[0].message.content
        st.chat_message("assistant").write(ans)
        save_message(st.session_state.current_session, "assistant", ans)
        if len(chat_history) == 0: st.rerun() # Para actualizar el título en el sidebar
    except:
        st.error("Error de conexión.")
