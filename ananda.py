import streamlit as st
from groq import Groq
import os
import sqlite3
from datetime import datetime
import math
from dotenv import load_dotenv

# 1. CONFIGURACIÓN Y ESTÉTICA
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Ananda: Mentor Akáshico", page_icon="🌙", layout="wide")

# --- CSS CORREGIDO (Seguro para el Sidebar) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    /* Dejamos que el header exista pero que no moleste visualmente */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA LUNAR ---
def get_lunar_phase():
    diff = datetime.now() - datetime(2000, 1, 6)
    days = diff.days + diff.seconds / 86400.0
    lunation = days % 29.530588853
    if lunation < 1.84: return "Nueva 🌑", "Ideal para intencionar y sembrar semillas de luz."
    elif lunation < 5.53: return "Creciente 🌒", "Momento de dar los primeros pasos."
    elif lunation < 9.22: return "Cuarto Creciente 🌓", "Energía de acción y superación."
    elif lunation < 12.91: return "Gibosa Creciente 🌔", "Perfeccionamiento y gestación."
    elif lunation < 16.61: return "Llena 🌕", "Culminación y claridad total."
    elif lunation < 20.30: return "Gibosa Menguante 🌖", "Compartir y reflexionar."
    elif lunation < 23.99: return "Cuarto Menguante 🌗", "Soltar y liberar lo viejo."
    elif lunation < 27.68: return "Vinculante 🌘", "Descanso y preparación."
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

# 2. PANEL LATERAL (SIDEBAR)
action_prompt = None

with st.sidebar:
    st.title("🌙 Oráculo Lunar")
    st.info(f"**Luna Actual:** {luna_nombre}\n\n*{luna_consejo}*")
    
    st.subheader("Herramientas Sagradas")
    if st.button("🃏 Tarot del Día", use_container_width=True):
        action_prompt = f"Ananda, bajo esta Luna {luna_nombre}, tirame 3 cartas de tarot simbólicas. ✨"
    if st.button("🕯️ Ritual Lunar", use_container_width=True):
        action_prompt = f"Sugerime un ritual específico para esta fase de Luna {luna_nombre}. 🌿"
    if st.button("🌌 Mensaje Guía", use_container_width=True):
        action_prompt = "Ananda, bajá un mensaje universal para mi alma hoy. ☁️"
    
    st.divider()
    st.subheader("Historial de Registros")
    if st.button("➕ Nueva Consulta", use_container_width=True):
        st.session_state.current_session = create_session()
        st.rerun()
    
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

    # --- BOTÓN CAFECITO ---
    st.divider()
    st.markdown("""
        <div style="text-align: center;">
            <p style="font-size: 0.9em; color: #666;">¿Te sirvió la guía de Ananda? ✨</p>
            <a href="https://cafecito.app/yogaroots" target="_blank">
                <img src="https://cdn.cafecito.app/imgs/buttons/button_5.png" 
                     alt="Invitame un café" 
                     style="width: 150px; border-radius: 10px;">
            </a>
        </div>
    """, unsafe_allow_html=True)

if "current_session" not in st.session_state:
    if sessions: st.session_state.current_session = sessions[0][0]
    else: st.session_state.current_session = create_session()

# 3. INTERFAZ PRINCIPAL
st.title("📖 Ananda: Mentor de Registros")
st.caption(f"Un espacio sagrado bajo la luz de la Luna {luna_nombre} ✨")

chat_history = load_messages(st.session_state.current_session)

for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = action_prompt if action_prompt else st.chat_input("Escribí tu visión o consulta acá...")

if user_input:
    st.chat_message("user").markdown(user_input)
    save_message(st.session_state.current_session, "user", user_input)
    
    if len(chat_history) == 0:
        try:
            client = Groq(api_key=api_key)
            t_gen = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Título corto (3 palabras) para: {user_input}"}],
                max_tokens=10
            )
            update_session_name(st.session_state.current_session, t_gen.choices[0].message.content.strip().replace('"', ''))
        except: pass

    try:
        client = Groq(api_key=api_key)
        system_prompt = {
            "role": "system", 
            "content": f"""Sos Ananda, mentora y oráculo akáshico. 🔮
            Hoy estamos bajo la influencia de la Luna {luna_nombre}. 🌙
            
            DINÁMICA DE CHARLA: Hacé UNA sola pregunta por vez (Entorno -> Cuerpo -> Emoción -> Elementos). 🌿
            
            TONO: Dulce, madura, profesional y muy delicada. Usá emoticones."""
        }
        
        api_messages = [system_prompt] + chat_history + [{"role": "user", "content": user_input}]
        
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
