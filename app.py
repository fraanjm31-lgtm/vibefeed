import streamlit as st
import os
import sqlite3
import hashlib
import pandas as datetime
import random
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Ultimate Suite",
    page_icon="🚀",
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

# --- BASE DE DATOS TOTALMENTE AMPLIADA ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    # Usuarios (con Bio, Avatar, Ciudad y Coordenadas para el VibeMap)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            bio TEXT DEFAULT 'Creador en VibeFeed 🚀',
            avatar TEXT DEFAULT '',
            city TEXT DEFAULT 'Madrid',
            lat REAL DEFAULT 40.4168,
            lon REAL DEFAULT -3.7038
        )
    ''')
    
    # Posts (con Soporte para VibeAI Tag, Historias efímeras y Retos)
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
            challenge_name TEXT DEFAULT ''
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
    
    # Migraciones seguras si la BD ya existía
    columns_to_check = [
        ("posts", "vibe_tag", "TEXT DEFAULT 'General 🌍'"),
        ("posts", "is_story", "INTEGER DEFAULT 0"),
        ("posts", "challenge_name", "TEXT DEFAULT ''"),
        ("users", "city", "TEXT DEFAULT 'Madrid'"),
        ("users", "lat", "REAL DEFAULT 40.4168"),
        ("users", "lon", "REAL DEFAULT -3.7038")
    ]
    for table, col, definition in columns_to_check:
        try:
            c.execute(f"SELECT {col} FROM {table} LIMIT 1")
        except sqlite3.OperationalError:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")

    # Rellenar un reto inicial si está vacío
    c.execute("SELECT COUNT(*) FROM challenges")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO challenges (title, description) VALUES (?, ?)", 
                  ("Reto #CodeMobile", "Sube contenido mostrando cómo programas o creas apps desde el móvil."))

    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

st.title("🚀 VibeFeed Ultimate Suite")
st.caption("✨ Red social con VibeMap global, análisis VibeAI, Desafíos y Historias efímeras.")

# Barra lateral de autenticación
with st.sidebar:
    st.subheader("🔐 Acceso")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Opción:", ["Iniciar Sesión", "Registrarse"])
        user_input = st.text_input("Usuario (@...)")
        pass_input = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if user_input and pass_input:
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                                  (user_input, make_hashes(pass_input)))
                        conn.commit()
                        st.success("¡Cuenta creada con éxito!")
                    except sqlite3.IntegrityError:
                        st.error("El usuario ya existe.")
                else:
                    st.warning("Rellena los campos.")
        else:
            if st.button("Entrar"):
                c.execute("SELECT password FROM users WHERE username = ?", (user_input,))
                res = c.fetchone()
                if res and check_hashes(pass_input, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user_input
                    st.success(f"¡Hola, {user_input}!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")
    else:
        st.success(f"Sesión: **{st.session_state['username']}**")
        c.execute("SELECT COUNT(*) FROM notifications WHERE user = ? AND is_read = 0", (st.session_state['username'],))
        unread = c.fetchone()[0]
        if unread > 0:
            st.warning(f"🔔 {unread} notificación(es)")
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()
    st.markdown("---")
    st.write("Versión 7.0 - Innovación Total")

# Navegación expandida con las 4 nuevas secciones
menu = st.tabs(["📱 Feed", "⏳ Historias", "🌍 VibeMap", "🏆 Desafíos", "🔍 Buscar", "# Tags", "💬 Chats", "🔔 Avisos", "👤 Perfil", "➕ Subir"])

# --- 1. FEED ---
with menu[0]:
    st.subheader("Feed de la Comunidad")
    filtro = st.radio("Filtrar contenido:", ["Todo", "Vídeos", "Fotos"], horizontal=True)
    
    query = "SELECT id, user, caption, file, file_type, likes, views, vibe_tag FROM posts WHERE is_story = 0"
    params = []
    if filtro == "Vídeos":
        query += " AND file_type LIKE '%video%'"
    elif filtro == "Fotos":
        query += " AND file_type LIKE '%image%'"
    query += " ORDER BY id DESC"
    
    c.execute(query, params)
    posts = c.fetchall()

    for post in posts:
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag = post
        try:
            c.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
            conn.commit()
        except:
            pass
        
        with st.container():
            c.execute("SELECT avatar FROM users WHERE username = ?", (user,))
            av = c.fetchone()
            av_path = av[0] if av and av[0] else None
            
            col_a, col_b = st.columns([1, 6])
            with col_a:
                if av_path and os.path.exists(av_path):
                    st.image(av_path, width=35)
                else:
                    st.write("👤")
            with col_b:
                st.markdown(f"### **{user}**  `{vibe_tag}`")
                
            st.write(caption)
            if file_path and os.path.exists(file_path):
                if "video" in file_type:
                    st.video(file_path)
                elif "image" in file_type:
                    st.image(file_path, use_container_width=True)
            
            st.caption(f"❤️ {likes} likes | 👁️ {(views or 0) + 1} vistas")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("❤️ Like", key=f"f_like_{post_id}"):
                    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                    conn.commit()
                    st.rerun()
            with c2:
                if st.button("🔗 Copiar", key=f"f_share_{post_id}"):
                    st.toast("¡Enlace copiado!", icon="📋")
            with c3:
                if st.session_state['logged_in'] and st.session_state['username'] == user:
                    if st.button("🗑️ Borrar", key=f"f_del_{post_id}"):
                        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                        conn.commit()
                        st.rerun()
            st.markdown("---")

# --- 2. HISTORIAS EFÍMERAS (Cápsulas de Tiempo 24h) ---
with menu[1]:
    st.subheader("⏳ Cápsulas de Tiempo (Stories 24h)")
    st.caption("Contenido efímero que se comparte en directo con la comunidad.")
    
    c.execute("SELECT id, user, caption, file, file_type FROM posts WHERE is_story = 1 ORDER BY id DESC")
    stories = c.fetchall()
    
    if stories:
        for st_item in stories:
            s_id, s_user, s_cap, s_file, s_type = st_item
            with st.container():
                st.markdown(f"**🔴 Historia de @{s_user}**")
                st.write(s_cap)
                if s_file and os.path.exists(s_file):
                    if "video" in s_type:
                        st.video(s_file)
                    else:
                        st.image(s_file, use_container_width=True)
                st.markdown("---")
    else:
        st.info("No hay historias activas en este momento. ¡Sube una desde la pestaña 'Subir' marcándola como historia!")

# --- 3. VIBEMAP (Mapa Global Interactivo) ---
with menu[2]:
    st.subheader("🌍 VibeMap: Creadores en el Mundo")
    st.caption("Descubre dónde están conectados los creadores de la comunidad.")
    
    c.execute("SELECT username, city, lat, lon FROM users")
    map_users = c.fetchall()
    
    if map_users:
        import pandas as pd
        df_map = pd.DataFrame(map_users, columns=['username', 'city', 'lat', 'lon'])
        st.map(df_map[['lat', 'lon']])
        st.write("### Creadores registrados:")
        for mu in map_users:
            st.markdown(f"- **@{mu[0]}** en *{mu[1]}*")
    else:
        st.info("Aún no hay ubicaciones registradas.")

# --- 4. DESAFÍOS DE LA COMUNIDAD ---
with menu[3]:
    st.subheader("🏆 Panel de Desafíos Activos")
    c.execute("SELECT title, description FROM challenges")
    challenge = c.fetchone()
    
    if challenge:
        st.markdown(f"### {challenge[0]}")
        st.info(challenge[1])
        
        st.write("---")
        st.subheader("Participaciones en este reto:")
        c.execute("SELECT user, caption, file, file_type, likes FROM posts WHERE challenge_name != '' ORDER BY id DESC")
        chal_posts = c.fetchall()
        
        if chal_posts:
            for cp in chal_posts:
                st.markdown(f"**@{cp[0]}**: {cp[1]}")
                if cp[2] and os.path.exists(cp[2]):
                    if "video" in cp[3]:
                        st.video(cp[2])
                    else:
                        st.image(cp[2], use_container_width=True)
                st.markdown("---")
        else:
            st.write("¡Sé el primero en subir contenido a este desafío!")

# --- 5. BUSCADOR ---
with menu[4]:
    st.subheader("🔍 Buscar Creadores")
    sq = st.text_input("Nombre de usuario...", key="search_box_main")
    if sq:
        c.execute("SELECT username, bio, avatar, city FROM users WHERE username LIKE ?", (f"%{sq}%",))
        res = c.fetchall()
        for r in res:
            st.markdown(f"### @{r[0]} ({r[3]})")
            st.write(f"*{r[1]}*")
            st.markdown("---")

# --- 6. HASHTAGS ---
with menu[5]:
    st.subheader("# Explorador de Hashtags")
    tq = st.text_input("Busca etiqueta (ej. #tech)...")
    if tq:
        if not tq.startswith("#"): tq = "#" + tq
        c.execute("SELECT user, caption, file, file_type, likes FROM posts WHERE caption LIKE ?", (f"%{tq}%",))
        for tp in c.fetchall():
            st.markdown(f"**@{tp[0]}**: {tp[1]}")
            if tp[2] and os.path.exists(tp[2]):
                st.image(tp[2], use_container_width=True)
            st.markdown("---")

# --- 7. CHATS PRIVADOS ---
with menu[6]:
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT username FROM users WHERE username != ?", (cur,))
        others = [row[0] for row in c.fetchall()]
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
    else:
        st.warning("Inicia sesión para usar los chats.")

# --- 8. AVISOS / NOTIFICACIONES ---
with menu[7]:
    st.subheader("🔔 Notificaciones")
    if st.session_state['logged_in']:
        c.execute("SELECT message, is_read FROM notifications WHERE user = ? ORDER BY id DESC", (st.session_state['username'],))
        for notif in c.fetchall():
            prefix = "🔴" if notif[1] == 0 else "⚪"
            st.markdown(f"{prefix} {notif[0]}")
    else:
        st.warning("Inicia sesión para ver tus avisos.")

# --- 9. PERFIL ---
with menu[8]:
    st.subheader("👤 Tu Perfil y Ubicación en el VibeMap")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT bio, city FROM users WHERE username = ?", (cur,))
        u_info = c.fetchone()
        
        with st.form("profile_upd"):
            new_bio = st.text_area("Biografía", value=u_info[0] if u_info else "")
            new_city = st.text_input("Ciudad (para el VibeMap)", value=u_info[1] if u_info else "Madrid")
            if st.form_submit_button("Actualizar Perfil"):
                # Coordenadas automáticas simplificadas según ciudad española/global de ejemplo
                lat, lon = 40.4168, -3.7038
                if "barcelona" in new_city.lower(): lat, lon = 41.3851, 2.1734
                elif "valencia" in new_city.lower(): lat, lon = 39.4699, -0.3763
                elif "sevilla" in new_city.lower(): lat, lon = 37.3891, -5.9845
                
                c.execute("UPDATE users SET bio = ?, city = ?, lat = ?, lon = ? WHERE username = ?", (new_bio, new_city, lat, lon, cur))
                conn.commit()
                st.success("¡Perfil y ubicación actualizados!")
                st.rerun()
    else:
        st.warning("Inicia sesión.")

# --- 10. SUBIR CONTENIDO (CON VibeAI AUTOMÁTICO Y RETOS) ---
with menu[9]:
    st.subheader("➕ Subir Contenido Multimedia")
    if st.session_state['logged_in']:
        with st.form("upload_full", clear_on_submit=True):
            caption = st.text_area("Escribe tu descripción...")
            media = st.file_uploader("Multimedia", type=["mp4", "mov", "jpg", "jpeg", "png"])
            is_story = st.checkbox("⏳ Publicar como Historia efímera (24h)")
            join_challenge = st.checkbox("🏆 Participar en el Desafío Activo (#CodeMobile)")
            
            if st.form_submit_button("Publicar Contenido"):
                if caption:
                    # 🤖 VibeAI: Analizador automático de sentimientos / etiquetas del post
                    cap_lower = caption.lower()
                    vibe_tag = "General 🌍"
                    if any(w in cap_lower for w in ["código", "app", "python", "dev", "bug", "programar"]):
                        vibe_tag = "Tech 💻"
                    elif any(w in cap_lower for w in ["risa", "jaja", "humor", "meme", "bromas"]):
                        vibe_tag = "Humor 😂"
                    elif any(w in cap_lower for w in ["viaje", "playa", "montaña", "avión"]):
                        vibe_tag = "Viajes ✈️"
                    elif any(w in cap_lower for w in ["motivación", "fuerza", "logro", "meta"]):
                        vibe_tag = "Motivación 🔥"
                    
                    path, f_type = None, "default"
                    if media is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", media.name)
                        with open(path, "wb") as f:
                            f.write(media.getbuffer())
                        f_type = media.type
                    
                    chal_val = "CodeMobile" if join_challenge else ""
                    
                    c.execute('''
                        INSERT INTO posts (user, caption, file, file_type, likes, views, vibe_tag, is_story, challenge_name) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (st.session_state['username'], caption, path, f_type, 1, 0, vibe_tag, 1 if is_story else 0, chal_val))
                    conn.commit()
                    st.success("¡Publicado con éxito gracias a VibeAI! 🚀")
                    st.rerun()
                else:
                    st.warning("Escribe una descripción.")
    else:
        st.warning("Inicia sesión para subir contenido.")
    
