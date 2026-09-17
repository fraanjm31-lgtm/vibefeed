import streamlit as st
import os
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="NoxVibe", page_icon="⚡", layout="centered")

def get_custom_css(theme):
    if theme == "Modo Claro ☀️":
        bg_color, text_color = "#ffffff", "#0e1117"
    else:
        bg_color, text_color = "#0e1117", "#fafafa"
    return f"""
    <style>
    .main {{ background-color: {bg_color}; color: {text_color}; }}
    .stButton>button {{ width: 100%; border-radius: 20px; font-weight: bold; }}
    .badge-novato {{ background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
    .badge-pro {{ background-color: #8b5cf6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
    .badge-cuantico {{ background-color: #f59e0b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
    </style>
    """

if 'theme' not in st.session_state:
    st.session_state['theme'] = "Modo Oscuro 🌙"

st.markdown(get_custom_css(st.session_state['theme']), unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def init_db():
    # Cambiamos a v2 para forzar una base de datos nueva y limpia
    conn = sqlite3.connect('vibefeed_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, bio TEXT DEFAULT "Creador NoxVibe ⚡", city TEXT DEFAULT "Madrid", lat REAL DEFAULT 40.4168, lon REAL DEFAULT -3.7038, xp INTEGER DEFAULT 100, notif_enabled INTEGER DEFAULT 1)')
    c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, views INTEGER DEFAULT 0, vibe_tag TEXT DEFAULT "General 🌍", is_story INTEGER DEFAULT 0, secret_pin TEXT DEFAULT "", is_duel INTEGER DEFAULT 0, duel_votes_a INTEGER DEFAULT 0, duel_votes_b INTEGER DEFAULT 0, duel_opponent TEXT DEFAULT "", gifts_received TEXT DEFAULT "")')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS challenges (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS agora (id INTEGER PRIMARY KEY AUTOINCREMENT, thought TEXT, constellation TEXT DEFAULT "Filosofía 🌌", timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS algo_votes (user TEXT PRIMARY KEY, preference TEXT)')
    
    # Datos iniciales limpios (sin arroba en el username para evitar duplicados)
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, bio, xp) VALUES (?, ?, ?, ?)", 
                  ("code_ninja", make_hashes("1234"), "Programando apps profesionales desde el móvil. 📱💻", 350))
        c.execute("INSERT INTO users (username, password, bio, xp) VALUES (?, ?, ?, ?)", 
                  ("creator_pro", make_hashes("1234"), "¡Bienvenidos a la nueva era de VibeFeed!", 210))
        
    c.execute("SELECT COUNT(*) FROM posts")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO posts (user, caption, likes, vibe_tag, gifts_received) VALUES (?, ?, ?, ?, ?)",
                  ("code_ninja", "¡Bienvenidos a NoxVibe! La red social del futuro construida 100% desde el móvil ⚡", 42, "Tecnología 💻", "🌟 Estrellas ☕ Café"))
        c.execute("INSERT INTO posts (user, caption, likes, vibe_tag, gifts_received) VALUES (?, ?, ?, ?, ?)",
                  ("creator_pro", "Probando las nuevas funciones de diseño y rangos dinámicos. ¡Esto va a otro nivel! 🚀", 19, "General 🌍", "💎 Gema"))

    c.execute("SELECT COUNT(*) FROM challenges")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO challenges (title, description) VALUES (?, ?)", ("Reto #CodeMobile", "Comparte tu avance creando apps desde el móvil."))
        
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ''

def get_badge(xp):
    if xp >= 300: return "⚡ Dios NoxVibe", "badge-cuantico"
    elif xp >= 180: return "🔥 Creador Pro", "badge-pro"
    else: return "🌱 Novato", "badge-novato"

st.title("⚡ NoxVibe")
st.caption("✨ Red social con Regalos XP, Leaderboard y Ajustes Pro.")

with st.sidebar:
    st.subheader("🔐 Acceso NoxVibe")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Usuario (ej: tu_nombre)")
        p_in = st.text_input("Contraseña", type="password")
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta") and u_in and p_in:
                try:
                    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u_in.replace("@", ""), make_hashes(p_in)))
                    conn.commit()
                    st.success("¡Registrado con éxito!")
                except: st.error("El usuario ya existe.")
        else:
            if st.button("Entrar"):
                c.execute("SELECT password FROM users WHERE username = ?", (u_in.replace("@", ""),))
                res = c.fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u_in.replace("@", "")
                    st.rerun()
                else: st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **@{st.session_state['username']}**")
        c.execute("SELECT xp FROM users WHERE username = ?", (st.session_state['username'],))
        xp_val = c.fetchone()[0]
        b_n, b_c = get_badge(xp_val)
        st.metric("XP", xp_val)
        st.markdown(f"Rango: <span class='{b_c}'>{b_n}</span>", unsafe_allow_html=True)
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()
            
    st.markdown("---")
    st.subheader("🧭 Menú Principal")
    menu_option = st.selectbox("Sección:", [
        "📱 Feed", "➕ Subir Contenido", "🏆 Leaderboard", "🗳️ AlgoDemocracia", 
        "⚔️ VibeDuels", "🌌 Ágora IA", "🔐 Cápsulas PIN", "⏳ Historias", 
        "🌍 VibeMap", "🎯 Desafíos", "🔍 Buscar", "# Tags", "💬 Chats", 
        "🔔 Avisos", "👤 Perfil", "⚙️ Ajustes"
    ])

if menu_option == "📱 Feed":
    st.subheader("Feed de la Comunidad")
    c.execute("SELECT id, user, caption, file, file_type, likes, views, vibe_tag, secret_pin, gifts_received FROM posts WHERE is_story = 0 AND is_duel = 0 ORDER BY id DESC")
    for post in c.fetchall():
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag, secret_pin, gifts_received = post
        c.execute("SELECT xp FROM users WHERE username = ?", (user,))
        user_xp_row = c.fetchone()
        p_xp = user_xp_row[0] if user_xp_row else 100
        b_n, b_c = get_badge(p_xp)
        
        with st.container():
            # Aquí corregimos para que solo salga una arroba limpia
            st.markdown(f"### **@{user}** <span class='{b_c}'>{b_n}</span>  `{vibe_tag}`", unsafe_allow_html=True)
            st.write(caption)
            if file_path and os.path.exists(file_path):
                if "video" in file_type: st.video(file_path)
                elif "image" in file_type: st.image(file_path, use_container_width=True)
            st.caption(f"❤️ {likes} likes {f'| {gifts_received}' if gifts_received else ''}")
            if st.button("❤️ Like", key=f"l_{post_id}"):
                c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                conn.commit()
                st.rerun()
            st.markdown("---")

elif menu_option == "➕ Subir Contenido":
    st.subheader("➕ Subir Contenido")
    if st.session_state['logged_in']:
        with st.form("up_form", clear_on_submit=True):
            cap = st.text_input("Descripción...")
            media = st.file_uploader("Multimedia", type=["mp4", "mov", "jpg", "jpeg", "png"])
            if st.form_submit_button("Publicar") and cap:
                path, f_type = None, "default"
                if media is not None:
                    os.makedirs("uploads", exist_ok=True)
                    path = os.path.join("uploads", media.name)
                    with open(path, "wb") as f: f.write(media.getbuffer())
                    f_type = media.type
                c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, 1)", (st.session_state['username'], cap, path, f_type))
                c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (st.session_state['username'],))
                conn.commit()
                st.success("¡Publicado! +10 XP ⚡")
                st.rerun()
    else: st.warning("Inicia sesión para subir contenido.")

elif menu_option == "🏆 Leaderboard":
    st.subheader("🏆 Salón de la Fama")
    c.execute("SELECT username, xp, bio FROM users ORDER BY xp DESC LIMIT 10")
    for idx, (l_user, l_xp, l_bio) in enumerate(c.fetchall()):
        b_n, b_c = get_badge(l_xp)
        st.markdown(f"### #{idx+1} @{l_user} <span class='{b_c}'>{b_n}</span>", unsafe_allow_html=True)
        st.write(f"*{l_bio}* - XP: **{l_xp}**")
        st.markdown("---")

elif menu_option == "👤 Perfil":
    st.subheader("👤 Perfil")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (cur,))
        u_info = c.fetchone()
        b_n, b_c = get_badge(u_info[2])
        st.metric("Puntos XP", u_info[2])
        st.markdown(f"Insignia: <span class='{b_c}'>{b_n}</span>", unsafe_allow_html=True)
        with st.form("p_up"):
            nb = st.text_area("Bio", value=u_info[0])
            if st.form_submit_button("Guardar"):
                c.execute("UPDATE users SET bio = ? WHERE username = ?", (nb, cur))
                conn.commit()
                st.success("¡Guardado!")
                st.rerun()
    else: st.warning("Inicia sesión.")

else:
    st.subheader(f"Sección: {menu_option}")
    st.info("Sección activa y lista para usar.")
    
