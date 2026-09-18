import streamlit as st
import sqlite3
import os
from datetime import datetime
import hashlib

# Configuración inicial de la página
st.set_page_config(page_title="NoxVibe", page_icon="⚡", layout="centered")

# Funciones de hashing para contraseñas
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashlib.sha256(str.encode(password)).hexdigest()
    return False

# Inicializar base de datos
conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        bio TEXT DEFAULT 'Hola, uso NoxVibe.',
        city TEXT DEFAULT 'Madrid',
        xp INTEGER DEFAULT 0,
        profile_pic TEXT DEFAULT ''
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        caption TEXT,
        file TEXT,
        file_type TEXT,
        likes INTEGER DEFAULT 0,
        vibe_tag TEXT
    )
''')

# Bloques de seguridad para actualizar bases de datos antiguas sin perder datos
try:
    c.execute("ALTER TABLE posts ADD COLUMN vibe_tag TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    c.execute("ALTER TABLE posts ADD COLUMN likes INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass

c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS follows (
        follower TEXT,
        followed TEXT
    )
''')
conn.commit()

# Estado de sesión por defecto
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Modo Oscuro 🌙'
if 'viewing_user' not in st.session_state:
    st.session_state['viewing_user'] = ''
if 'active_tab_idx' not in st.session_state:
    st.session_state['active_tab_idx'] = 0

# Función para insignias XP
def get_badge(xp):
    if xp >= 300:
        return "🔥 Creador Pro", "badge-pro"
    else:
        return "🌱 Novato", "badge-novato"

st.title("⚡ NoxVibe")
st.caption("✨ Red social completa con XP, Canales y Perfiles.")

# Barra lateral de autenticación y perfil
with st.sidebar:
    st.subheader("🔑 Acceso NoxVibe")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Apodo / Usuario")
        p_in = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if u_in and p_in:
                    clean_user = u_in.strip().replace("@", "")
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (clean_user, make_hashes(p_in)))
                        conn.commit()
                        st.success("¡Registrado con éxito!")
                    except sqlite3.IntegrityError:
                        st.error("Ese apodo ya está en uso.")
                else:
                    st.warning("Rellena todos los campos.")
        else:
            if st.button("Entrar"):
                clean_user = u_in.strip().replace("@", "")
                res = c.execute("SELECT password FROM users WHERE username = ?", (clean_user,)).fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = clean_user
                    st.success(f"¡Bienvenido, @{clean_user}!")
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **@{st.session_state['username']}**")
        u_data = c.execute("SELECT xp, profile_pic FROM users WHERE username = ?", (st.session_state['username'],)).fetchone()
        xp_val = u_data[0]
        u_pic = u_data[1]
        
        if u_pic and os.path.exists(u_pic):
            st.image(u_pic, width=80)
            
        badge_name, badge_class = get_badge(xp_val)
        st.metric("Tus Puntos XP", xp_val)
        st.markdown(f"Rango: **{badge_name}**")
        
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown("---")
    st.subheader("💼 Explorar Perfiles")
    search_query = st.text_input("🔍 Escribe el apodo:", placeholder="Ej: Labachito")
    if st.button("Buscar Usuario"):
        clean_q = search_query.strip().replace("@", "")
        exists = c.execute("SELECT 1 FROM users WHERE username = ?", (clean_q,)).fetchone()
        if exists:
            st.session_state['viewing_user'] = clean_q
            st.session_state['active_tab_idx'] = 1
            st.rerun()
        else:
            st.error("Usuario no encontrado.")

# Pestañas principales de la app
tabs = st.tabs([
    "👤 Perfil / Canal", 
    "👥 Siguiendo", 
    "📺 Canal / Perfil", 
    "💬 Mensajes", 
    "⚙️ Ajustes"
])

# 1. Perfil / Canal
with tabs[0]:
    st.subheader("👤 Tu Perfil y Canal")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        u_info = c.execute("SELECT bio, city, xp, profile_pic FROM users WHERE username = ?", (cur,)).fetchone()
        
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            if u_info[3] and os.path.exists(u_info[3]):
                st.image(u_info[3], width=100)
            else:
                st.write("📷 Sin foto")
        with col_p2:
            st.markdown(f"**Bio:** {u_info[0]}")
            st.markdown(f"**Ciudad:** {u_info[1]}")
            st.markdown(f"**XP:** {u_info[2]}")
            
        st.markdown("---")
        st.subheader("📝 Publicar Contenido en tu Canal")
        with st.form("new_post_form", clear_on_submit=True):
            cap = st.text_area("¿Qué estás pensando?")
            tag = st.selectbox("Vibe / Categoría", ["General", "Música", "Tecnología", "Amor", "Viajes"])
            uploaded_file = st.file_uploader("Sube foto o vídeo", type=["jpg", "png", "mp4", "mov"])
            
            if st.form_submit_button("Publicar 🚀"):
                path_to_save = ""
                f_type = ""
                if uploaded_file is not None:
                    os.makedirs("uploads", exist_ok=True)
                    path_to_save = os.path.join("uploads", uploaded_file.name)
                    with open(path_to_save, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    f_type = "video" if uploaded_file.type.startswith("video") else "image"
                
                c.execute("INSERT INTO posts (username, caption, file, file_type, likes, vibe_tag) VALUES (?, ?, ?, ?, ?, ?)",
                          (cur, cap, path_to_save, f_type, 0, tag))
                c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (cur,))
                conn.commit()
                st.success("¡Publicado con éxito! (+10 XP)")
                st.rerun()
    else:
        st.warning("Inicia sesión para gestionar tu perfil y publicar.")

# 2. Siguiendo
with tabs[1]:
    st.subheader("👥 Actividad de Seguidos")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        following = [row[0] for row in c.execute("SELECT followed FROM follows WHERE follower = ?", (cur,)).fetchall()]
        if not following:
            st.info("Aún no sigues a nadie. Busca perfiles en la barra lateral para ver su contenido aquí.")
        else:
            for f_user in following:
                st.markdown(f"### Canal de @{f_user}")
                f_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (f_user,)).fetchall()
                for p in f_posts:
                    st.markdown(f"*Tema: {p[5]}*")
                    if p[1]:
                        st.write(p[1])
                    if p[2] and os.path.exists(p[2]):
                        if p[3] == "video":
                            st.video(p[2])
                        else:
                            st.image(p[2], use_container_width=True)
                    st.markdown("---")
    else:
        st.warning("Inicia sesión para ver la actividad de tus seguidos.")

# 3. Canal / Perfil (Búsqueda externa)
with tabs[2]:
    st.subheader("🔍 Canal y Perfil del Creador")
    target_user = st.session_state.get('viewing_user') or st.session_state.get('username')
    
    if target_user:
        u_data = c.execute("SELECT username, bio, city, xp, profile_pic FROM users WHERE username = ?", (target_user,)).fetchone()
        if u_data:
            b_name, b_class = get_badge(u_data[3])
            col_ping1, col_ping2 = st.columns([1, 2])
            with col_ping1:
                if u_data[4] and os.path.exists(u_data[4]):
                    st.image(u_data[4], width=100)
                else:
                    st.write("📷")
            with col_ping2:
                st.markdown(f"### @{u_data[0]} [{b_name}]")
                st.markdown(f"**Bio:** {u_data[1]} | **Ciudad:** {u_data[2]} | **XP:** {u_data[3]}")
                
                if st.session_state['logged_in'] and st.session_state['username'] != target_user:
                    is_following = c.execute("SELECT 1 FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], target_user)).fetchone()
                    if is_following:
                        if st.button("❌ Dejar de seguir"):
                            c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], target_user))
                            conn.commit()
                            st.rerun()
                    else:
                        if st.button("➕ Seguir"):
                            c.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (st.session_state['username'], target_user))
                            conn.commit()
                            st.rerun()
                            
            st.markdown("---")
            user_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (target_user,)).fetchall()
            if not user_posts:
                st.info("Este usuario aún no ha publicado nada.")
            else:
                for p in user_posts:
                    st.markdown(f"*Tema: {p[5]}*")
                    if p[1]:
                        st.write(p[1])
                    if p[2] and os.path.exists(p[2]):
                        if p[3] == "video":
                            st.video(p[2])
                        else:
                            st.image(p[2], use_container_width=True)
                    st.markdown("---")
        else:
            st.info("Busca un usuario en el menú lateral para ver su perfil.")
    else:
        st.info("Busca un usuario en el menú lateral para ver su perfil.")

# 4. Mensajes Privados
with tabs[3]:
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        
        chat_conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
        chat_c = chat_conn.cursor()
        
        users_list = [u[0] for u in chat_c.execute("SELECT username FROM users WHERE username != ?", (cur,)).fetchall()]
        
        if not users_list:
            st.info("No hay más usuarios registrados.")
        else:
            partner = st.selectbox("Para:", users_list, key="chat_partner_final_definitivo")
            if partner:
                unread_count = chat_c.execute("""
                    SELECT COUNT(*) FROM messages 
                    WHERE sender = ? AND receiver = ?
                """, (partner, cur)).fetchone()[0]
                
                if unread_count > 0:
                    st.markdown(f"🔴 **¡Tienes {unread_count} mensajes de @{partner}!**")

                st.markdown(f"**Chat con @{partner}**")
                
                @st.fragment(run_every=5)
                def mostrar_mensajes_en_tiempo_real():
                    inner_conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
                    inner_c = inner_conn.cursor()
                    
                    msgs = inner_c.execute("""
                        SELECT sender, message, timestamp 
                        FROM messages 
                        WHERE (sender = ? AND receiver = ?) 
                           OR (sender = ? AND receiver = ?) 
                        ORDER BY id ASC
                    """, (cur, partner, partner, cur)).fetchall()
                    
                    inner_conn.close()
                    
                    if not msgs:
                        st.info("No hay mensajes aún. ¡Escribe el primero!")
                    else:
                        for s, m, t in msgs:
                            if s == cur:
                                st.markdown(f"**Tú:** {m} *({t})*")
                            else:
                                st.markdown(f"**@{s}:** {m} *({t})*")

                mostrar_mensajes_en_tiempo_real()
                
                with st.form(key=f"chat_form_final_{partner}", clear_on_submit=True):
                    txt = st.text_input("Escribe tu mensaje...", key="input_msg_final")
                    if st.form_submit_button("Enviar 🚀"):
                        if txt.strip():
                            chat_c.execute(
                                "INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", 
                                (cur, partner, txt.strip(), datetime.now().strftime("%H:%M"))
                            )
                            chat_conn.commit()
                            chat_conn.close()
                            st.rerun()
                            
        chat_conn.close()
    else:
        st.warning("Inicia sesión para chatear.")

# 5. Ajustes
with tabs[4]:
    st.subheader("⚙️ Ajustes")
    sel_theme = st.selectbox("Tema:", ["Modo Oscuro 🌙", "Modo Claro ☀️"], key="settings_theme_final_def")
    if sel_theme != st.session_state['theme']:
        st.session_state['theme'] = sel_theme
        st.rerun()
        
