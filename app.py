import streamlit as st
import sqlite3
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="NoxVibe", page_icon="🧭", layout="centered")

# Estilos CSS personalizados (Modo Oscuro / Neón y diseño de perfil en línea)
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
    /* Estilo para alinear contadores de perfil de forma compacta */
    .profile-stats {
        display: flex;
        justify-content: space-around;
        text-align: center;
        background: #161b22;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stat-box {
        display: inline-block;
        margin: 0 8px;
    }
    .stat-num {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    .stat-label {
        font-size: 12px;
        color: #8b949e;
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

# Asegurar columnas y esquemas actualizados sin errores
try:
    c.execute("ALTER TABLE posts ADD COLUMN privacy TEXT DEFAULT 'Público'")
except:
    pass

try:
    c.execute("ALTER TABLE users ADD COLUMN account_privacy TEXT DEFAULT 'Público'")
except:
    pass

try:
    c.execute("ALTER TABLE follows ADD COLUMN status TEXT DEFAULT 'accepted'")
except:
    pass

try:
    c.execute("ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 100")
except:
    pass

# Tabla para registrar los regalos enviados
c.execute('''CREATE TABLE IF NOT EXISTS gifts (
             id INTEGER PRIMARY KEY AUTOINCREMENT, 
             sender TEXT, 
             receiver TEXT, 
             post_id INTEGER, 
             gift_name TEXT, 
             coins_cost INTEGER, 
             timestamp TEXT)''')

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
    st.session_state.profile_tab = "Fotos"

# Menú lateral de navegación
st.sidebar.title("🧭 Menú")
menu_option = st.sidebar.radio("Navegación", ["Mi Perfil", "Buscar / Ver Perfiles", "Siguiendo", "Muro 24h", "Explorar Canales", "Mensajes", "Ajustes"])

if st.session_state.logged_in:
    c.execute("SELECT coins FROM users WHERE username = ?", (st.session_state.username,))
    res_coins = c.fetchone()
    user_coins = res_coins[0] if res_coins else 100
    
    st.sidebar.markdown(f"---")
    st.sidebar.success(f"Sesión: @{st.session_state.username}")
    st.sidebar.info(f"🪙 NoxCoins: **{user_coins} 🪙**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# --- PANTALLA DE INICIO DE SESIÓN / REGISTRO ---
if not st.session_state.logged_in:
    st.title("Bienvenido a NoxVibe 🚀")
    tab_login, tab_reg = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
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
                
    with tab_reg:
        r_user = st.text_input("Nuevo Usuario", key="r_user")
        r_pass = st.text_input("Nueva Contraseña", type="password", key="r_pass")
        if st.button("Crear cuenta"):
            if r_user and r_pass:
                try:
                    c.execute("INSERT INTO users (username, password, xp, bio, avatar, account_privacy, coins) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (r_user, r_pass, 10, "¡Hola! Estoy usando NoxVibe.", "", "Público", 100))
                    conn.commit()
                    st.success("¡Cuenta creada con éxito! Tienes 100 NoxCoins de regalo. Ya puedes iniciar sesión.")
                except:
                    st.error("El nombre de usuario ya existe.")
            else:
                st.warning("Rellena todos los campos.")

# --- APLICACIÓN PRINCIPAL ---
else:
    cur = st.session_state.username
    
    if menu_option == "Mi Perfil":
        c.execute("SELECT xp, bio, avatar, account_privacy, coins FROM users WHERE username = ?", (cur,))
        user_data = c.fetchone()
        xp = user_data[0] if user_data else 0
        bio = user_data[1] if user_data else ""
        avatar = user_data[2] if user_data else ""
        account_privacy = user_data[3] if user_data else "Público"
        coins = user_data[4] if user_data else 100

        priv_badge = "🔒 Cuenta Privada" if account_privacy == "Privado" else "🌐 Cuenta Pública"
        st.title(f"@{cur} ({priv_badge})")
        
        c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (cur,))
        total_posts = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM follows WHERE followed = ? AND status = 'accepted'", (cur,))
        total_followers = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM follows WHERE follower = ? AND status = 'accepted'", (cur,))
        total_following = c.fetchone()[0]

        col1, col2 = st.columns([1, 2])
        with col1:
            if avatar and os.path.exists(avatar):
                st.image(avatar, width=110)
            else:
                st.image("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", width=110)
        with col2:
            st.markdown(f"""
                <div class="profile-stats">
                    <div class="stat-box">
                        <div class="stat-num">{total_posts}</div>
                        <div class="stat-label">Posts</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num">{total_followers}</div>
                        <div class="stat-label">Seguidores</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-num">{total_following}</div>
                        <div class="stat-label">Siguiendo</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Tus XP:** {xp} | **NoxCoins:** {coins} 🪙")
            
        st.write(bio)
            
        c.execute("SELECT follower FROM follows WHERE followed = ? AND status = 'pending'", (cur,))
        pending_requests = c.fetchall()
        
        if pending_requests:
            st.markdown("---")
            st.markdown("### 🔔 Solicitudes de seguimiento pendientes")
            for req in pending_requests:
                req_user = req[0]
                cols_req = st.columns([2, 1, 1])
                with cols_req[0]:
                    st.write(f"**@{req_user}** quiere seguirte.")
                with cols_req[1]:
                    if st.button("Aceptar", key=f"accept_{req_user}"):
                        c.execute("UPDATE follows SET status = 'accepted' WHERE follower = ? AND followed = ?", (req_user, cur))
                        conn.commit()
                        st.success(f"¡Has aceptado a @{req_user}!")
                        st.rerun()
                with cols_req[2]:
                    if st.button("Rechazar", key=f"reject_{req_user}"):
                        c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (req_user, cur))
                        conn.commit()
                        st.rerun()

        st.markdown("---")
        
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
                    
                    c.execute("INSERT INTO posts (username, caption, file, file_type, likes, vibe_tag, timestamp, privacy) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                              (cur, cap, path_to_save, f_type, 0, auto_tag, now_str, "Público"))
                    c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (cur,))
                    conn.commit()
                    st.success(f"¡Publicado! {ai_msg} (+15 XP)")
                    st.rerun()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🖼️ Fotos", use_container_width=True):
                st.session_state.profile_tab = "Fotos"
        with col_btn2:
            if st.button("🎬 Vídeos", use_container_width=True):
                st.session_state.profile_tab = "Vídeos"

        st.markdown("---")

        if st.session_state.profile_tab == "Fotos":
            st.markdown("### 🖼️ Tus Fotos")
            c.execute("SELECT id, caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? AND (file_type = 'image' OR file_type = '') ORDER BY id DESC", (cur,))
            photo_posts = c.fetchall()
            
            if not photo_posts:
                st.info("No tienes fotos publicadas todavía.")
            
            for post in photo_posts:
                p_id, p_cap, p_file, p_type, p_likes, p_tag, p_time = post
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap:
                    st.write(p_cap)
                if p_file and os.path.exists(p_file):
                    st.image(p_file, use_column_width=True)
                
                c.execute("SELECT gift_name, COUNT(*) FROM gifts WHERE post_id = ? GROUP BY gift_name", (p_id,))
                post_gifts = c.fetchall()
                if post_gifts:
                    gift_summary = " · ".join([f"{g[0]} (x{g[1]})" for g in post_gifts])
                    st.markdown(f"🎁 **Regalos recibidos:** {gift_summary}")

                st.markdown(f"❤️ {p_likes} Me gusta")
                st.markdown("---")
                
        else:
            st.markdown("### 🎬 Tus Vídeos")
            c.execute("SELECT id, caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? AND file_type = 'video' ORDER BY id DESC", (cur,))
            video_posts = c.fetchall()
            
            if not video_posts:
                st.info("No tienes vídeos publicados todavía.")
                
            for post in video_posts:
                p_id, p_cap, p_file, p_type, p_likes, p_tag, p_time = post
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap:
                    st.write(p_cap)
                if p_file and os.path.exists(p_file):
                    st.video(p_file)

                c.execute("SELECT gift_name, COUNT(*) FROM gifts WHERE post_id = ? GROUP BY gift_name", (p_id,))
                post_gifts = c.fetchall()
                if post_gifts:
                    gift_summary = " · ".join([f"{g[0]} (x{g[1]})" for g in post_gifts])
                    st.markdown(f"🎁 **Regalos recibidos:** {gift_summary}")

                st.markdown(f"❤️ {p_likes} Me gusta")
                st.markdown("---")

    elif menu_option == "Buscar / Ver Perfiles":
        st.title("🔍 Buscar Perfiles")
        search_user = st.text_input("Escribe el nombre de usuario que quieres buscar:")
        
        if search_user:
            c.execute("SELECT username, bio, avatar, account_privacy FROM users WHERE username = ?", (search_user,))
            target_user = c.fetchone()
            
            if not target_user:
                st.error("No se ha encontrado ningún usuario con ese nombre.")
            else:
                t_user, t_bio, t_avatar, t_privacy = target_user
                
                st.markdown(f"### Perfil de @{t_user}")
                col_u1, col_u2 = st.columns([1, 2])
                with col_u1:
                    if t_avatar and os.path.exists(t_avatar):
                        st.image(t_avatar, width=100)
                    else:
                        st.image("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", width=100)
                with col_u2:
                    st.write(t_bio)
                    
                c.execute("SELECT status FROM follows WHERE follower = ? AND followed = ?", (cur, t_user))
                row_follow = c.fetchone()
                follow_status = row_follow[0] if row_follow else None
                
                if t_user != cur:
                    if follow_status == 'accepted':
                        if st.button("Siguiendo 👤✓"):
                            c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (cur, t_user))
                            conn.commit()
                            st.rerun()
                    elif follow_status == 'pending':
                        if st.button("Solicitud Enviada ⏳"):
                            c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (cur, t_user))
                            conn.commit()
                            st.rerun()
                    else:
                        btn_label = "Solicitar Seguir 🔒" if t_privacy == "Privado" else "Seguir ➕"
                        if st.button(btn_label):
                            initial_status = 'pending' if t_privacy == "Privado" else 'accepted'
                            c.execute("INSERT INTO follows (follower, followed, status) VALUES (?, ?, ?)", (cur, t_user, initial_status))
                            conn.commit()
                            st.rerun()

                st.markdown("---")
                
                if t_privacy == "Privado" and t_user != cur and follow_status != 'accepted':
                    st.warning("🔒 **Esta cuenta es privada.** Envía una solicitud de seguimiento para ver sus fotos y vídeos.")
                else:
                    st.markdown("#### Publicaciones:")
                    c.execute("SELECT id, caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? ORDER BY id DESC", (t_user,))
                    user_posts = c.fetchall()
                    
                    if not user_posts:
                        st.info("Este usuario no tiene publicaciones.")
                    
                    for post in user_posts:
                        p_id, p_cap, p_file, p_type, p_likes, p_tag, p_time = post
                        st.markdown(f"**@{t_user}** · `{p_tag}` · {p_time}")
                        if p_cap:
                            st.write(p_cap)
                        if p_file and os.path.exists(p_file):
                            if p_type == "video":
                                st.video(p_file)
                            else:
                                st.image(p_file, use_column_width=True)
                        
                        c.execute("SELECT gift_name, COUNT(*) FROM gifts WHERE post_id = ? GROUP BY gift_name", (p_id,))
                        post_gifts = c.fetchall()
                        if post_gifts:
                            gift_summary = " · ".join([f"{g[0]} (x{g[1]})" for g in post_gifts])
                            st.markdown(f"🎁 **Regalos recibidos:** {gift_summary}")

                        st.markdown(f"❤️ {p_likes} Me gusta")
                        
                        if t_user != cur:
                            col_g1, col_g2, col_g3 = st.columns(3)
                            with col_g1:
                                if st.button("🔥 Fuego (10 🪙)", key=f"fire_{p_id}"):
                                    c.execute("SELECT coins FROM users WHERE username = ?", (cur,))
                                    my_coins = c.fetchone()[0]
                                    if my_coins >= 10:
                                        c.execute("UPDATE users SET coins = coins - 10 WHERE username = ?", (cur,))
                                        c.execute("UPDATE users SET coins = coins + 10 WHERE username = ?", (t_user,))
                                        c.execute("INSERT INTO gifts (sender, receiver, post_id, gift_name, coins_cost, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                                  (cur, t_user, p_id, "🔥 Fuego", 10, datetime.now().strftime("%Y-%m-%d %H:%M")))
                                        conn.commit()
                                        st.success("¡Has enviado 🔥 Fuego!")
                                        st.rerun()
                                    else:
                                        st.error("No tienes suficientes NoxCoins.")
                            with col_g2:
                                if st.button("⭐ Estrella (50 🪙)", key=f"star_{p_id}"):
                                    c.execute("SELECT coins FROM users WHERE username = ?", (cur,))
                                    my_coins = c.fetchone()[0]
                                    if my_coins >= 50:
                                        c.execute("UPDATE users SET coins = coins - 50 WHERE username = ?", (cur,))
                                        c.execute("UPDATE users SET coins = coins + 50 WHERE username = ?", (t_user,))
                                        c.execute("INSERT INTO gifts (sender, receiver, post_id, gift_name, coins_cost, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                                  (cur, t_user, p_id, "⭐ Estrella", 50, datetime.now().strftime("%Y-%m-%d %H:%M")))
                                        conn.commit()
                                        st.s
