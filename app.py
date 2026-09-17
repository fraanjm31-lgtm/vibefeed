import streamlit as st
import os
import sqlite3
import hashlib

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Media",
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

# Función para encriptar contraseñas
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- CONFIGURACIÓN DE LA BASE DE DATOS SQLITE (CON AUTO-ACTUALIZACIÓN) ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
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
    # Comprobar y añadir la columna views si la tabla es antigua
    try:
        c.execute("SELECT views FROM posts LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE posts ADD COLUMN views INTEGER DEFAULT 0")

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
st.title("🎬 VibeFeed Media")
st.caption("✨ Red social multimedia con perfiles, seguidores y analíticas.")

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
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown("---")
    st.write("Versión 5.1 - Social Pro Edition")

# Menú de navegación superior
menu = st.tabs(["📱 Feed", "🔍 Buscar", "👤 Mi Perfil", "➕ Subir", "ℹ️ Info"])

# --- SECCIÓN 1: EL FEED (Global o Siguiendo) ---
with menu[0]:
    st.subheader("Feed de la Comunidad")
    
    feed_type = "Global"
    if st.session_state['logged_in']:
        feed_mode = st.radio("Mostrar publicaciones de:", ["🌍 Global", "👥 Siguiendo"], horizontal=True)
        if feed_mode == "👥 Siguiendo":
            feed_type = "Following"

    filtro = st.radio("Filtrar:", ["Todo", "Vídeos", "Fotos"], horizontal=True)
    
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
                        conn.commit()
                        st.rerun()
            
            st.markdown("---")

# --- SECCIÓN 2: BUSCADOR DE CREADORES ---
with menu[1]:
    st.subheader("🔍 Buscar Creadores")
    search_query = st.text_input("Escribe el nombre del usuario a buscar...")
    
    if search_query:
        c.execute("SELECT username FROM users WHERE username LIKE ?", (f"%{search_query}%",))
        found_users = c.fetchall()
        
        if found_users:
            for fu in found_users:
                f_user = fu[0]
                st.markdown(f"### 👤 @{f_user}")
                
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
                            conn.commit()
                            st.rerun()
                
                c.execute("SELECT caption, file, file_type, likes FROM posts WHERE user = ? ORDER BY id DESC", (f_user,))
                u_posts = c.fetchall()
                st.caption(f"Publicaciones: {len(u_posts)}")
                st.markdown("---")
        else:
            st.warning("No se ha encontrado ningún creador con ese nombre.")

# --- SECCIÓN 3: PERFIL PERSONAL ---
with menu[2]:
    st.subheader("👤 Tu Muro y Estadísticas")
    if st.session_state['logged_in']:
        current_user = st.session_state['username']
        st.markdown(f"### Perfil de **{current_user}**")
        
        c.execute("SELECT COUNT(*) FROM follows WHERE followed = ?", (current_user,))
        followers_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM follows WHERE follower = ?", (current_user,))
        following_count = c.fetchone()[0]
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.metric("Seguidores", followers_count)
        with col_f2:
            st.metric("Siguiendo", following_count)
            
        st.markdown("---")
        
        c.execute("SELECT id, caption, file, file_type, likes, views FROM posts WHERE user = ? ORDER BY id DESC", (current_user,))
        user_posts = c.fetchall()
        
        st.info(f"📁 Tienes un total de **{len(user_posts)}** publicaciones.")
        st.markdown("---")
        
        for post in user_posts:
            post_id, caption, file_path, file_type, likes, views = post
            with st.container():
                st.write(caption)
                if file_path and os.path.exists(file_path):
                    if "video" in file_type:
                        st.video(file_path)
                    elif "image" in file_type:
                        st.image(file_path, use_container_width=True)
                
                v_count = views if views is not None else 0
                l_count = likes if likes is not None else 0
                st.caption(f"❤️ {l_count} likes | 👁️ {v_count} vistas")
                
                if st.button("🗑️ Borrar publicación", key=f"my_del_{post_id}"):
                    c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
                    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                    conn.commit()
                    st.toast("Publicación eliminada", icon="🗑️")
                    st.rerun()
                st.markdown("---")
    else:
        st.warning("⚠️ Inicia sesión para ver tu perfil.")

# --- SECCIÓN 4: SUBIR CONTENIDO ---
with menu[3]:
    st.subheader("Sube Contenido Multimedia")
    if st.session_state['logged_in']:
        with st.form("pub_form", clear_on_submit=True):
            st.write(f"Publicando como: **{st.session_state['username']}**")
            caption = st.text_area("Añade una descripción...")
            media = st.file_uploader("Sube foto o vídeo", type=["mp4", "mov", "jpg", "jpeg", "png"])
            
            enviar = st.form_submit_button("Publicar")
            
            if enviar:
                if caption:
                    path = None
                    file_type = "default"
                    if media is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", media.name)
                        with open(path, "wb") as f:
                            f.write(media.getbuffer())
                        file_type = media.type
                    
                    c.execute("INSERT INTO posts (user, caption, file, file_type, likes, views) VALUES (?, ?, ?, ?, ?, ?)",
                              (st.session_state['username'], caption, path, file_type, 1, 0))
                    conn.commit()
                    st.success("¡Publicado con éxito!")
                    st.rerun()
                else:
                    st.warning("Escribe una descripción.")
    else:
        st.warning("⚠️ Inicia sesión para subir contenido.")

# --- SECCIÓN 5: INFORMACIÓN ---
with menu[4]:
    st.subheader("📊 Estadísticas Generales")
    c.execute("SELECT COUNT(*) FROM posts")
    total_posts = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    col_1, col_2 = st.columns(2)
    with col_1:
        st.metric("Creadores", total_users)
    with col_2:
        st.metric("Posts Globales", total_posts)
    
