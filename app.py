import streamlit as st
import os
import sqlite3

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Pro - Photo Edition",
    page_icon="📸",
    layout="centered"
)

# Estilos CSS profesionales enfocados en multimedia
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
    .photo-container {
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
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

# Título principal
st.title("📸 VibeFeed Photo")
st.caption("✨ Tu galería global de momentos y creadores visuales.")

# Menú de navegación superior
menu = st.tabs(["📱 Galería Global", "➕ Subir Foto/Vídeo", "ℹ️ Acerca de"])

# --- SECCIÓN 1: LA GALERÍA / FEED VISUAL ---
with menu[0]:
    st.subheader("Explora la Comunidad Visual")
    
    # Filtro rápido de contenido
    filtro = st.radio("Filtrar contenido:", ["Todo", "Solo con Multimedia (Fotos/Vídeos)"], horizontal=True)
    
    if filtro == "Solo con Multimedia (Fotos/Vídeos)":
        c.execute("SELECT id, user, caption, file, file_type, likes FROM posts WHERE file_type != 'default' ORDER BY id DESC")
    else:
        c.execute("SELECT id, user, caption, file, file_type, likes FROM posts ORDER BY id DESC")
        
    posts = c.fetchall()
    
    if not posts:
        c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, ?)",
                  ("@photo_master", "¡Bienvenidos a la nueva experiencia visual de VibeFeed! 📸✨", None, "default", 50))
        conn.commit()
        c.execute("SELECT id, user, caption, file, file_type, likes FROM posts ORDER BY id DESC")
        posts = c.fetchall()

    for post in posts:
        post_id, user, caption, file_path, file_type, likes = post
        
        with st.container():
            st.markdown(f"### **{user}**")
            st.write(caption)
            
            # Renderizado multimedia mejorado y llamativo
            if file_path and os.path.exists(file_path):
                if "video" in file_type:
                    st.video(file_path)
                elif "image" in file_type:
                    st.image(file_path, use_container_width=True)
            else:
                st.info("📷 [ Publicación de texto de la comunidad ]")
            
            # Botones interactivos (Likes y Compartir)
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button(f"❤️ {likes}", key=f"like_{post_id}"):
                    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                    conn.commit()
                    st.rerun()
            
            with col2:
                whatsapp_url = f"https://api.whatsapp.com/send?text=Mira%20esta%20foto%20en%20VibeFeed%20Photo:%20{caption}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:8px; border-radius:20px; text-align:center; font-weight:bold; font-size:14px;">💬 Compartir</div></a>', unsafe_allow_html=True)

            with col3:
                if st.button(f"🔗 Copiar enlace", key=f"share_{post_id}"):
                    st.toast(f"¡Enlace de la foto #{post_id} copiado!", icon="📋")

            # Sección de comentarios dinámicos
            with st.expander(f"💬 Comentarios"):
                c.execute("SELECT comment FROM comments WHERE post_id = ?", (post_id,))
                comments = c.fetchall()
                
                if comments:
                    for com in comments:
                        st.text(f"• {com[0]}")
                else:
                    st.text("Sé el primero en comentar esta foto...")
                
                new_com = st.text_input("Escribe un comentario...", key=f"com_input_{post_id}")
                if st.button("Enviar comentario", key=f"btn_com_{post_id}"):
                    if new_com:
                        c.execute("INSERT INTO comments (post_id, comment) VALUES (?, ?)", (post_id, new_com))
                        conn.commit()
                        st.rerun()
            
            st.markdown("---")

# --- SECCIÓN 2: SUBIR CONTENIDO VISUAL ---
with menu[1]:
    st.subheader("Comparte tus mejores fotos y vídeos")
    with st.form("pub_form", clear_on_submit=True):
        username = st.text_input("Tu nombre de usuario", value="@")
        caption = st.text_area("Añade una descripción o historia a tu foto...")
        media = st.file_uploader("Sube tu foto o vídeo de galería", type=["mp4", "mov", "jpg", "jpeg", "png"])
        
        enviar = st.form_submit_button("Publicar en la Galería")
        
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
                st.success("¡Tu foto ya está brillando en la galería global!")
                st.rerun()
            else:
                st.warning("Por favor, rellena tu usuario y la descripción.")

# --- SECCIÓN 3: ACERCA DE Y ESTADÍSTICAS EN VIVO ---
with menu[2]:
    st.subheader("📊 Estadísticas de la Comunidad Visual")
    
    c.execute("SELECT COUNT(*) FROM posts")
    total_posts = c.fetchone()[0]
    
    c.execute("SELECT SUM(likes) FROM posts")
    total_likes_result = c.fetchone()[0]
    total_likes = total_likes_result if total_likes_result else 0
    
    c.execute("SELECT COUNT(*) FROM comments")
    total_comments = c.fetchone()[0]
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Publicaciones", total_posts)
    with col_m2:
        st.metric("Total Likes", total_likes)
    with col_m3:
        st.metric("Comentarios", total_comments)

    st.markdown("---")
    st.subheader("Acerca de VibeFeed Photo")
    st.write("""
        **VibeFeed Photo** es la evolución visual de tu plataforma, diseñada para compartir fotos con la máxima calidad y fluidez en dispositivos móviles.
        
        * **Versión:** 3.0 Photo Gallery Edition
        * **Desarrollo:** Optimizado para creadores visuales.
        * **Base de Datos:** SQLite persistente.
    """)
    st.info("¡Sube tus mejores fotos y haz crecer la comunidad!")
    

