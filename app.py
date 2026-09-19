from datetime import datetime
import os
import sqlite3
import streamlit as st

st.set_page_config(page_title="NoxVibe", page_icon="🧭", layout="centered")

conn = sqlite3.connect("noxvibe.db", check_same_thread=False)
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, xp INTEGER, bio TEXT, avatar TEXT)"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, vibe_tag TEXT, timestamp TEXT)"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT, status TEXT)"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS post_reactions (post_id INTEGER, username TEXT, reaction_type TEXT)"""
)
c.execute(
    """CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT)"""
)

columnas_usuarios = [
    ("nombre", "TEXT"),
    ("apellidos", "TEXT"),
    ("edad", "INTEGER"),
    ("email", "TEXT"),
    ("theme", "TEXT DEFAULT 'Oscuro'"),
    ("account_privacy", "TEXT DEFAULT 'Publico'"),
    ("coins", "INTEGER DEFAULT 100"),
]
for col_nombre, col_tipo in columnas_usuarios:
  try:
    c.execute(f"ALTER TABLE users ADD COLUMN {col_nombre} {col_tipo}")
  except:
    pass

columnas_posts = [
    ("fires", "INTEGER DEFAULT 0"),
    ("thumbs", "INTEGER DEFAULT 0"),
    ("hearts", "INTEGER DEFAULT 0"),
    ("privacy", "TEXT DEFAULT 'Publico'"),
]
for col_nombre, col_tipo in columnas_posts:
  try:
    c.execute(f"ALTER TABLE posts ADD COLUMN {col_nombre} {col_tipo}")
  except:
    pass

conn.commit()

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.profile_tab = "Fotos"
  st.session_state.theme = "Oscuro"

if st.session_state.logged_in and st.session_state.username:
  c.execute(
      "SELECT theme FROM users WHERE username = ?", (st.session_state.username,)
  )
  res_theme = c.fetchone()
  if res_theme and res_theme[0]:
    st.session_state.theme = res_theme[0]

if st.session_state.theme == "Claro":
  bg_color = "#ffffff"
  text_color = "#000000"
  box_bg = "#f0f2f6"
  sub_text = "#555555"
elif st.session_state.theme == "Neon / Cyber":
  bg_color = "#05050a"
  text_color = "#00ffcc"
  box_bg = "#121224"
  sub_text = "#ff007f"
else:
  bg_color = "#0e1117"
  text_color = "#ffffff"
  box_bg = "#161b22"
  sub_text = "#8b949e"

st.markdown(
    f"""
    <style>
    [data-testid="stToolbar"] a[href*="github"],
    header a[href*="github"] {{
        display: none !important;
    }}
    footer {{visibility: hidden !important;}}
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    div.stButton > button {{
        background-color: {box_bg} !important;
        color: {text_color} !important;
        border: 1px solid {sub_text} !important;
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
    """,
    unsafe_allow_html=True,
)


def ai_vibe_checker(text):
  if not text:
    return "✨ Chill", "Ambiente tranquilo detectado."
  t = text.lower()
  if any(w in t for w in ["fiesta", "noche", "baila", "dj", "alcohol", "musica"]):
    return "🎉 Fiesta", "Energia de fiesta detectada por la IA."
  elif any(w in t for w in ["amor", "corazon", "te amo", "feliz", "lindo"]):
    return "❤️ Hype / Amor", "Vibra positiva detectada."
  elif any(w in t for w in ["triste", "solo", "mal", "duro", "llorar"]):
    return "🌧️ Melancolico", "Momento de reflexion detectado."
  else:
    return "🚀 Inspirador", "Pensamiento innovador detectado."


def handle_reaction(p_id, user, r_type):
  c.execute(
      "SELECT * FROM post_reactions WHERE post_id = ? AND username = ? AND"
      " reaction_type = ?",
      (p_id, user, r_type),
  )
  if not c.fetchone():
    c.execute(
        "INSERT INTO post_reactions (post_id, username, reaction_type) VALUES"
        " (?, ?, ?)",
        (p_id, user, r_type),
    )
    if r_type == "fire":
      c.execute("UPDATE posts SET fires = fires + 1 WHERE id = ?", (p_id,))
    elif r_type == "thumb":
      c.execute("UPDATE posts SET thumbs = thumbs + 1 WHERE id = ?", (p_id,))
    elif r_type == "heart":
      c.execute("UPDATE posts SET hearts = hearts + 1 WHERE id = ?", (p_id,))
    conn.commit()
    st.rerun()
  else:
    st.toast("Ya habias dado esta reacción", icon="⚠️")


st.sidebar.title("🧭 Menu NoxVibe")
menu_option = st.sidebar.radio(
    "Navegacion",
    [
        "🔥 Feed de Videos",
        "👤 Mi Perfil",
        "🔍 Buscar Perfiles",
        "👥 Siguiendo",
        "📺 Explorar Canales",
        "💬 Mensajes",
        "⚙️ Ajustes",
    ],
)

if st.session_state.logged_in:
  c.execute(
      "SELECT coins FROM users WHERE username = ?", (st.session_state.username,)
  )
  res_coins = c.fetchone()
  user_coins = res_coins[0] if res_coins else 100

  st.sidebar.markdown(f"---")
  st.sidebar.success(f"Sesion: @{st.session_state.username}")
  st.sidebar.info(f"🪙 NoxCoins: **{user_coins}**")
  if st.sidebar.button("Cerrar Sesion"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

if not st.session_state.logged_in:
  st.title("Bienvenido a NoxVibe 🚀")

  tab_login, tab_reg = st.tabs(["🔑 Iniciar Sesion", "📝 Registrarse"])

  with tab_login:
    l_user = st.text_input("Usuario (o correo)", key="l_user")
    l_pass = st.text_input("Contrasena", type="password", key="l_pass")
    if st.button("Entrar"):
      c.execute(
          "SELECT * FROM users WHERE (username = ? OR email = ?) AND password ="
          " ?",
          (l_user, l_user, l_pass),
      )
      if c.fetchone():
        st.session_state.logged_in = True
        st.session_state.username = l_user
        st.rerun()
      else:
        st.error("Usuario o contrasena incorrectos")

  with tab_reg:
    r_user = st.text_input(
        "Nombre de Usuario (para iniciar sesion)", key="r_user"
    )
    r_nombre = st.text_input("Nombre", key="r_nombre")
    r_apellidos = st.text_input("Apellidos", key="r_apellidos")
    r_edad = st.number_input(
        "Edad", min_value=1, max_value=120, value=18, key="r_edad"
    )
    r_email = st.text_input("Correo Electronico", key="r_email")
    r_pass = st.text_input("Contrasena", type="password", key="r_pass")

    if st.button("Registrarse y Entrar"):
      if not r_user or not r_nombre or not r_email or not r_pass:
        st.warning("Por favor, rellena todos los campos obligatorios.")
      else:
        try:
          c.execute(
              "INSERT INTO users (username, password, nombre, apellidos, edad,"
              " email, xp, bio, avatar, account_privacy, coins, theme) VALUES"
              " (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (
                  r_user,
                  r_pass,
                  r_nombre,
                  r_apellidos,
                  int(r_edad),
                  r_email,
                  10,
                  "Hola! Uso NoxVibe.",
                  "",
                  "Publico",
                  100,
                  "Oscuro",
              ),
          )
          conn.commit()
          st.session_state.logged_in = True
          st.session_state.username = r_user
          st.success("¡Registro completado con éxito! Entrando...")
          st.rerun()
        except Exception as ex:
          st.error(f"El usuario o correo ya existe, o hubo un error: {ex}")

else:
  cur = st.session_state.username

if menu_option == "🔥 Feed de Videos":
    st.title("🔥 NoxVibe Feed")
    st.write("Videos publicos de la comunidad.")
    
    
    # Mostrar todos los videos ordenados del más nuevo al más antiguo
    c.execute("""
        SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
        FROM posts p 
        WHERE p.file_type = 'video' 
        ORDER BY p.id DESC
    """)
    posts = c.fetchall()
    
    if not posts:
      st.info("No hay videos publicados. Sube el primero desde tu perfil.")
    else:
      for post in posts:
        p_id, p_user, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
        val_fires = p_fires if p_fires is not None else 0
        val_thumbs = p_thumbs if p_thumbs is not None else 0
        val_hearts = p_hearts if p_hearts is not None else 0

        st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
        col_vid, col_act = st.columns([4, 1])

        with col_vid:
          st.markdown(f"### @{p_user} · `{p_tag}` ({p_time})")
          if p_cap:
            st.write(p_cap)
          if p_file and isinstance(p_file, str) and os.path.exists(p_file):
            st.video(p_file)

        with col_act:
          st.markdown("<br><br>", unsafe_allow_html=True)
          if st.button(f"🔥 {val_fires}", key=f"feed_fire_{p_id}", use_container_width=True):
            handle_reaction(p_id, cur, "fire")
          if st.button(f"👍 {val_thumbs}", key=f"feed_thumb_{p_id}", use_container_width=True):
            handle_reaction(p_id, cur, "thumb")
          if st.button(f"❤️ {val_hearts}", key=f"feed_heart_{p_id}", use_container_width=True):
            handle_reaction(p_id, cur, "heart")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
          
    c.execute("""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
            FROM posts p 
            JOIN users u ON p.username = u.username 
            WHERE p.file_type = 'video' AND u.account_privacy = 'Publico' 
            ORDER BY p.id DESC
        """)
    videos = c.fetchall()

    if not videos:
      st.info("No hay videos publicos. Sube el primero desde tu perfil.")
    else:
      for post in videos:
        (
            p_id,
            p_user,
            p_cap,
            p_file,
            p_fires,
            p_thumbs,
            p_hearts,
            p_tag,
            p_time,
        ) = post
        val_fires = p_fires if p_fires is not None else 0
        val_thumbs = p_thumbs if p_thumbs is not None else 0
        val_hearts = p_hearts if p_hearts is not None else 0

        st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
        col_vid, col_act = st.columns([4, 1])

        with col_vid:
          st.markdown(f"### @{p_user} · `{p_tag}`")
          if p_cap:
            st.write(p_cap)
          if p_file and isinstance(p_file, str) and os.path.exists(p_file):
            st.video(p_file)

        with col_act:
          st.markdown("<br><br>", unsafe_allow_html=True)
          if st.button(
              f"🔥 {val_fires}", key=f"feed_fire_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "fire")
          if st.button(
              f"👍 {val_thumbs}", key=f"feed_like_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "thumb")
          if st.button(
              f"❤️ {val_hearts}",
              key=f"feed_heart_{p_id}",
              use_container_width=True,
          ):
            handle_reaction(p_id, cur, "heart")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
elif menu_option == "👤 Mi Perfil":
    st.markdown(f"## {cur}")
    st.markdown(f"""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
    <img src="https://www.w3schools.com/howto/img_avatar.png" style="width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 2px solid #ff4b4b;">
    <div>
        <h2 style="margin: 0; font-size: 22px;">{cur}</h2>
        <p style="margin: 0; color: gray; font-size: 14px;">🌐 Cuenta Pública</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Contadores de estadísticas (alineados en horizontal)
st.markdown(f"""
<div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 15px;">
    <div>
        <span style="font-size: 14px; color: gray;">Posts</span><br>
        <span style="font-size: 20px; font-weight: bold;">{len(videos_usuario)}</span>
    </div>
    <div>
        <span style="font-size: 14px; color: gray;">Seguidores</span><br>
        <span style="font-size: 20px; font-weight: bold;">0</span>
    </div>
    <div>
        <span style="font-size: 14px; color: gray;">Siguiendo</span><br>
        <span style="font-size: 20px; font-weight: bold;">0</span>
    </div>
</div>
""", unsafe_allow_html=True)
     
st.markdown(f"**Tus XP:** 100 | **NoxCoins:** 10 🪙")

st.markdown("¡Hola! Estoy un Creator de Contenido y en especial GTAV Mod Policia")
st.markdown("---")
   
    
    # Botón para publicar contenido nuevo directamente desde el perfil
    if st.button("✏️ Publicar Contenido", use_container_width=True):
        # Aquí puedes poner la lógica o redirección para abrir el modal/sección de subida
        st.info("Usa el menú de publicación para subir nuevo contenido.")
        
    st.markdown("### Tus Vídeos")
    
    # Bucle para mostrar los vídeos de este usuario
    # (Asegúrate de usar aquí la lista filtrada solo con los posts de @Javimarquez)
    for post in videos_usuario:
        p_id, p_user_post, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
        st.markdown(f"**@{p_user_post}** · {p_time}")
        if p_cap:
            st.write(p_cap)
        if p_file and isinstance(p_file, str) and os.path.exists(p_file):
            st.video(p_file)
        st.markdown("---")
        
        
        st.markdown("### 🎬 Tus Videos")
        c.execute("""
            SELECT id, caption, file, fires, thumbs, hearts, vibe_tag, timestamp 
            FROM posts 
            WHERE username = ? AND file_type = 'video' 
            ORDER BY id DESC
        """, (cur,))
        my_posts = c.fetchall()
        
        if not my_posts:
            st.info("Aún no has subido ningún video.")
        else:
            for post in my_posts:
                p_id, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                val_fires = p_fires if p_fires is not None else 0
                val_thumbs = p_thumbs if p_thumbs is not None else 0
                val_hearts = p_hearts if p_hearts is not None else 0
                
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap:
                    st.write(p_cap)
                if p_file and isinstance(p_file, str) and os.path.exists(p_file):
                    st.video(p_file)
                st.markdown("---")
    else:
        st.warning("Usuario no encontrado.")
        
        st.markdown("### 🎬 Tus Videos")
        c.execute("""
            SELECT id, caption, file, fires, thumbs, hearts, vibe_tag, timestamp 
            FROM posts 
            WHERE username = ? AND file_type = 'video' 
            ORDER BY id DESC
        """, (cur,))
        my_posts = c.fetchall()
        
        if not my_posts:
            st.info("Aún no has subido ningún video.")
        else:
            for post in my_posts:
                p_id, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                val_fires = p_fires if p_fires is not None else 0
                val_thumbs = p_thumbs if p_thumbs is not None else 0
                val_hearts = p_hearts if p_hearts is not None else 0
                
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap:
                    st.write(p_cap)
                if p_file and isinstance(p_file, str) and os.path.exists(p_file):
                    st.video(p_file)
                st.markdown("---")
    
        
        
        st.markdown("### 🎬 Tus Videos")
        c.execute("""
            SELECT id, caption, file, fires, thumbs, hearts, vibe_tag, timestamp 
            FROM posts 
            WHERE username = ? AND file_type = 'video' 
            ORDER BY id DESC
        """, (cur,))
        my_posts = c.fetchall()
        
        if not my_posts:
            st.info("Aún no has subido ningún video.")
        else:
            for post in my_posts:
                p_id, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                val_fires = p_fires if p_fires is not None else 0
                val_thumbs = p_thumbs if p_thumbs is not None else 0
                val_hearts = p_hearts if p_hearts is not None else 0
                
                st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
                if p_cap:
                    st.write(p_cap)
                if p_file and isinstance(p_file, str) and os.path.exists(p_file):
                    st.video(p_file)
                st.markdown("---")
        
            
  
    c.execute(
        "SELECT xp, bio, avatar, account_privacy, coins, nombre, apellidos, edad"
        " FROM users WHERE username = ?",
        (cur,),
    )
    user_data = c.fetchone()
    xp = user_data[0] if user_data else 0
    bio = user_data[1] if user_data else ""
    avatar = user_data[2] if user_data else ""
    account_privacy = user_data[3] if user_data else "Publico"
    coins = user_data[4] if user_data else 100

    nombre_real = (
        f"{user_data[5]} {user_data[6]}" if user_data and user_data[5] else cur
    )
    priv_badge = (
        "🔒 Cuenta Privada"
        if account_privacy == "Privado"
        else "🌐 Cuenta Publica"
    )

    st.title(f"{nombre_real}")
    st.caption(f"@{cur} · {priv_badge}")

    c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (cur,))
    total_posts = c.fetchone()[0]

    try:
      c.execute(
          "SELECT COUNT(*) FROM follows WHERE followed = ? AND status ="
          " 'accepted'",
          (cur,),
      )
      total_followers = c.fetchone()[0]
      c.execute(
          "SELECT COUNT(*) FROM follows WHERE follower = ? AND status ="
          " 'accepted'",
          (cur,),
      )
      total_following = c.fetchone()[0]
    except:
      total_followers = 0
      total_following = 0

    col1, col2 = st.columns([1, 2])
    with col1:
      if avatar and isinstance(avatar, str) and os.path.exists(avatar):
        st.image(avatar, width=110) 
      else:
        st.image(
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
            width=110,
        )
    with col2:
      st.markdown(
          f"""
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
            """,
          unsafe_allow_html=True,
      )
      st.markdown(f"**Tus XP:** {xp} | **NoxCoins:** {coins} 🪙")

    st.write(bio)
    st.markdown("---")

    with st.expander("✏️ Publicar Contenido", expanded=False):
      with st.form("new_post_form", clear_on_submit=True):
        cap = st.text_input("Que estas pensando?")
        uploaded_file = st.file_uploader(
            "Sube foto o video", type=["jpg", "png", "mp4", "mov"]
        )

        if st.form_submit_button("Publicar 🚀"):
          path_to_save = ""
          f_type = ""
          if uploaded_file is not None:
            os.makedirs("uploads", exist_ok=True)
            path_to_save = os.path.join("uploads", uploaded_file.name)
            with open(path_to_save, "wb") as f:
              f.write(uploaded_file.getbuffer())
            f_type = (
                "video"
                if uploaded_file.type.startswith("video")
                else "image"
            )

          auto_tag, ai_msg = ai_vibe_checker(cap)
          now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

          c.execute(
              "INSERT INTO posts (username, caption, file, file_type, likes,"
              " fires, thumbs, hearts, vibe_tag, timestamp, privacy) VALUES (?,"
              " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (
                  cur,
                  cap,
                  path_to_save,
                  f_type,
                  0,
                  0,
                  0,
                  0,
                  auto_tag,
                  now_str,
                  "Publico",
              ),
          )
          c.execute(
              "UPDATE users SET xp = xp + 15 WHERE username = ?", (cur,)
          )
          conn.commit()
          st.success(f"Publicado! {ai_msg}")
          st.rerun()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
      if st.button("🖼️ Ver Fotos", use_container_width=True):
        st.session_state.profile_tab = "Fotos"
    with col_btn2:
      if st.button("🎬 Ver Videos", use_container_width=True):
        st.session_state.profile_tab = "Videos"

    st.markdown("---")

    if st.session_state.profile_tab == "Fotos":
      st.markdown("### 🖼️ Tus Fotos")
      c.execute(
          "SELECT id, caption, file, file_type, fires, thumbs, hearts,"
          " vibe_tag, timestamp FROM posts WHERE username = ? AND (file_type ="
          " 'image' OR file_type = '') ORDER BY id DESC",
          (cur,),
      )
      for post in c.fetchall():
        (
            p_id,
            p_cap,
            p_file,
            p_type,
            p_fires,
            p_thumbs,
            p_hearts,
            p_tag,
            p_time,
        ) = post
        val_f = p_fires if p_fires is not None else 0
        val_t = p_thumbs if p_thumbs is not None else 0
        val_h = p_hearts if p_hearts is not None else 0

        st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
        if p_cap:
          st.write(p_cap)
        if p_file and isinstance(p_file, str) and os.path.exists(p_file):
          st.image(p_file, width=320)

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
          if st.button(
              f"🔥 {val_f}", key=f"p_fire_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "fire")
        with col_r2:
          if st.button(
              f"👍 {val_t}", key=f"p_like_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "thumb")
        with col_r3:
          if st.button(
              f"❤️ {val_h}", key=f"p_heart_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "heart")
        st.markdown("---")
    else:
      st.markdown("### 🎬 Tus Videos")
      c.execute(
          "SELECT id, caption, file, file_type, fires, thumbs, hearts,"
          " vibe_tag, timestamp FROM posts WHERE username = ? AND file_type ="
          " 'video' ORDER BY id DESC",
          (cur,),
      )
      for post in c.fetchall():
        (
            p_id,
            p_cap,
            p_file,
            p_type,
            p_fires,
            p_thumbs,
            p_hearts,
            p_tag,
            p_time,
        ) = post
        val_f = p_fires if p_fires is not None else 0
        val_t = p_thumbs if p_thumbs is not None else 0
        val_h = p_hearts if p_hearts is not None else 0

        st.markdown(f"**@{cur}** · `{p_tag}` · {p_time}")
        if p_cap:
          st.write(p_cap)
        if p_file and isinstance(p_file, str) and os.path.exists(p_file):
          st.video(p_file)

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
          if st.button(
              f"🔥 {val_f}", key=f"pv_fire_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "fire")
        with col_r2:
          if st.button(
              f"👍 {val_t}", key=f"pv_like_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "thumb")
        with col_r3:
          if st.button(
              f"❤️ {val_h}", key=f"pv_heart_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "heart")
        st.markdown("---")
if menu_option == "🔍 Buscar Perfiles":
    st.title("🔍 Buscar Perfiles")
    search_user = st.text_input("Escribe el nombre de usuario a buscar")
    if search_user:
        c.execute(
            "SELECT username, bio, avatar, account_privacy FROM users WHERE username = ?",
            (search_user,),
        )
        target_user = c.fetchone()
        if target_user:
            t_username, t_bio, t_avatar, t_privacy = target_user
            st.success(f"Usuario encontrado: @{t_username}")
            st.write(f"**Biografía:** {t_bio if t_bio else 'Sin biografía'}")
            
            if t_username == cur:
                st.info("Este es tu propio perfil.")
            else:
                c.execute(
                    "SELECT status FROM follows WHERE follower = ? AND followed = ?",
                    (cur, t_username),
                )
                relacion = c.fetchone()
                
                if relacion:
                    st.info(f"Estado de amistad: {relacion[0]}")
                    if st.button("❌ Dejar de seguir"):
                        c.execute(
                            "DELETE FROM follows WHERE follower = ? AND followed = ?",
                            (cur, t_username),
                        )
                        conn.commit()
                        st.success("Has dejado de seguir a este usuario.")
                        st.rerun()
                else:
                    if st.button("➕ Añadir de Amiga / Seguir"):
                        c.execute(
                            "INSERT INTO follows (follower, followed, status) VALUES (?, ?, ?)",
                            (cur, t_username, "accepted"),
                        )
                        conn.commit()
                        st.success(f"¡Ahora sigues a @{t_username}!")
                        st.rerun()
        else:
            st.warning("No se encontró ningún usuario con ese nombre.")
            
  
elif menu_option == "👥 Siguiendo":
    st.title("👥 Siguiendo")
    st.write("Videos recientes de la gente a la que sigues.")
    
    c.execute("SELECT followed FROM follows WHERE follower = ? AND status = 'accepted'", (cur,))
    siguiendo = [r[0] for r in c.fetchall()]
    
    if not siguiendo:
      st.info("Aún no sigues a nadie. ¡Busca perfiles y añádelos para ver sus videos aquí!")
    else:
      placeholders = ','.join(['?'] * len(siguiendo))
      query = f"""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
            FROM posts p 
            WHERE p.file_type = 'video' AND p.username IN ({placeholders}) 
            ORDER BY p.id DESC
      """
      c.execute(query, siguiendo)
      videos_amigos = c.fetchall()
      
      if not videos_amigos:
        st.info("La gente a la que sigues aún no ha subido ningún video.")
      else:
        for post in videos_amigos:
          p_id, p_user, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
            
          val_fires = p_fires if p_fires is not None else 0
          val_thumbs = p_thumbs if p_thumbs is not None else 0
          val_hearts = p_hearts if p_hearts is not None else 0

          st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
          col_vid, col_act = st.columns([4, 1])

          with col_vid:
            st.markdown(f"### @{p_user} · `{p_tag}`")
            if p_cap:
              st.write(p_cap)
            if p_file and isinstance(p_file, str) and os.path.exists(p_file):
                          import base64
            with open(p_file, "rb") as f:
                video_bytes = f.read()
            video_base64 = base64.b64encode(video_bytes).decode()
            
            video_html = f"""
                <video width="100%" autoplay loop muted playsinline style="border-radius: 10px;">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Tu navegador no soporta el elemento de video.
                </video>
            """
            st.markdown(video_html, unsafe_allow_html=True)
              

          with col_act:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button(f"🔥 {val_fires}", key=f"f_fire_{p_id}", use_container_width=True):
              handle_reaction(p_id, cur, "fire")
            if st.button(f"👍 {val_thumbs}", key=f"f_like_{p_id}", use_container_width=True):
              handle_reaction(p_id, cur, "thumb")
            if st.button(f"❤️ {val_hearts}", key=f"f_heart_{p_id}", use_container_width=True):
              handle_reaction(p_id, cur, "heart")

          st.markdown("</div>", unsafe_allow_html=True)
          st.markdown("---")

elif menu_option == "📺 Explorar Canales":
    st.title("📺 Explorar Canales por Categoría")
    
    canales = ["Todos", "✨ Chill", "🎉 Fiesta", "❤️ Hype / Amor", "🌧️ Melancolico", "🚀 Inspirador"]
    canal_sel = st.selectbox("Elige un canal:", canales)
    
    if canal_sel == "Todos":
      c.execute("""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
            FROM posts p 
            JOIN users u ON p.username = u.username 
            WHERE p.file_type = 'video' AND u.account_privacy = 'Publico' 
            ORDER BY p.id DESC
      """)
    else:
      c.execute("""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
            FROM posts p 
            JOIN users u ON p.username = u.username 
            WHERE p.file_type = 'video' AND u.account_privacy = 'Publico' AND p.vibe_tag = ? 
            ORDER BY p.id DESC
      """, (canal_sel,))
      
    videos_canal = c.fetchall()
    
    if not videos_canal:
      st.info(f"No hay videos públicos en el canal '{canal_sel}' todavía.")
    else:
      for post in videos_canal:
        p_id, p_user, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
        val_fires = p_fires if p_fires is not None else 0
        val_thumbs = p_thumbs if p_thumbs is not None else 0
        val_hearts = p_hearts if p_hearts is not None else 0

        st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
        col_vid, col_act = st.columns([4, 1])

        with col_vid:
          st.markdown(f"### @{p_user} · `{p_tag}`")
          if p_cap:
            st.write(p_cap)
          if p_file and isinstance(p_file, str) and os.path.exists(p_file):
            st.video(p_file)

        with col_act:
          st.markdown("<br><br>", unsafe_allow_html=True)
          if st.button(f"🔥 {val_fires}", key=f"c_fire_{p_id}", use_container_width=True):
            handle_reaction(p_id, cur, "fire")
          if st.button(f"👍 {val_thumbs}", key=f"c_like_{p_id}", use_container_width=True):
            handle_reaction(p_id, cur, "thumb")
          if st.button(f"❤️ {val_hearts}", key=f"c_heart_{p_id}", use_container_width=True):
            handle_reaction(p_id, cur, "heart")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
          
          

elif menu_option == "💬 Mensajes":
    st.title("💬 Tus Mensajes")
    c.execute(
        "SELECT DISTINCT sender FROM messages WHERE receiver = ? UNION SELECT"
        " DISTINCT receiver FROM messages WHERE sender = ?",
        (cur, cur),
    )
    res_contactos = c.fetchall()
    contactos = [r[0] for r in res_contactos] if res_contactos else []

    chat_con = st.selectbox("Selecciona un usuario para chatear", [""] + contactos)

    if chat_con:
      st.markdown(f"### Chat con @{chat_con}")
      c.execute(
          "SELECT sender, message, timestamp FROM messages WHERE (sender = ?"
          " AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC",
          (cur, chat_con, chat_con, cur),
      )
      mensajes = c.fetchall()

      for m_sender, m_text, m_time in mensajes:
        if m_sender == cur:
          st.markdown(f"**Tú ({m_time}):** {m_text}")
        else:
          st.markdown(f"**@{m_sender} ({m_time}):** {m_text}")

      nuevo_msg = st.text_input("Escribe tu mensaje...")
      if st.button("Enviar Mensaje 🚀"):
        if nuevo_msg:
          now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
          c.execute(
              "INSERT INTO messages (sender, receiver, message, timestamp)"
              " VALUES (?, ?, ?, ?)",
              (cur, chat_con, nuevo_msg, now_str),
          )
          conn.commit()
          st.success("¡Mensaje enviado!")
          st.rerun()

elif menu_option == "⚙️ Ajustes":
    st.title("⚙️ Ajustes de la cuenta")

    c.execute(
        "SELECT theme, account_privacy FROM users WHERE username = ?", (cur,)
    )
    u_settings = c.fetchone()

    current_db_theme = (
        u_settings[0]
        if u_settings and u_settings[0] is not None
        else "Oscuro"
    )
    current_privacy = (
        u_settings[1]
        if u_settings and len(u_settings) > 1 and u_settings[1] is not None
        else "Publico"
    )

    st.subheader("🎨 Apariencia y Privacidad")

    opciones_temas = ["Oscuro", "Claro", "Neon / Cyber"]
    idx_tema = (
        opciones_temas.index(current_db_theme)
        if current_db_theme in opciones_temas
        else 0
    )
    tema_sel = st.selectbox("Tema de Colores", opciones_temas, index=idx_tema)

    opciones_priv = ["Publico", "Privado"]
    idx_priv = (
        opciones_priv.index(current_privacy)
        if current_privacy in opciones_priv
        else 0
    )
    priv_sel = st.selectbox(
        "Privacidad de la Cuenta", opciones_priv, index=idx_priv
    )

    if st.button("Guardar Cambios de Ajustes"):
      c.execute(
          "UPDATE users SET theme = ?, account_privacy = ? WHERE username = ?",
          (tema_sel, priv_sel, cur),
      )
      conn.commit()
      st.session_state.theme = tema_sel
      st.success("¡Ajustes actualizados con éxito!")
      st.rerun()
        
