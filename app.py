import streamlit as st
import os
import sqlite3
import hashlib

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed",
    page_icon="⚡",
    layout="centered"
)

# Estilos CSS básicos
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- BASE DE DATOS BÁSICA ---
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
            likes INTEGER
        )
    ''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

st.title("⚡ VibeFeed")
st.caption("Tu red social ligera y rápida.")

# Menú lateral sencillo
with st.sidebar:
    st.subheader("🔐 Cuenta")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Usuario")
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
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()
            
    st.markdown("---")
    menu_option = st.selectbox("Menú:", ["📱 Feed", "➕ Subir Contenido", "🔍 Buscar"])

# 1. Feed
if menu_option == "📱 Feed":
    st.subheader("Feed de la Comunidad")
    c.execute("SELECT id, user, caption, file, file_type, likes FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    
    if not posts:
        st.info("No hay publicaciones todavía. ¡Sé el primero en subir algo!")
    
    for post in posts:
        post_id, user, caption, file_path, file_type, likes = post
        with st.container():
            st.markdown(f"### **@{user}**")
            st.write(caption)
            if file_path and os.path.exists(file_path):
                if "video" in file_type: 
                    st.video(file_path)
                elif "image" in file_type: 
                    st.image(file_path, use_container_width=True)
            
            st.caption(f"❤️ {likes} likes")
            if st.button("❤️ Like", key=f"l_{post_id}"):
                c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                conn.commit()
                st.rerun()
            st.markdown("---")

# 2. Subir Contenido
elif menu_option == "➕ Subir Contenido":
    st.subheader("➕ Nueva Publicación")
    if st.session_state['logged_in']:
        with st.form("up_form", clear_on_submit=True):
            cap = st.text_area("¿Qué estás pensando?")
            media = st.file_uploader("Sube una foto o vídeo", type=["mp4", "mov", "jpg", "jpeg", "png"])
            
            if st.form_submit_button("Publicar"):
                if cap or media:
                    path, f_type = None, "default"
                    if media is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", media.name)
                        with open(path, "wb") as f: 
                            f.write(media.getbuffer())
                        f_type = media.type
                    
                    c.execute('''
                        INSERT INTO posts (user, caption, file, file_type, likes)
                        VALUES (?, ?, ?, ?, 0)
                    ''', (st.session_state['username'], cap, path, f_type))
                    conn.commit()
                    st.success("¡Publicado con éxito!")
                    st.rerun()
                else:
                    st.warning("Escribe algo o añade un archivo.")
    else:
        st.warning("Inicia sesión en el menú lateral para poder publicar.")

# 3. Buscar
elif menu_option == "🔍 Buscar":
    st.subheader("🔍 Buscar publicaciones")
    query = st.text_input("Escribe una palabra clave:")
    if query:
        c.execute("SELECT user, caption, likes FROM posts WHERE caption LIKE ?", (f"%{query}%",))
        results = c.fetchall()
        if results:
            for r in results:
                st.write(f"**@{r[0]}**: {r[1]} (❤️ {r[2]})")
                st.markdown("---")
        else:
            st.info("No se han encontrado resultados.")
            
