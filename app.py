import streamlit as st
import sqlite3
import os
from datetime import datetime, date

st.set_page_config(page_title="NoxVibe", page_icon="🧭", layout="centered")

conn = sqlite3.connect('noxvibe.db', check_same_thread=False)
c = conn.cursor()

# Creación de tablas básicas y columnas de seguridad
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, xp INTEGER, bio TEXT, avatar TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, vibe_tag TEXT, timestamp TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS post_reactions (post_id INTEGER, username TEXT, reaction_type TEXT)''')

for col, definition in [
    ("email", "TEXT"),
    ("theme", "TEXT DEFAULT 'Oscuro'"),
    ("account_privacy", "TEXT DEFAULT 'Publico'"),
    ("coins", "INTEGER DEFAULT 100")
]:
    try:
        c.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
    except:
        pass

for col, definition in [
    ("fires", "INTEGER DEFAULT 0"),
    ("thumbs", "INTEGER DEFAULT 0"),
    ("hearts", "INTEGER DEFAULT 0"),
    ("privacy", "TEXT DEFAULT 'Publico'")
]:
    try:
        c.execute(f"ALTER TABLE posts ADD COLUMN {col} {definition}")
    except:
        pass

conn.commit()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.profile_tab = "Fotos"
    st.session_state.theme = "Oscuro"

if st.session_state.logged_in and st.session_state.username:
    c.execute("SELECT theme FROM users WHERE username = ?", (st.session_state.username,))
    res_theme = c.fetchone()
    if res_theme and res_theme[0]:
        st.session_state.theme = res_theme[0]

# Estilos visuales
bg_color = "#0e1117" if st.session_state.theme != "Claro" else "#ffffff"
text_color = "#ffffff" if st.session_state.theme != "Claro" else "#000000"
box_bg = "#161b22" if st.session_state.theme != "Claro" else "#f0f2f6"
sub_text = "#8b949e" if st.session_state.theme != "Claro" else "#555555"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    div.stButton > button {{ background-color: {box_bg} !important; color: {text_color} !important; border: 1px solid {sub_text} !important; }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🧭 Menu NoxVibe")
menu_option = st.sidebar.radio("Navegacion", ["🔥 Feed de Videos", "👤 Mi Perfil", "⚙️ Ajustes"])

if st.session_state.logged_in:
    if st.sidebar.button("Cerrar Sesion"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

if not st.session_state.logged_in:
    st.title("Bienvenido a NoxVibe 🚀")
    u = st.text_input("Usuario")
    p = st.text_input("Contrasena", type="password")
    if st.button("Entrar"):
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u, p))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Datos incorrectos")
else:
    cur = st.session_state.username
    
    if menu_option == "⚙️ Ajustes":
        st.title("⚙️ Ajustes de la cuenta")
        
        c.execute("SELECT bio, account_privacy, theme FROM users WHERE username = ?", (cur,))
        u_settings = c.fetchone()
        current_bio = u_settings[0] if u_settings and u_settings[0] else ""
        current_acc_priv = u_settings[1] if u_settings and u_settings[1] else "Publico"
        current_db_theme = u_settings[2] if u_settings and u_settings[2] else "Oscuro"
        
        with st.form("settings_form"):
            new_bio = st.text_area("Actualizar tu biografia", value=current_bio)
            priv_choice = st.selectbox("Privacidad del Perfil", ["Publico", "Privado"], index=0 if current_acc_priv == "Publico" else 1)
            new_theme = st.selectbox("🎨 Tema de Colores", ["Oscuro", "Claro", "Neon / Cyber"], index=0)
            
            submitted = st.form_submit_button("Guardar cambios")
            
        if submitted:
            c.execute("UPDATE users SET bio = ?, account_privacy = ?, theme = ? WHERE username = ?", (new_bio, priv_choice, new_theme, cur))
            conn.commit()
            st.session_state.theme = new_theme
            st.success("¡Ajustes guardados correctamente!")
            st.rerun()
            
