
import streamlit as st
import os
import sqlite3

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Pro",
    page_icon="🔥",
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
    .card {
        padding: 15px;
        border-radius: 10px;
        background-color: #161b22;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LA BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            comment TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# Título principal y estadísticas de audiencia
st.title("🔥 VibeFeed Pro")
st.caption("✨ La comunidad global de creadores de contenido.")

# Menú de navegación superior
menu = st.tabs(["📱 Feed en Directo", "➕ Publicar", "ℹ️ Acerca de"])

# --- SECCIÓN 1: EL FEED ---
with menu[0]:
    st.subheader("Tendencias para ti")
    
    # Obtener posts de la base de datos
    c.execute("SELECT id, user, caption, file, file_type, likes FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    
    # Si la base de datos está vacía, insertamos posts de ejemplo iniciales
    if not posts:
        c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, ?)",
                  ("@creator_pro", "¡Bienvenidos a la nueva era de VibeFeed Pro! 🚀🔥", None, "default", 42))
        c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, ?)",
                  ("@code_ninja", "Programando apps profesionales desde el móvil. ¡Todo es posible! 📱💻", None, "default", 28))
        conn.commit()
        c.execute("SELECT id, user, caption, file, file_type, likes FROM posts ORDER BY id DESC")
        posts = c.fetchall()

    for post in posts:
        post_id, user, caption, file_path, file_type, likes = post
        
        with st.container():
            st.markdown(f"### **{user}**")
            st.write(caption)
            
            # Renderizado multimedia
            if file_path and os.path.exists(file_path):
                if "video" in file_type:
                    st.video(file_path)
                elif "image" in file_type:
                    st.image(file_path, use_container_width=True)
            else:
                st.info("🎬 [ Contenido verificado de la comunidad ]")
            
            # Botón de Me Gusta interactivo
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button(f"❤️ {likes}", key=f"like_{post_id}"):
                    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                    conn.commit()
                    st.rerun()
            
            # Sección de comentarios dinámicos
            with st.expander(f"💬 Comentarios"):
                c.execute("SELECT comment FROM comments WHERE post_id = ?", (post_id,))
                comments = c.fetchall()
                
                if comments:
                    for com in comments:
                        st.text(f"• {com[0]}")
                else:
                    st.text("Sé el primero en comentar...")
                
                new_com = st.text_input("Escribe un comentario...", key=f"com_input_{post_id}")
                if st.button("Enviar comentario", key=f"btn_com_{post_id}"):
                    if new_com:
                        c.execute("INSERT INTO comments (post_id, comment) VALUES (?, ?)", (post_id, new_com))
                        conn.commit()
                        st.rerun()
            
            st.markdown("---")

# --- SECCIÓN 2: PUBLICAR CONTENIDO ---
with menu[1]:
    st.subheader("Comparte tu momento con el mundo")
    with st.form("pub_form", clear_on_submit=True):
        username = st.text_input("Tu nombre de usuario", value="@")
        caption = st.text_area("¿Qué estás pensando o creando?")
        media = st.file_uploader("Sube tu foto o vídeo", type=["mp4", "mov", "jpg", "png"])
        
        enviar = st.form_submit_button("Publicar en VibeFeed")
        
        if enviar:
            if username and caption:
                path = None
                file_type = "default"
                if media is not None:
                    os.makedirs("uploads", exist_ok=True)
                    path = os.path.join("uploads", media.name)
                    with open(path, "wb") as f:
                        f.write(media.getbuffer())
                    file_type = media.type
                
                c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, ?)",
                          (username, caption, path, file_type, 1))
                conn.commit()
                st.success("¡Tu publicación ya está en directo para toda la audiencia!")
                st.rerun()
            else:
                st.warning("Por favor, rellena tu usuario y la descripción.")

# --- SECCIÓN 3: ACERCA DE ---
with menu[2]:
    st.subheader("Acerca de VibeFeed Pro")
    st.write("""
        **VibeFeed Pro** es una plataforma social diseñada para ofrecer experiencias multimedia fluidas, interactivas y adaptadas al rendimiento móvil.
        
        * **Versión:** 2.0 Pro Audience Edition
        * **Desarrollo:** Optimizado para creadores y comunidades activas.
        * **Estado del Servidor:** Conectado a base de datos segura SQLite.
    """)
    st.info("¡Gracias por formar parte de la comunidad!")
