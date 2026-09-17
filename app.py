import streamlit as st
import os
import sqlite3
import hashlib

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Photo",
    page_icon="📸",
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

# Función para encriptar contraseñas por seguridad
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- CONFIGURACIÓN DE LA BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    # Tabla de posts con el creador asociado
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            caption TEXT,
            file TEXT,
            file_type TEXT,
            likes INTEGER
        )
    ''')
    # Tabla de comentarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user TEXT,
            comment TEXT
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
st.title("📸 VibeFeed Photo")
st.caption("✨ Tu red social visual de creadores.")

# Barra lateral para el Login / Registro estilo Instagram
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
    st.write("Versión 4.0 - Auth Edition")

# Menú de navegación superior
menu = st.tabs(["📱 Galería Global", "👤 Perfil Personal", "➕ Subir Foto/Vídeo", "ℹ️ Acerca de"])

# --- SECCIÓN 1: LA GALERÍA / FEED VISUAL ---
with menu[0]:
    st.subheader("Explora la Comunidad Visual")
    
    filtro = st.radio("Filtrar contenido:", ["Todo", "Solo con Multimedia (Fotos/Vídeos)"], horizontal=True)
    
    if filtro == "Solo con Multimedia (Fotos/Vídeos)":
        c.execute("SELECT id, user, caption, file, file_type, likes FROM posts WHERE file_type != 'default' ORDER BY id DESC")
    else:
        c.execute("SELECT id, user, caption, file, file_type, likes FROM posts ORDER BY id DESC")
        
    posts = c.fetchall()

    for post in posts:
        post_id, user, caption, file_path, file_type, likes = post
        
        with st.container():
            st.markdown(f"### **{user}**")
            st.write(caption)
            
            if file_path and os.path.exists(file_path):
                if "video" in file_type:
                    st.video(file_path)
                elif "image" in file_type:
                    st.image(file_path, use_container_width=True)
            else:
                st.info("📷 [ Publicación de texto de la comunidad ]")
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                if st.button(f"❤️ {likes}", key=f"like_{post_id}"):
                    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                    conn.commit()
                    st.rerun()
            
            with col2:
                whatsapp_url = f"https://api.whatsapp.com/send?text=Mira%20esta%20foto%20en%20VibeFeed%20Photo:%20{caption}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:8px; border-radius:20px; text-align:center; font-weight:bold; font-size:12px;">💬 Compartir</div></a>', unsafe_allow_html=True)

            with col3:
                if st.button(f"🔗 Copiar", key=f"share_{post_id}"):
                    st.toast(f"¡Enlace copiado!", icon="📋")

            with col4:
                # Solo el dueño de la publicación puede borrarla
                if st.session_state['logged_in'] and st.session_state['username'] == user:
                    if st.button(f"🗑️ Borrar", key=f"del_{post_id}"):
                        c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
                        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                        conn.commit()
                        st.toast("Publicación borrada", icon="🗑️")
                        st.rerun()
                else:
                    st.write("") # Espacio vacío si no es el dueño

            # Comentarios
            with st.expander(f"💬 Comentarios"):
                c.execute("SELECT user, comment FROM comments WHERE post_id = ?", (post_id,))
                comments = c.fetchall()
                
                if comments:
                    for com in comments:
                        st.text(f"@{com[0]}: {com[1]}")
                else:
                    st.text("Sé el primero en comentar...")
                
                new_com = st.text_input("Escribe un comentario...", key=f"com_input_{post_id}")
                if st.button("Enviar comentario", key=f"btn_com_{post_id}"):
                    if new_com:
                        com_user = st.session_state['username'] if st.session_state['logged_in'] else "Anónimo"
                        c.execute("INSERT INTO comments (post_id, user, comment) VALUES (?, ?, ?)", (post_id, com_user, new_com))
                        conn.commit()
                        st.rerun()
            
            st.markdown("---")

# --- SECCIÓN 2: PERFIL PERSONAL ---
with menu[1]:
    st.subheader("👤 Tu Muro Personal")
    if st.session_state['logged_in']:
        current_user = st.session_state['username']
        st.markdown(f"### Perfil de **{current_user}**")
        
        c.execute("SELECT id, caption, file, file_type, likes FROM posts WHERE user = ? ORDER BY id DESC", (current_user,))
        user_posts = c.fetchall()
        
        st.info(f"📸 Tienes un total de **{len(user_posts)}** publicaciones en tu muro.")
        st.markdown("---")
        
        for post in user_posts:
            post_id, caption, file_path, file_type, likes = post
            with st.container():
                st.write(caption)
                if file_path and os.path.exists(file_path):
                    if "video" in file_type:
                        st.video(file_path)
                    elif "image" in file_type:
                        st.image(file_path, use_container_width=True)
                
                if st.button(f"🗑️ Borrar mi post", key=f"my_del_{post_id}"):
                    c.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
                    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                    conn.commit()
                    st.toast("Publicación eliminada", icon="🗑️")
                    st.rerun()
                st.markdown("---")
    else:
        st.warning("⚠️ Debes iniciar sesión en la barra lateral para ver y gestionar tu perfil privado.")

# --- SECCIÓN 3: SUBIR CONTENIDO VISUAL ---
with menu[2]:
    st.subheader("Comparte tus mejores fotos y vídeos")
    if st.session_state['logged_in']:
        with st.form("pub_form", clear_on_submit=True):
            st.write(auto_user := f"Publicando como: **{st.session_state['username']}**")
            caption = st.text_area("Añade una descripción o historia a tu foto...")
            media = st.file_uploader("Sube tu foto o vídeo", type=["mp4", "mov", "jpg", "jpeg", "png"])
            
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
                    
                    c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, ?)",
                              (st.session_state['username'], caption, path, file_type, 1))
                    conn.commit()
                    st.success("¡Publicado en tu perfil y en la galería global!")
                    st.rerun()
                else:
                    st.warning("Por favor, añade una descripción.")
    else:
        st.warning("⚠️ Inicia sesión en la barra lateral con tu cuenta para poder subir contenido a VibeFeed.")

# --- SECCIÓN 4: ACERCA DE ---
with menu[3]:
    st.subheader("📊 Estadísticas de VibeFeed")
    c.execute("SELECT COUNT(*) FROM posts")
    total_posts = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    col_1, col_2 = st.columns(2)
    with col_1:
        st.metric("Creadores Registrados", total_users)
    with col_2:
        st.metric("Publicaciones Totales", total_posts)
        
    st.markdown("---")
    st.write("Red social visual privada con autenticación de usuarios por contraseña.")

    

    
