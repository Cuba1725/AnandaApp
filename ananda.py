import streamlit as st
from groq import Groq
import os
import sqlite3
from datetime import datetime
import math # Para calcular la fase lunar de forma sencilla
from dotenv import load_dotenv

# 1. CONFIGURACIÓN
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
st.set_page_config(page_title="Ananda: Mentor Akáshico", page_icon="🌙", layout="wide")

# --- LÓGICA LUNAR ---
def get_lunar_phase():
    """Calcula la fase lunar aproximada basada en la fecha actual"""
    # Fecha de referencia: Luna Nueva el 6 de enero de 2000
    diff = datetime.now() - datetime(2000, 1, 6)
    days = diff.days + diff.seconds / 86400.0
    lunation = days % 29.530588853
    
    if lunation < 1.84: return "Nueva 🌑", "Ideal para intencionar y sembrar semillas de luz."
    elif lunation < 5.53: return "Creciente 🌒", "Momento de dar los primeros pasos y nutrir tus proyectos."
    elif lunation < 9.22: return "Cuarto Creciente 🌓", "Energía de acción y superación de obstáculos."
    elif lunation < 12.91: return "Gibosa Creciente 🌔", "Perfeccionamiento y gestación final."
    elif lunation < 16.61: return "Llena 🌕", "Culminación, claridad total y agradecimiento."
    elif lunation < 20.30: return "Gibosa Menguante 🌖", "Compartir frutos y reflexionar sobre lo aprendido."
    elif lunation < 23.99: return "Cuarto Menguante 🌗", "Soltar, perdonar y liberar lo que ya no vibra con vos."
    elif lunation < 27.68: return "Vinculante 🌘", "Descanso profundo y preparación para el nuevo ciclo."
    else: return "Nueva 🌑", "Intenciones puras."

luna_nombre, luna_consejo = get_lunar_phase()

# --- BASE DE DATOS ---
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

def delete_session(session_id):
    conn = sqlite3.connect('ananda_akasha.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
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

init_db()

# 2. PANEL LATERAL
with st.sidebar:
    st.title("📚 Registros")
    # Indicador Lunar Discreto
    st.info(f"**Luna Actual:** {luna_nombre}\n\n*{luna_consejo}*")
    
    if st.button("➕ Nueva Consulta", use_container_width=True):
        st.session_state.current_session = create_session()
        st.rerun()
    st.divider()
    sessions = get_sessions()
    for s_id, s_name in sessions:
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"📖 {s_name}", key=f"s_{s_id}", use_container_width=True):
                st.session_state.current_session = s_id
                st.rerun()
        with cols[1]:
            if st.button("🗑️", key=f"d_{s_id}"):
                delete_session(s_id)
                st.rerun()

if "current_session" not in st.session_state:
    if sessions: st.session_state.current_session = sessions[0][0]
    else: st.session_state.current_session = create_session()

# 3. INTERFAZ DE ANANDA
st.title("📖 Ananda: Oráculo Akáshico")
st.caption(f"Acompañando tu proceso bajo la luz de la Luna {luna_nombre} ✨")

chat_history = load_messages(st.session_state.current_session)

# --- BOTONES DE PODER ---
c1, c2, c3 = st.columns(3)
action_prompt = None

with c1:
    if st.button("🃏 Tarot del Día", use_container_width=True):
        action_prompt = f"Ananda, bajo esta Luna {luna_nombre}, tirame 3 cartas de tarot. ✨"
with c2:
    if st.button("🕯️ Ritual Lunar", use_container_width=True):
        action_prompt = f"Sugerime un ritual específico para esta fase de Luna {luna_nombre}. 🌿"
with c3:
    if st.button("🌌 Mensaje Guía", use_container_width=True):
        action_prompt = "Ananda, bajá un mensaje universal para mi alma hoy. ☁️"

# Mostrar historial
for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de usuario
if prompt := (action_prompt if action_prompt else st.chat_input("Escribí tu consulta acá...")):
    st.chat_message("user").markdown(prompt)
    save_message(st.session_state.current_session, "user", prompt)
    
    # Título automático
    if len(chat_history) == 0:
        try:
            client = Groq(api_key=api_key)
            t_gen = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Título corto para: {prompt}"}],
                max_tokens=10
            )
            update_session_name(st.session_state.current_session, t_gen.choices[0].message.content.strip())
        except: pass

    # CEREBRO DE ANANDA LUNAR
    try:
        client = Groq(api_key=api_key)
        system_prompt = {
            "role": "system", 
            "content": f"""Sos Ananda, mentora y oráculo akáshico. 🔮
            Hoy estamos bajo la influencia de la Luna {luna_nombre}. 🌙
            
            REGLAS LUNARES:
            - Si te piden un RITUAL, debe estar alineado con la fase {luna_nombre}.
            - Si te piden TAROT, integrá el significado de la luna en la lectura.
            - Si traen una VISIÓN de registros, usá el protocolo de 4 preguntas (una por una).
            
            TONO: Dulce, maduro, poético y profesional. Voseo natural. Usá emoticones delicados. ✨🌿"""
        }
        
        api_messages = [system_prompt] + chat_history + [{"role": "user", "content": prompt}]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            temperature=0.7
        )
        
        ans = response.choices[0].message.content
        st.chat_message("assistant").markdown(ans)
        save_message(st.session_state.current_session, "assistant", ans)
        st.rerun()

    except Exception as e:
        st.error(f"Se cortó la conexión: {e}")
