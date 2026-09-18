import streamlit as st
import sqlite3
import os
from datetime import datetime, date

st.set_page_config(page_title="NoxVibe", page_icon="🧭", layout="centered")

# Gestionar el tema visual guardado en la sesión
if 'theme' not in st.session_state:
    st.session_state.theme = "Oscuro (Por defecto)"

# Definir colores según el tema elegido
if st.session_state.theme == "Claro":
    bg_color = "#ffffff"
    text_color = "#000000"
    box_bg = "#f0f2f6"
    sub_text = "#555555"
elif st.session_state.theme == "Neón / Cyber":
    bg_color = "#05050a"
    text_color = "#00ffcc"
    box_bg = "#121224"
    sub_text = "#ff007f"
else:  # Oscuro
    bg_color = "#0e1117"
    text_color = "#ffffff"
    box_bg = "#161b22"
    sub_text = "#8b949e"

st.markdown(f"""
    <style>
    header [data-testid="stToolbar"] a[href*="github"],
    header [data-testid="stToolbar"] button[kind="header"],
    header [data-testid="stToolbar"] [title*="Edit"],
    header [data-testid="stToolbar"] [title*="Share"],
    header [data-testid="stToolbar"] button[aria-label*="Share"],
    header [data-testid="stToolbar"] button[aria-label="Edit"],
    header [data-testid="stToolbar"] [data-testid="stDecoration"],
    header [data-testid="collapsedControl"] {{
        display: none !important;
    }}
    
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .profile-stats {{
        display: flex;
        justify-content: space-around;
        text-align: center;
        background: {box_bg};
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }}
    .stat-box {{
        display: inline-block;
        margin: 0 8px;
    }}
    .stat-num {{
        font-size: 18px;
        font-weight: bold;
        color: {text_color};
    }}
    .stat-label {{
        font-size: 12px;
        color: {sub_text};
    }}
    .video-container {{
        position: relative;
        background: {box_bg};
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    </style>
""", unsafe_allow_html=True)

conn = sqlite3.connect('noxvibe.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, xp INTEGER, bio TEXT, avatar TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, vibe_tag TEXT, timestamp TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS post_reactions (post_id INTEGER, username TEXT, reaction_type TEXT)''')

try:
    c.execute("ALTER TABLE users ADD COLUMN email TEXT")
except:
    pass
try:
    c.execute("ALTER TABLE posts ADD COLUMN fires INTEGER DEFAULT 0")
except:
    pass
try:
    c.execute("ALTER TABLE posts ADD COLUMN thumbs INTEGER DEFAULT 0")
except:
    pass
try:
    c.execute("ALTER TABLE posts ADD COLUMN hearts INTEGER DEFAULT 0")
except:
    pass
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

c.execute('''CREATE TABLE IF NOT EXISTS gifts (
             id INTEGER PRIMARY KEY AUTOINCREMENT, 
             sender TEXT, 
             receiver TEXT, 
             post_id INTEGER, 
             gift_name TEXT, 
             coins_cost INTEGER, 
             timestamp TEXT)''')
conn.commit()

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

def handle_reaction(p_id, user, r_type):
    c.execute("SELECT * FROM post_reactions WHERE post_id = ? AND username = ? AND reaction_type = ?", (p_id, user, r_type))
    if not c.fetchone():
        c.execute("INSERT INTO post_reactions (post_id, username, reaction_type) VALUES (?, ?, ?)", (p_id, user, r_type))
        if r_type == 'fire':
            c.execute("UPDATE posts SET fires = fires + 1 WHERE id = ?", (p_id,))
        elif r_type == 'thumb':
            c.execute("UPDATE posts SET thumbs = thumbs + 1 WHERE id = ?", (p_id,))
        elif r_type == 'heart':
            c.execute("UPDATE posts SET hearts = hearts + 1 WHERE id = ?", (p_id,))
        conn.commit()
        st.rerun()
    else:
        st.toast("¡Ya has dado esta reacción!", icon="⚠️")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.profile_tab = "Fotos"

st.sidebar.title("🧭 Menú NoxVibe")
menu_option = st.sidebar.radio("Navegación", ["🔥 Feed de Vídeos", "Mi Perfil", "Buscar / Ver Perfiles", "Siguiendo", "Explorar Canales", "Mensajes", "Ajustes"])

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

if not st.session_state.logged_in:
    st.title("Bienvenido a NoxVibe 🚀")
    st.info("🔒 **Acceso Estricto:** Comunidad privada exclusiva para mayores de edad con invitación y correo.")
    
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
        r_email = st.text_input("Correo Electrónico (Obligatorio)", key="r_email")
        r_user = st.text_input("Nuevo Usuario", key="r_user")
        r_pass = st.text_input("Nueva Contraseña", type="password", key="r_pass")
        r_dob = st.date_input("Fecha de nacimiento", min_value=date(1900, 1, 1), max_value=date.today(), key="r_dob")
        
        codigo_secreto_invitacion = "noxvibe2026"
        r_invite = st.text_input("Código de Invitación / Acceso", type="password", key="r_invite", placeholder="Pide el código al administrador")
        r_adult = st.checkbox("Confirmo bajo mi responsabilidad que soy mayor de 18 años.")
        
        if st.button("Crear cuenta"):
            today = date.today()
            age = today.year - r_dob.year - ((today.month, today.day) < (r_dob.month, r_dob.day))
            
            if not r_email or "@" not in r_email or "." not in r_email:
                st.error("❌ Introduce un correo electrónico válido.")
            elif not r_user or not r_pass:
                st.warning("⚠️ Rellena el usuario y la contraseña.")
            elif age < 18:
                st.error("❌ Lo sentimos, debes ser mayor de 18 años.")
            elif r_invite != codigo_secreto_invitacion:
                st.error("❌ Código de invitación incorrecto. Esta comunidad es privada.")
            elif not r_adult:
                st.warning("⚠️ Debes marcar la casilla de confirmación de mayoría de edad.")
            else:
                try:
                    c.execute("INSERT INTO users (username, password, email, xp, bio, avatar, account_privacy, coins) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                              (r_user, r_pass, r_email, 10, "¡Hola! Estoy usando NoxVibe.", "", "Público", 100))
                    conn.commit()
                    st.success("¡Cuenta creada con éxito y verificada! Ya puedes iniciar sesión.")
                except:
                    st.error("El nombre de usuario ya está en uso.")

else:
    cur = st.session_state.username
    
    if menu_option == "🔥 Feed de Vídeos":
        st.title("🔥 NoxVibe Feed")
        st.write("Vídeos públicos de la comunidad al estilo interactivo.")
        
        c.execute("""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
            FROM posts p 
            JOIN users u ON p.username = u.username 
            WHERE p.file_type = 'video' AND u.account_privacy = 'Público' 
            ORDER BY p.id DESC
        """)
        videos = c.fetchall()
        
        if not videos:
            st.info("No hay vídeos públicos en este momento. ¡Sube el primero desde tu perfil!")
        else:
            for post in videos:
                p_id, p_user, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                
                st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
                col_vid, col_act = st.columns([4, 1])
                
                with col_vid:
                    st.markdown(f"### @{p_user} · `{p_tag}`")
                    if p_cap: st.write(p_cap)
                    if p_file and isinstance(p_file, str) and os.path.exists(p_file):
                        st.video(p_file)
                
                with col_act:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button(f"🔥\n{p_fires if p_fires is not None else 0}", key=f"feed_fire_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'fire')
                    if st.button(f"👍\n{p_thumbs if p_thumbs is not None else 0}", key=f"feed_like_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'thumb')
                    if st.button(f"❤️\n{p_hearts if p_hearts is not None else 0}", key=f"feed_heart_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'heart')
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

    elif menu_option == "Mi Perfil":
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
            if avatar and isinstance(avatar, str) and os.path.exists(avatar):
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
        st.markdown("---")
        
        with st.expander("✏️ Publicar Contenido (Fotos o Vídeos)", expanded=False):
            with st.form("new_post_form", clear_on_submit=True):
                cap = st.text_input("¿Qué estás pensando?")
                uploaded_file = st.file_uploader("Sube foto (para tu perfil) o vídeo (para el feed general)", type=["jpg", "png", "mp4", "mov"])
                
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
                    
                    c.execute("INSERT INTO posts (username, caption, file, file_type, likes, fires, thumbs, hearts, vibe_tag, timestamp, privacy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                              (cur, cap, path_to_save, f_type, 0, 0, 0, 0, auto_tag, now_str, "Público"))
                    c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (cur,))
                    conn.commit()
                    st.success(f"¡Publicado! {ai_msg}")
                    st.rerun()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🖼️ Fotos (Tu Galería)", use_container_width=True):
                st.session_state.profile_tab = "Fotos"
        with col_btn2:
            if st.button("🎬 Vídeos", use_container_width=True):
                st.session_state.profile_tab = "Vídeos"

        st.markdown("---")

        if st.session_state.profile_tab == "Fotos":
            st.markdown("### 🖼️ Tus Fotos (Privadas o de perfil)")
            c.execute("SELECT id, caption, file, file_type, fires, thumbs, hearts, vibe_tag, timestamp FROM posts WHERE username = ? AND (file_type = 'image' OR file_type = '') ORDER BY id DESC", (cur,))
            for post in c.fetchall():
                p_id, p_cap, p_file, p_type, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap: st.write(p_cap)
                if p_file and isinstance(p_file, str) and os.path.exists(p_file): 
                    st.image(p_file, width=320)
                
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    if st.button(f"🔥 {p_fires if p_fires is not None else 0}", key=f"p_fire_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'fire')
                with col_r2:
                    if st.button(f"👍 {p_thumbs if p_thumbs is not None else 0}", key=f"p_like_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'thumb')
                with col_r3:
                    if st.button(f"❤️ {p_hearts if p_hearts is not None else 0}", key=f"p_heart_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'heart')
                st.markdown("---")
        else:
            st.markdown("### 🎬 Tus Vídeos")
            c.execute("SELECT id, caption, file, file_type, fires, thumbs, hearts, vibe_tag, timestamp FROM posts WHERE username = ? AND file_type = 'video' ORDER BY id DESC", (cur,))
            for post in c.fetchall():
                p_id, p_cap, p_file, p_type, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap: st.write(p_cap)
                if p_file and isinstance(p_file, str) and os.path.exists(p_file): 
                    st.video(p_file)
                
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    if st.button(f"🔥 {p_fires if p_fires is not None else 0}", key=f"pv_fire_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'fire')
                with col_r2:
                    if st.button(f"👍 {p_thumbs if p_thumbs is not None else 0}", key=f"pv_like_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'thumb')
                with col_r3:
                    if st.button(f"❤️ {p_hearts if p_hearts is not None else 0}", key=f"pv_heart_{p_id}", use_container_width=True):
                        handle_reaction(p_id, cur, 'heart')
                st.markdown("---")

    elif menu_option == "Buscar / Ver Perfiles":
        st.title("🔍 Buscar Perfiles")
        search_user = st.text_input("Escribe el nombre de usuario:")
        if search_user:
            c.execute("SELECT username, bio, avatar, account_privacy FROM users WHERE username = ?", (search_user,))
            target_user = c.fetchone()
            if target_user:
                t_user, t_bio, t_avatar, t_privacy = target_user
                st.markdown(f"### @{t_user}")
                st.write(t_bio)
                st.info(f"Tipo de cuenta: {t_privacy}")

    elif menu_option == "Siguiendo":
        st.title("👥 Siguiendo")
        st.write("Vídeos de la gente a la que sigues.")

    elif menu_option == "Explorar Canales":
        st.title("🔍 Explorar Canales")
        st.write("Tendencias y canales temáticos.")

    elif menu_option == "Mensajes":
        st.title("💬 Mensajes Directos")
        st.write("Tus chats privados.")

    elif menu_option == "Ajustes":
        st.title("⚙️ Ajustes de la cuenta")
        
        c.execute("SELECT bio, avatar, account_privacy FROM users WHERE username = ?", (cur,))
        u_settings = c.fetchone()
        current_bio = u_settings[0] if u_settings and u_settings[0] else ""
        current_acc_priv = u_settings[2] if u_settings and u_settings[2] else "Público"
        
        with st.form("settings_form"):
            new_bio = st.text_area("Actualizar tu biografía", value=current_bio)
            priv_index = 0 if current_acc_priv == "Público" else 1
            priv_choice = st.selectbox("Privacidad del Perfil", ["Público", "Privado"], index=priv_index)
            
            temas_disponibles = ["Oscuro (Por defecto)", "Claro", "Neón / Cyber"]
            current_theme_index = temas_disponibles.index(st.session_state.theme) if st.session_state.theme in temas_disponibles else 0
            new_theme = st.selectbox("🎨 Tema de Colores de la App", temas_disponibles, index=current_theme_index)
            
        
