import streamlit as st
import sqlite3
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="NoxVibe", page_icon="🧭", layout="centered")

# Estilos CSS personalizados (Modo Oscuro / Neón)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión a Base de Datos
conn = sqlite3.connect('noxvibe.db', check_same_thread=False)
c = conn.cursor()

# Crear tablas si no existen
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, xp INTEGER, bio TEXT, avatar TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, vibe_tag TEXT, timestamp TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT)''')
conn.commit()

# Función de la IA para etiquetar vibraciones
def ai_vibe_checker(text):
    if not text:
        return "✨ Chill", "Ambiente tranquilo y relajado detectado."
    t = text.lower()
    if any(w in t for w in ["fiesta", "noche", "baila", "dj", "alcohol", "musica"]):
        return "🎉 Fiesta", "¡Energía de fiesta a tope detectada por la IA!"
    elif any(w in t for w in ["amor", "corazon", "te amo", "feliz", "lindo"]):
        return "❤️ Hype / Amor", "¡Vibra muy positiva y afectuosa detectada!"
    elif any(w in t for w in ["triste", "solo", "mal", "duro", "llorar"]):
        return "🌧️ Melancólico", "Momento de reflexión detectado por el sistema."
    else:
        return "🚀 Inspirador", "¡Pensamiento innovador detectado!"

# Estado de sesión para control de usuarios
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Menú lateral de navegación
st.sidebar.title("🧭 Menú")
menu_option = st.sidebar.radio("Navegación", ["Mi Perfil", "Siguiendo", "Muro 24h", "Explorar Canales", "Mensajes", "Ajustes"])

if st.session_state.logged_in:
    st.sidebar.markdown(f"---")
    st.sidebar.success(f"Sesión: @{st.session_state.username}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# --- PANTALLA DE INICIO DE SESIÓN / REGISTRO ---
if not st.session_state.logged_in:
    st.title("Bienvenido a NoxVibe 🚀")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        l_user = st.text_input("Usuario", key="l_user")
        l_pass = st.text_input("Contraseña", type="password", key="l_pass")
        if st.button("Entrar"):
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (l_user, l_pass))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.username = l_user
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
                
    with tab2:
        r_user = st.text_input("Nuevo Usuario", key="r_user")
        r_pass = st.text_input("Nueva Contraseña", type="password", key="r_pass")
        if st.button("Crear cuenta"):
            if r_user and r_pass:
                try:
                    c.execute("INSERT INTO users (username, password, xp, bio, avatar) VALUES (?, ?, ?, ?, ?)", 
                              (r_user, r_pass, 10, "¡Hola! Estoy usando NoxVibe.", ""))
                    conn.commit()
                    st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                except:
                    st.error("El nombre de usuario ya existe.")
            else:
                st.warning("Rellena todos los campos.")

# --- APLICACIÓN PRINCIPAL ---
else:
    cur = st.session_state.username
    
    # Obtener datos del usuario
    c.execute("SELECT xp, bio, avatar FROM users WHERE username = ?", (cur,))
    user_data = c.fetchone()
    xp = user_data[0] if user_data else 0
    bio = user_data[1] if user_data else ""
    avatar = user_data[2] if user_data else ""

    if menu_option == "Mi Perfil":
        st.title(f"@{cur}")
        
        # Calcular estadísticas reales de la base de datos
        c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (cur,))
        total_posts = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM follows WHERE followed = ?", (cur,))
        total_followers = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM follows WHERE follower = ?", (cur,))
        total_following = c.fetchone()[0]

        # Perfil con foto, métricas reales y biografía
        col1, col2 = st.columns([1, 2])
        with col1:
            if avatar and os.path.exists(avatar):
                st.image(avatar, width=100)
            else:
                st.image("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", width=100)
        with col2:
            # Métricas reales conectadas a SQLite
            m1, m2, m3 = st.columns(3)
            m1.metric("Posts", total_posts)
            m2.metric("Seguidores", total_followers)
            m3.metric("Siguiendo", total_following)
            
            st.markdown(f"**Tus XP:** {xp}")
            st.write(bio)
            
        st.markdown("---")
        
        # Formulario desplegable para publicar contenido
        with st.expander("✏️ Publicar Contenido", expanded=False):
            with st.form("new_post_form", clear_on_submit=True):
                cap = st.text_input("¿Qué estás pensando?")
                uploaded_file = st.file_uploader("Sube foto o vídeo", type=["jpg", "png", "mp4", "mov"])
                
                if st.form_submit_button("Publicar con IA 🚀"):
                    path_to_save = ""
                    f_type = ""
                    if uploaded_file is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path_to_save = os.path.join("uploads", uploaded_file.name)
                        with open(path_to_save, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        f_type = "video" if uploaded_file.type.startswith("video") else "image"
                    
                    auto_tag, ai_msg = ai_vibe_checker(cap)
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    c.execute("INSERT INTO posts (username, caption, file, file_type, likes, vibe_tag, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (cur, cap, path_to_save, f_type, 0, auto_tag, now_str))
                    c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (cur,))
                    conn.commit()
                    st.success(f"¡Publicado! {ai_msg} (+15 XP)")
                    st.rerun()

        st.markdown("### Tus publicaciones recientes")
        c.execute("SELECT caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? ORDER BY id DESC", (cur,))
        user_posts = c.fetchall()
        
        if not user_posts:
            st.info("Aún no has publicado nada. ¡Despliega 'Publicar Contenido' arriba para crear tu primer post!")
        
        for post in user_posts:
            p_cap, p_file, p_type, p_likes, p_tag, p_time = post
            st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
            if p_cap:
                st.write(p_cap)
            if p_file and os.path.exists(p_file):
                if p_type == "image":
                    st.image(p_file, use_column_width=True)
                elif p_type == "video":
                    st.video(p_file)
            st.markdown(f"❤️ {p_likes} Me gusta")
            st.markdown("---")

    elif menu_option == "Muro 24h":
        st.title("🌐 Muro Global 24h")
        st.write("Explora lo que comparte la comunidad de NoxVibe:")
        
        c.execute("SELECT username, caption, file, file_type, likes, vibe_tag, timestamp FROM posts ORDER BY id DESC")
        all_posts = c.fetchall()
        
        if not all_posts:
            st.info("El muro está tranquilo por ahora. ¡Sé el primero en publicar algo!")
            
        for post in all_posts:
            p_user, p_cap, p_file, p_type, p_likes, p_tag, p_time = post
            st.markdown(f"**@{p_user}** · `{p_tag}` · {p_time}")
            if p_cap:
                st.write(p_cap)
            if p_file and os.path.exists(p_file):
                if p_type == "image":
                    st.image(p_file, use_column_width=True)
                elif p_type == "video":
                    st.video(p_file)
            st.markdown(f"❤️ {p_likes} Me gusta")
            st.markdown("---")

    elif menu_option == "Siguiendo":
        st.title("👥 Siguiendo")
        st.write("Aquí verás las publicaciones de la gente que sigues.")

    elif menu_option == "Explorar Canales":
        st.title("🔍 Explorar Canales")
        st.write("Descubre temáticas, música y tendencias.")

    elif menu_option == "Mensajes":
        st.title("💬 Mensajes Directos")
        st.write("Tus chats privados aparecerán aquí.")

    elif menu_option == "Ajustes":
        st.title("⚙️ Ajustes de la cuenta")
        
        new_bio = st.text_area("Actualizar tu biografía", value=bio)
        new_avatar = st.file_uploader("Sube tu nueva foto de perfil", type=["jpg", "png", "jpeg"])
        
        if st.button("Guardar cambios"):
            avatar_path = avatar
            if new_avatar is not None:
                os.makedirs("uploads", exist_ok=True)
                avatar_path = os.path.join("uploads", f"avatar_{cur}_{new_avatar.name}")
                with open(avatar_path, "wb") as f:
                    f.write(new_avatar.getbuffer())
            
            c.execute("UPDATE users SET bio = ?, avatar = ? WHERE username = ?", (new_bio, avatar_path, cur))
            conn.commit()
            st.success("¡Perfil y foto actualizados con éxito!")
            st.rerun()
            
