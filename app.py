import streamlit as st
import os
import sqlite3
import hashlib
import random
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Quantum Edition",
    page_icon="🌌",
    layout="centered"
)

# Estilos CSS avanzados
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- BASE DE DATOS TOTALMENTE REVOLUCIONARIA ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    # Usuarios y XP para Duels
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            bio TEXT DEFAULT 'Creador Cuántico 🌌',
            avatar TEXT DEFAULT '',
            city TEXT DEFAULT 'Madrid',
            lat REAL DEFAULT 40.4168,
            lon REAL DEFAULT -3.7038,
            xp INTEGER DEFAULT 100
        )
    ''')
    
    # Posts con Cápsulas Protegidas y Duelos
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            caption TEXT,
            file TEXT,
            file_type TEXT,
            likes INTEGER,
            views INTEGER DEFAULT 0,
            vibe_tag TEXT DEFAULT 'General 🌍',
            is_story INTEGER DEFAULT 0,
            challenge_name TEXT DEFAULT '',
            secret_pin TEXT DEFAULT '',
            is_duel INTEGER DEFAULT 0,
            duel_votes_a INTEGER DEFAULT 0,
            duel_votes_b INTEGER DEFAULT 0,
            duel_opponent TEXT DEFAULT ''
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user TEXT,
            comment TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS follows (
            follower TEXT,
            followed TEXT,
            PRIMARY KEY (follower, followed)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    ''')
    
    # Ágora / Pensamientos anónimos
    c.execute('''
        CREATE TABLE IF NOT EXISTS agora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thought TEXT,
            constellation TEXT DEFAULT 'Filosofía 🌌',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Algoritmo Democrático Global (Votos de la comunidad)
    c.execute('''
        CREATE TABLE IF NOT EXISTS algo_votes (
            user TEXT PRIMARY KEY,
            preference TEXT
        )
    ''')

    # Migraciones seguras
    cols = [
        ("posts", "secret_pin", "TEXT DEFAULT ''"),
        ("posts", "is_duel", "INTEGER DEFAULT 0"),
        ("posts", "duel_votes_a", "INTEGER DEFAULT 0"),
        ("posts", "duel_votes_b", "INTEGER DEFAULT 0"),
        ("posts", "duel_opponent", "TEXT DEFAULT ''"),
        ("users", "xp", "INTEGER DEFAULT 100")
    ]
    for table, col, defn in cols:
        try:
            c.execute(f"SELECT {col} FROM {table} LIMIT 1")
        except sqlite3.OperationalError:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")

    c.execute("SELECT COUNT(*) FROM challenges")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO challenges (title, description) VALUES (?, ?)", 
                  ("Reto #CodeMobile", "Comparte tu avance creando apps desde el móvil."))

    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

st.title("🌌 VibeFeed Quantum Suite")
st.caption("✨ Red social descentralizada con Cápsulas PIN, Algoritmo Democrático, Duelos y Ágora IA.")

# Sidebar de acceso
with st.sidebar:
    st.subheader("🔐 Acceso Cuántico")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Usuario (@...)")
        p_in = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if u_in and p_in:
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u_in, make_hashes(p_in)))
                        conn.commit()
                        st.success("¡Registrado con éxito!")
                    except sqlite3.IntegrityError:
                        st.error("El usuario ya existe.")
                else:
                    st.warning("Rellena los campos.")
        else:
            if st.button("Entrar"):
                c.execute("SELECT password FROM users WHERE username = ?", (u_in,))
                res = c.fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u_in
                    st.success(f"¡Bienvenido, {u_in}!")
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **{st.session_state['username']}**")
        c.execute("SELECT xp FROM users WHERE username = ?", (st.session_state['username'],))
        xp_val = c.fetchone()[0]
        st.metric("Tus Puntos XP", xp_val)
        
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()
    st.markdown("---")
    st.write("Versión 8.0 - Quantum Matrix")

# Menú expandido con las nuevas funciones exclusivas
menu = st.tabs([
    "📱 Feed", 
    "🗳️ AlgoDemocracia", 
    "⚔️ VibeDuels", 
    "🌌 Ágora IA", 
    "🔐 Cápsulas PIN", 
    "⏳ Historias", 
    "🌍 VibeMap", 
    "🏆 Desafíos", 
    "🔍 Buscar", 
    "# Tags", 
    "💬 Chats", 
    "🔔 Avisos", 
    "👤 Perfil", 
    "➕ Subir"
])

# --- 1. FEED CON ALGORITMO DEMOCRÁTICO ---
with menu[0]:
    st.subheader("Feed de la Comunidad")
    
    pref_query = "SELECT preference FROM algo_votes"
    if st.session_state['logged_in']:
        c.execute("SELECT preference FROM algo_votes WHERE user = ?", (st.session_state['username'],))
        res_p = c.fetchone()
        if res_p: pref_mode = res_p[0]
        else: pref_mode = "Todo"
    else:
        pref_mode = "Todo"
        
    st.caption(f"⚙️ Algoritmo actual en vigor: **{pref_mode}** (votado por la comunidad)")
    
    query = "SELECT id, user, caption, file, file_type, likes, views, vibe_tag, secret_pin FROM posts WHERE is_story = 0 AND is_duel = 0"
    if pref_mode == "Solo Vídeos":
        query += " AND file_type LIKE '%video%'"
    elif pref_mode == "Solo Fotos":
        query += " AND file_type LIKE '%image%'"
    query += " ORDER BY id DESC"
    
    c.execute(query)
    posts = c.fetchall()

    for post in posts:
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag, secret_pin = post
        
        if secret_pin and secret_pin.strip() != "":
            with st.container():
                st.markdown(f"### **{user}** 🔒 *[Cápsula Protegida por PIN]*")
                st.warning("Esta publicación está cifrada con clave secreta.")
                entered_pin = st.text_input(f"Introduce el PIN para abrir post #{post_id}", type="password", key=f"pin_feed_{post_id}")
                if entered_pin == secret_pin:
                    st.success("¡PIN Correcto! Contenido descifrado:")
                    st.write(caption)
                    if file_path and os.path.exists(file_path):
                        if "video" in file_type: st.video(file_path)
                        else: st.image(file_path, use_container_width=True)
                st.markdown("---")
            continue

        with st.container():
            st.markdown(f"### **{user}**  `{vibe_tag}`")
            st.write(caption)
            if file_path and os.path.exists(file_path):
                if "video" in file_type: st.video(file_path)
                elif "image" in file_type: st.image(file_path, use_container_width=True)
            
            if pref_mode != "Modo Sin Likes":
                st.caption(f"❤️ {likes} likes | 👁️ {(views or 0) + 1} vistas")
            else:
                st.caption("🛡️ [Modo Sin Likes Activo por la Comunidad]")
                
            if st.button("❤️ Like", key=f"feed_l_{post_id}"):
                c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                conn.commit()
                st.rerun()
            st.markdown("---")

# --- 2. ALGORITMO SOCIAL DEMOCRÁTICO ---
with menu[1]:
    st.subheader("🗳️ Elige las Reglas del Algoritmo")
    st.caption("A diferencia de Instagram o TikTok, aquí la comunidad vota en tiempo real cómo funciona el sistema de recomendación.")
    
    if st.session_state['logged_in']:
        chosen_pref = st.radio("¿Cómo quieres que se ordene el feed general hoy?", ["Todo", "Solo Vídeos", "Solo Fotos", "Modo Sin Likes"])
        if st.button("Aplicar Voto al Algoritmo"):
            c.execute("INSERT OR REPLACE INTO algo_votes (user, preference) VALUES (?, ?)", (st.session_state['username'], chosen_pref))
            conn.commit()
            st.success("¡Tu voto ha modificado el algoritmo global de VibeFeed!")
            st.rerun()
    else:
        st.warning("Inicia sesión para votar en el algoritmo democrático.")

# --- 3. VIBEDUELS (Batallas 1v1 de Creadores) ---
with menu[2]:
    st.subheader("⚔️ VibeDuels: Batallas 1v1")
    st.caption("Dos creadores compiten cara a cara. Vota por tu favorito y hazle ganar XP.")
    
    c.execute("SELECT id, user, caption, file, file_type, duel_opponent FROM posts WHERE is_duel = 1")
    duels = c.fetchall()
    
    if duels:
        for d in duels:
            d_id, d_user, d_cap, d_file, d_type, d_opp = d
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Retador A: @{d_user}**")
                st.write(d_cap)
                if d_file and os.path.exists(d_file): st.image(d_file, use_container_width=True)
                if st.button(f"Votar por @{d_user}", key=f"vote_a_{d_id}"):
                    c.execute("UPDATE posts SET duel_votes_a = duel_votes_a + 1 WHERE id = ?", (d_id,))
                    c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (d_user,))
                    conn.commit()
                    st.toast("¡Voto registrado para A!", icon="⚔️")
                    st.rerun()
            with col2:
                st.markdown(f"**Retador B: @{d_opp}**")
                st.write("¡Batalla en curso en VibeFeed!")
                if st.button(f"Votar por @{d_opp}", key=f"vote_b_{d_id}"):
                    c.execute("UPDATE posts SET duel_votes_b = duel_votes_b + 1 WHERE id = ?", (d_id,))
                    c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (d_opp,))
                    conn.commit()
                    st.toast("¡Voto registrado para B!", icon="⚔️")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("No hay duelos activos en este momento. ¡Crea un duelo desde la pestaña 'Subir'!")

# --- 4. ÁGORA IA (Pensamientos Anónimos y Constelaciones) ---
with menu[3]:
    st.subheader("🌌 Ágora: Constelaciones de Pensamiento Anónimo")
    st.caption("Un espacio seguro y filosófico donde las ideas de todo el mundo se agrupan por IA.")
    
    if st.session_state['logged_in']:
        with st.form("agora_form", clear_on_submit=True):
            thought_text = st.text_area("Lanza una reflexión al universo anónimo...")
            if st.form_submit_button("Publicar en el Ágora") and thought_text:
                t_lower = thought_text.lower()
                constelacion = "Filosofía 🌌"
                if any(w in t_lower for w in ["código", "tech", "IA", "algoritmo"]): constelacion = "Tecnología y Futuro 💻"
                elif any(w in t_lower for w in ["vida", "tiempo", "sentir", "amor"]): constelacion = "Existencialismo 🧠"
                elif any(w in t_lower for w in ["arte", "música", "crear", "bello"]): constelacion = "Arte y Creación 🎨"
                
                c.execute("INSERT INTO agora (thought, constellation) VALUES (?, ?)", (thought_text, constelacion))
                conn.commit()
                st.success("¡Tu pensamiento ya forma parte de una constelación global!")
                st.rerun()
                
    st.markdown("---")
    c.execute("SELECT thought, constellation, timestamp FROM agora ORDER BY id DESC")
    agoras = c.fetchall()
    if agoras:
        for ag in agoras:
            st.markdown(f"> *\"{ag[0]}\"* \n\n 🏷️ **Constelación:** `{ag[1]}` 🕒 *{ag[2]}*")
            st.markdown("---")
    else:
        st.info("El ágora está en silencio. Sé el primero en dejar tu reflexión.")

# --- 5. CÁPSULAS PIN ---
with menu[4]:
    st.subheader("🔐 Cápsulas de Tiempo Protegidas por PIN")
    st.caption("Introduce un PIN secreto para descifrar publicaciones ocultas de la comunidad.")
    pin_search = st.text_input("Introduce un PIN numérico o clave secreta para buscar cápsulas:")
    if pin_search:
        c.execute("SELECT id, user, caption, file, file_type FROM posts WHERE secret_pin = ?", (pin_search,))
        res_pins = c.fetchall()
        if res_pins:
            for rp in res_pins:
                st.success(f"¡Cápsula descifrada de @{rp[1]}!")
                st.write(rp[2])
                if rp[3] and os.path.exists(rp[3]): st.image(rp[3], use_container_width=True)
        else:
            st.error("Ninguna cápsula coincide con esa clave secreta.")

# --- 6. HISTORIAS EFÍMERAS ---
with menu[5]:
    st.subheader("⏳ Historias Efímeras (24h)")
    c.execute("SELECT user, caption, file, file_type FROM posts WHERE is_story = 1 ORDER BY id DESC")
    for st_item in c.fetchall():
        st.markdown(f"**🔴 Historia de @{st_item[0]}**")
        st.write(st_item[1])
        if st_item[2] and os.path.exists(st_item[2]): st.image(st_item[2], use_container_width=True)
        st.markdown("---")

# --- 7. VIBEMAP ---
with menu[6]:
    st.subheader("🌍 VibeMap Global")
    c.execute("SELECT username, city, lat, lon FROM users")
    map_users = c.fetchall()
    if map_users:
        import pandas as pd
        st.map(pd.DataFrame(map_users, columns=['username', 'city', 'lat', 'lon'])[['lat', 'lon']])
    else:
        st.info("Sin ubicaciones registradas.")

# --- 8. DESAFÍOS ---
with menu[7]:
    st.subheader("🏆 Desafíos Activos")
    c.execute("SELECT title, description FROM challenges")
    chal = c.fetchone()
    if chal:
        st.markdown(f"### {chal[0]}")
        st.info(chal[1])

# --- 9. BUSCAR ---
with menu[8]:
    st.subheader("🔍 Buscar Creadores")
    sq = st.text_input("Usuario...")
    if sq:
        c.execute("SELECT username, bio, city, xp FROM users WHERE username LIKE ?", (f"%{sq}%",))
        for r in c.fetchall():
            st.markdown(f"### @{r[0]} ({r[2]}) - ⚡ XP: {r[3]}")
            st.write(f"*{r[1]}*")
            st.markdown("---")

# --- 10. HASHTAGS ---
with menu[9]:
    st.subheader("# Tags")
    tq = st.text_input("Busca etiqueta...")
    if tq:
        if not tq.startswith("#"): tq = "#" + tq
        c.execute("SELECT user, caption, file FROM posts WHERE caption LIKE ?", (f"%{tq}%",))
        for tp in c.fetchall():
            st.markdown(f"**@{tp[0]}**: {tp[1]}")
            if tp[2] and os.path.exists(tp[2]): st.image(tp[2], use_container_width=True)
            st.markdown("---")

# --- 11. CHATS ---
with menu[10]:
    st.subheader("💬 Chats Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT username FROM users WHERE username != ?", (cur,))
        others = [r[0] for r in c.fetchall()]
        if others:
            dest = st.selectbox("Hablar con:", others)
            c.execute("SELECT sender, message FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)", (cur, dest, dest, cur))
            for msg in c.fetchall():
                st.text(f"@{msg[0]}: {msg[1]}")
            with st.form("dm_f", clear_on_submit=True):
                txt = st.text_input("Mensaje...")
                if st.form_submit_button("Enviar") and txt:
                    c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (cur, dest, txt))
                    conn.commit()
                    st.rerun()

# --- 12. AVISOS ---
with menu[11]:
    st.subheader("🔔 Avisos")
    if st.session_state['logged_in']:
        c.execute("SELECT message, is_read FROM notifications WHERE user = ? ORDER BY id DESC", (st.session_state['username'],))
        for notif in c.fetchall():
            st.markdown(f"{'🔴' if notif[1]==0 else '⚪'} {notif[0]}")

# --- 13. PERFIL ---
with menu[12]:
    st.subheader("👤 Tu Perfil Cuántico")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (cur,))
        u_info = c.fetchone()
        st.metric("Puntos de Experiencia (XP)", u_info[2])
        with st.form("profile_upd"):
            new_bio = st.text_area("Biografía", value=u_info[0])
            new_city = st.text_input("Ciudad", value=u_info[1])
            if st.form_submit_button("Actualizar"):
                lat, lon = 40.4168, -3.7038
                if "barcelona" in new_city.lower(): lat, lon = 41.3851, 2.1734
                elif "valencia" in new_city.lower(): lat, lon = 39.4699, -0.3763
                elif "sevilla" in new_city.lower(): lat, lon = 37.3891, -5.9845
                c.execute("UPDATE users SET bio = ?, city = ?, lat = ?, lon = ? WHERE username = ?", (new_bio, new_city, lat, lon, cur))
                conn.commit()
                st.success("¡Actualizado!")
                st.rerun()

# --- 14. SUBIR CONTENIDO CON OPCIONES CUÁNTICAS ---
with menu[13]:
    st.subheader("➕ Subir Contenido Cuántico")
    if st.session_state['logged_in']:
        with st.form("upload_quantum", clear_on_submit=True):
            caption = st.text_area("Descripción...")
            media = st.file_uploader("Multimedia", type=["mp4", "mov", "jpg", "jpeg", "png"])
            
            st.markdown("---")
            st.write("⚙️ **Opciones Cuánticas Avanzadas:**")
            is_story = st.checkbox("⏳ Historia Efímera (24h)")
            is_duel = st.checkbox("⚔️ Lanzar como VibeDuel 1v1 contra otro usuario")
            c.execute("SELECT username FROM users WHERE username != ?", (st.session_state['username'],))
            opps = [r[0] for r in c.fetchall()]
            duel_opp = st.selectbox("Elige rival para el Duelo", opps) if opps else ""
            secret_pin = st.text_input("🔐 Bloquear con PIN Secreto (Opcional, déjalo vacío si es público)")
            
            if st.form_submit_button("Publicar en la Red Cuántica"):
                if caption:
                 cap_l = captio
    
