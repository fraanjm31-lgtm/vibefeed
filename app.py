import streamlit as st
import os
import sqlite3
import hashlib
import re

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Media Pro",
    page_icon="🎬",
    layout="centered"
)

# Estilos CSS profesionales
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Funciones de encriptación
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- CONFIGURACIÓN DE LA BASE DE DATOS SQLITE (CON TODAS LAS TABLAS) ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    # Usuarios con bio y avatar
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            bio TEXT DEFAULT 'Creador de contenido en VibeFeed 🚀',
            avatar TEXT DEFAULT ''
        )
    ''')
    
    # Posts
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            caption TEXT,
            file TEXT,
            file_type TEXT,
            likes INTEGER,
            views INTEGER DEFAULT 0
        )
    ''')
    
    # Comentarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user TEXT,
            comment TEXT
        )
    ''')
    
    # Seguidores
    c.execute('''
        CREATE TABLE IF NOT EXISTS follows (
            follower TEXT,
            followed TEXT,
            PRIMARY KEY (follower, followed)
        )
    ''')
    
    # Notificaciones
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0
        )
    ''')
    
    # Mensajes Privados (DMs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migraciones / Comprobaciones seguras por si la BD ya existía
    try:
        c.execute("SELECT views FROM posts LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE posts ADD COLUMN views INTEGER DEFAULT 0")
        
    try:
        c.execute("SELECT bio FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT 'Creador de contenido en VibeFeed 🚀'")
        c.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT ''")

    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# Control de sesión en Streamlit
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# Título principal
st.title("🎬 VibeFeed Media Pro")
st.caption("✨ Red social multimedia completa con DMs, Biografías y Notificaciones.")

# Barra lateral para el Login / Registro
with st.sidebar:
    st.subheader("🔐 Acceso de Creador")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Elige opción:", ["Iniciar Sesión", "Registrarse"])
        
        user_input = st.text_input("Usuario (@...)")
        pass_input = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if user_input and pass_input:
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                                  (user_input, make_hashes(pass_input)))
                        conn.commit()
                        st.success("¡Cuenta creada! Ya puedes iniciar sesión.")
                    except sqlite3.IntegrityError:
                        st.error("Ese nombre de usuario ya está cogido.")
                else:
                    st.warning("Rellena todos los campos.")
        else:
            if st.button("Entrar"):
                c.execute("SELECT password FROM users WHERE username = ?", (user_input,))
                result = c.fetchone()
                if result and check_hashes(pass_input, result[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user_input
                    st.success(f"¡Bienvenido de nuevo, {user_input}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
    else:
        st.success(f"Sesión iniciada como:\n**{st.session_state['username']}**")
        
        # Badge de Notificaciones no leídas en la barra lateral
        c.execute("SELECT COUNT(*) FROM notifications WHERE user = ? AND is_read = 0", (st.session_state['username'],))
        unread_count = c.fetchone()[0]
        if unread_count > 0:
            st.warning(f"🔔 Tienes {unread_count} notificación(es) nueva(s)")
            
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown("---")
    st.write("Versión 6.0 - Full Social Suite")

# Menú de navegación superior (Se han añadido la Campanita de Avisos y los DMs)
menu = st.tabs(["📱 Feed", "🔍 Buscar", "# Hashtags", "💬 Chats", "🔔 Avisos", "👤 Mi Perfil", "➕ Subir"])

# --- SECCIÓN 1: EL FEED (Global o Siguiendo) ---
with menu[0]:
    st.subheader("Feed de la Comunidad")
    
    feed_type = "Global"
    if st.session_state['logged_in']:
        feed_mode = st.radio("Mostrar publicaciones de:", ["🌍 Global", "👥 Siguiendo"], horizontal=True)
        if feed_mode == "👥 Siguiendo":
            feed_type = "Following"

    filtro = st.radio("Filtrar por tipo:", ["Todo", "Vídeos", "Fotos"], horizontal=True)
    
    query = "SELECT id, user, caption, file, file_type, likes, views FROM posts"
    params = []
    
    conditions = []
    if feed_type == "Following":
        c.execute("SELECT followed FROM follows WHERE follower = ?", (st.session_state['username'],))
        following_users = [row[0] for row in c.fetchall()]
        if following_users:
            placeholders = ','.join(['?'] * len(following_users))
            conditions.append(f"user IN ({placeholders})")
            params.extend(following_users)
        else:
            conditions.append("1 = 0")
            
    if filtro == "Vídeos":
        conditions.append("file_type LIKE '%video%'")
    elif filtro == "Fotos":
        conditions.append("file_type LIKE '%image%'")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC"
    
    c.execute(query, params)
    posts = c.fetchall()

    if not posts and feed_type == "Following":
        st.info("Aún no sigues a ningún creador o no han publicado nada. ¡Busca perfiles en la pestaña 'Buscar'!")

    for post in posts:
        post_id, user, caption, file_path, file_type, likes, views = post
        
        # Incrementar vistas de forma segura
        try:
            c.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
            conn.commit()
        except sqlite3.OperationalError:
            pass
        
        with st.container():
            # Cargar avatar del creador si existe
            c.execute("SELECT avatar FROM users WHERE username = ?", (user,))
            res_av = c.fetchone()
            avatar_path = res_av[0] if res_av and res_av[0] else None
            
            col_av, col_name = st.columns([1, 6])
            with col_av:
                if avatar_path and os.path.exists(avatar_path):
                    st.image(avatar_path, width=40)
                else:
                    st.write("👤")
            with col_name:
                st.markdown(f"### **{user}**")
                
            st.write(caption)
            
            if file_path and os.path.exists(file_path):
                if "video" in file_type:
                    st.video(file_path)
                elif "image" in file_type:
                    st.image(file_path, use_container_width=True)
            else:
                st.info("💬 [ Publicación de texto ]")
            
            current_views = views if views is not None else 0
            current_likes = likes if likes is not None else 0
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.caption(f"❤️ {current_likes} likes")
            with col_m2:
                st.caption(f"👁️ {current_views + 1} vistas")
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button("❤️ Like", key=f"like_{post_id}"):
                    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                    conn.commit()
                    # Registrar notificación de like si no es su propio post
                    if st.session_state['logged_in'] and st.session_state['username'] != user:
                        msg_notif = f"❤️ @{st.session_state['username']} le dio like a tu publicación."
                        c.execute("INSERT INTO notifications (user, message) VALUES (?, ?)", (user, msg_notif))
                        conn.commit()
                    st.rerun()
            
            with col2:
                whatsapp_url = f"https://api.whatsapp.com/send?text=Mira%20esto%20en%20VibeFeed:%20{caption}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:8px; border-radius:20px; text-align:center; font-weight:bold; font-size:12px;">💬 Compartir</div></a>', unsafe_allow_html=True)

            with col3:
                if st.button("🔗 Copiar", key=f"share_{post_id}"):
                    st.toast("¡Enlace copiado!", icon="📋")

            with col4:
                if st.session_state['logged_in'] and st.session_state['username'] == user:
                    if st.button("🗑️ Borrar", key=f"del_{post_id}"):
                        c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
                        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                        conn.commit()
                        st.toast("Publicación borrada", icon="🗑️")
                        st.rerun()
                else:
                    st.write("")

            # Comentarios
            with st.expander("💬 Comentarios"):
                try:
                    c.execute("SELECT user, comment FROM comments WHERE post_id = ?", (post_id,))
                    comments = c.fetchall()
                except sqlite3.OperationalError:
                    comments = []
                
                if comments:
                    for com in comments:
                        c_user = com[0] if com[0] else "Anónimo"
                        st.text(f"@{c_user}: {com[1]}")
                else:
                    st.text("Sé el primero en comentar...")
                
                new_com = st.text_input("Escribe un comentario...", key=f"com_input_{post_id}")
                if st.button("Enviar", key=f"btn_com_{post_id}"):
                    if new_com:
                        com_user = st.session_state['username'] if st.session_state['logged_in'] else "Anónimo"
                        try:
                            c.execute("INSERT INTO comments (post_id, user, comment) VALUES (?, ?, ?)", (post_id, com_user, new_com))
                        except sqlite3.OperationalError:
                            c.execute("ALTER TABLE comments ADD COLUMN user TEXT")
                            c.execute("INSERT INTO comments (post_id, user, comment) VALUES (?, ?, ?)", (post_id, com_user, new_com))
                        
                        # Notificar al dueño del post
                        if st.session_state['logged_in'] and st.session_state['username'] != user:
                            msg_com = f"💬 @{com_user} comentó tu publicación: '{new_com[:20]}...'"
                            c.execute("INSERT INTO notifications (user, message) VALUES (?, ?)", (user, msg_com))
                            
                        conn.commit()
                        st.rerun()
            
            st.markdown("---")

# --- SECCIÓN 2: BUSCADOR DE CREADORES ---
with menu[1]:
    st.subheader("🔍 Buscar Creadores")
    search_query = st.text_input("Escribe el nombre del usuario a buscar...", key="search_user_box")
    
    if search_query:
        c.execute("SELECT username, bio, avatar FROM users WHERE username LIKE ?", (f"%{search_query}%",))
        found_users = c.fetchall()
        
        if found_users:
            for fu in found_users:
                f_user, f_bio, f_avatar = fu
                
                col_av_s, col_info_s = st.columns([1, 5])
                with col_av_s:
                    if f_avatar and os.path.exists(f_avatar):
                        st.image(f_avatar, width=50)
                    else:
                        st.write("👤")
                with col_info_s:
                    st.markdown(f"### @{f_user}")
                    st.write(f"*{f_bio}*")
                
                if st.session_state['logged_in'] and st.session_state['username'] != f_user:
                    c.execute("SELECT * FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], f_user))
                    is_following = c.fetchone()
                    
                    if is_following:
                        if st.button(f"Dejar de seguir @{f_user}", key=f"unfollow_{f_user}"):
                            c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], f_user))
                            conn.commit()
                            st.rerun()
                    else:
                        if st.button(f"Seguir @{f_user}", key=f"follow_{f_user}"):
                            c.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (st.session_state['username'], f_user))
                            # Notificar al usuario seguido
                            msg_follow = f"👤 @{st.session_state['username']} ha empezado a seguirte."
                            c.execute("INSERT INTO notifications (user, message) VALUES (?, ?)", (f_user, msg_follow))
                            conn.commit()
                            st.rerun()
                
                c.execute("SELECT caption, file, file_type, likes FROM posts WHERE user = ? ORDER BY id DESC", (f_user,))
                u_posts = c.fetchall()
                st.caption(f"Publicaciones totales: {len(u_posts)}")
                st.markdown("---")
        else:
            st.warning("No se ha encontrado ningún creador con ese nombre.")

# --- SECCIÓN 3: HASHTAGS ---
with menu[2]:
    st.subheader("# Explorador de Hashtags")
    tag_query = st.text_input("Busca una etiqueta (ej. #tech, #humor, #viajes)...")
    
    if tag_query:
        # Asegurarse de que incluya '#' para buscar bien
        if not tag_query.startswith("#"):
            tag_query = "#" + tag_query
            
        c.execute("SELECT id, user, caption, file, file_type, likes, views FROM posts WHERE caption LIKE ? ORDER BY id DESC", (f"%{tag_query}%",))
        tagged_posts = c.fetchall()
        
        st.info(f"Mostrando resultados para: **{tag_query}** ({len(tagged_posts)} encontrados)")
        
        for post in tagged_posts:
            post_id, user, caption, file_path, file_type, likes, views = post
            with st.container():
                st.markdown(f"### **{user}**")
                st.write(caption)
                if file_path and os.path.exists(file_path):
                    if "video" in file_type:
                        st.video(file_path)
                    elif "image" in file_type:
                        st.image(file_path, use_container_width=True)
                st.caption(f"❤️ {likes} likes | 👁️ {views} vistas")
                st.markdown("---")

# --- SECCIÓN 4: MENSAJERÍA PRIVADA (DMs) ---
with menu[3]:
    st.subheader("💬 Mensajes Privados (DMs)")
    if st.session_state['logged_in']:
        current_user = st.session_state['username']
        
        # Obtener lista de usuarios para chatear
        c.execute("SELECT username FROM users WHERE username != ?", (current_user,))
        other_users = [row[0] for row in c.fetchall()]
        
        if other_users:
            chat_with = st.selectbox("Selecciona un creador para chatear:", other_users)
            
            if chat_with:
                st.markdown(f"--- \n **Chat activo con @{chat_with}**")
                
                # Cargar historial de mensajes entre ambos
                c.execute('''
                    SELECT sender, receiver, message, timestamp FROM messages 
                    WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
                    ORDER BY id ASC
                ''', (current_user, chat_with, chat_with, current_user))
                messages = c.fetchall()
                
                chat_container = st.container(height=300)
                with chat_container:
                    for msg in messages:
                        sender, receiver, text, timestamp = msg
                        if sender == current_user:
                            st.markdown(f"<div style='text-align: right; background-color: #1f6feb; color: white; padding: 8px 12px; border-radius: 12px; margin: 5px 0;'><b>Tú:</b> {text}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: left; background-color: #21262d; color: white; padding: 8px 12px; border-radius: 12px; margin: 5px 0;'><b>@{sender}:</b> {text}</div>", unsafe_allow_html=True)
                
                with st.form(key="dm_form", clear_on_submit=True):
                    new_msg = st.text_input("Escribe tu mensaje privado...")
                    send_dm = st.form_submit_button("Enviar Mensaje")
                    
                    if send_dm and new_msg:
                        c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (current_user, chat_with, new_msg))
                        # Notificar al destinatario
                        c.execute("INSERT INTO notifications (user, message) VALUES (?, ?)", (chat_with, f"💬 Nuevo mensaje privado de @{current_user}"))
                        conn.commit()
                        st.rerun()
        else:
            st.info("No hay más usuarios registrados en la plataforma para chatear todavía.")
    else:
        st.warning("⚠️ Inicia sesión para usar la mensajería privada.")

# --- SECCIÓN 5: NOTIFICACIONES / AVISOS ---
with menu[4]:
    st.subheader("🔔 Tus Notificaciones")
    if st.session_state['logged_in']:
        current_user = st.session_state['username']
        
        c.execute("SELECT id, message, is_read FROM notifications WHERE user = ? ORDER BY id DESC", (current_user,))
        notifs = c.fetchall()
        
        if st.button("Marcar todas como leídas"):
            c.execute("UPDATE notifications SET is_read = 1 WHERE user = ?", (current_user,))
            conn.commit()
            st.rerun()
            
        st.markdown("---")
        if notifs:
            for notif in notifs:
                nid, text, read_status = notif
        
    
