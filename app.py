from datetime import datetime
import os
import sqlite3
import streamlit as st
import base64

def mostrar_video_con_elementos_superpuestos(video_file_path, username, status, vibe_tag):
    # 1. Leer y codificar el vídeo en base64 para usarlo en el reproductor HTML
    try:
        with open(video_file_path, "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de vídeo: {video_file_path}")
        return

    # 2. Estilos CSS personalizados para la superposición
    st.markdown(f"""
        <style>
        .video-container {{
            position: relative;
            width: 100%;
            max-width: 400px; /* Ajusta según el tamaño de tu móvil */
            margin-bottom: 20px;
            border-radius: 15px;
            overflow: hidden;
            background-color: black;
        }}
        .video-player {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .overlay-info {{
            position: absolute;
            bottom: 15px; /* Alineación abajo como en la foto */
            left: 15px;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
            z-index: 10;
        }}
        .live-label-container {{
            position: absolute;
            top: 15px; /* Alineación arriba */
            left: 15px;
            display: flex;
            gap: 10px;
            z-index: 10;
        }}
        .live-label {{
            background-color: #E91E63; /* Color rosa/magenta de "LIVE ahora" */
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9rem;
        }}
        .follow-btn {{
            background-color: rgba(255,255,255,0.3);
            color: white;
            border: 1px solid white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.9rem;
            cursor: pointer;
        }}
        .username {{
            font-size: 1.2rem;
            font-weight: bold;
        }}
        .status-text {{
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        .vibe-tag {{
            background-color: rgba(200, 230, 201, 0.7); /* Color del tag */
            color: #2E7D32;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
            margin-left: 5px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # 3. Estructura HTML del reproductor superpuesto
    st.markdown(f"""
        <div class="video-container">
            <video class="video-player" controls>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Tu navegador no soporta la etiqueta de vídeo.
            </video>
            
            <div class="live-label-container">
                <span class="live-label">🔴 LIVE ahora</span>
                <button class="follow-btn">Siguiendo</button>
            </div>
            
            <div class="overlay-info">
                <div class="username">@{username} <span class="vibe-tag">✨ {vibe_tag}</span></div>
                <div class="status-text">{status}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Ejemplo de uso dentro de tu bucle del feed de vídeos ---
# Reemplaza 'video_file_path', 'username', etc., con las variables reales de tu base de datos

# Ejemplo (simulando que esto está dentro de `for post in videos:`):
p_file = "ruta/a/tu/video.mp4" # Ruta al archivo de vídeo real
p_user = "Javimarquez"       # Nombre del usuario
p_cap = "UN DIA COMO POLICIA 🔥" # Título del vídeo
p_vibe = "Chill"             # Etiqueta de estado

mostrar_video_con_elementos_superpuestos(p_file, p_user, p_cap, p_vibe)

st.set_page_config(page_title="NoxVibe", page_icon="🧭", layout="centered")

conn = sqlite3.connect("noxvibe.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT, status TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS post_reactions (post_id INTEGER, username TEXT, reaction TEXT)")




columnas_usuarios = [
    ("nombre", "TEXT"),
    ("apellidos", "TEXT"),
    ("edad", "INTEGER"),
    ("email", "TEXT"),
    ("theme", "TEXT DEFAULT 'Oscuro'"),
    ("account_privacy", "TEXT DEFAULT 'Publico'"),
    ("coins", "INTEGER DEFAULT 100"),
    ("vibe", "TEXT DEFAULT '✨ Explorando noxvibe'"),
    ("badge", "TEXT"),
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
        "💬 Mensajes",
        "🛍️ Tienda Vibe",
        "🎁 Enviar Regalo",
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

    c.execute("""
        SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
        FROM posts p
        JOIN users u ON p.username = u.username
        WHERE p.file_type = 'video'
        ORDER BY p.id DESC
    """)
      
      
    videos = c.fetchall()

    if not videos:
      st.info("No hay videos publicos. Sube el primero desde tu perfil.")
    else:
         for post in videos:
            p_id, p_user, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
            
            # --- AQUÍ LLAMAS A NUESTRA FUNCIÓN ---
            mostrar_video_con_elementos_superpuestos(p_file, p_user, p_cap, p_tag)
            
            val_fires = p_fires if p_fires is not None else 0
            val_thumbs = p_thumbs if p_thumbs is not None else 0
            val_hearts = p_hearts if p_hearts is not None else 0
            
                
              col_vid, col_act = st.columns((4, 1))
              
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
            
            # --- PEGA ESTO AQUÍ SIN BORRAR NADA DE LO DEMÁS ---
               if st.button(
                "🌹 5C", key=f"feed_gift_{p_id}", use_container_width=True
            ):
              c.execute(
                  "SELECT coins FROM users WHERE username = ?",
                  (st.session_state.username,),
              )
              u_data = c.fetchone()
                  mis_c = (
                  u_data[0] if u_data and u_data[0] is not None else 0
              )

              if mis_c >= 5:
                c.execute(
                    "UPDATE users SET coins = ? WHERE username = ?",
                    (mis_c - 5, st.session_state.username),
                )
                c.execute(
                    "SELECT coins FROM users WHERE username = ?", (p_user,)
                )
                creador_data = c.fetchone()
                creador_c = (
                    creador_data[0]
                    if creador_data and creador_data[0] is not None
                    else 0
                )
                c.execute(
                    "UPDATE users SET coins = ? WHERE username = ?",
                    (creador_c + 5, p_user),
                )

                msg_regalo = (
                    "🎁 ¡Te ha enviado un regalo: 🌹 Rosa Vibe (5 Coins)! 🌹"
                )
                c.execute(
                    (
                        "INSERT INTO messages (sender, receiver, message) VALUES"
                        " (?, ?, ?)"
                    ),
                    (st.session_state.username, p_user, msg_regalo),
                )
                conn.commit()
                st.toast(f"¡Rosa enviada a @{p_user} con éxito! 🌹", icon="🎉")
                st.rerun()
              else:
                st.toast(
                    "¡No tienes suficientes Coins para enviar la Rosa!",
                    icon="⚠️",
                )
            # --------------------------------------------------

            st.markdown("</div>", unsafe_allow_html=True)  # Línea 337 original
            st.markdown("---")  # Línea 338 original
              
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")

  elif menu_option == "👤 Mi Perfil":
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
    nombre_completo = (
        f"{user_data[5]} {user_data[6]}" if user_data and user_data[5] else cur
    )

    priv_badge = (
        "🔒 Cuenta Privada"
        if account_privacy == "Privado"
        else "🌐 Cuenta Publica"
    )
    st.title(f"{nombre_completo} (@{cur})")
    st.caption(priv_badge)

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

  elif menu_option == "🔍 Buscar Perfiles":
    st.title("🔍 Buscar Perfiles")
    search_user = st.text_input("Escribe el nombre de usuario:")
    if search_user:
      c.execute(
          "SELECT username, bio, avatar, account_privacy FROM users WHERE"
          " username = ?",
          (search_user,),
      )
      target_user = c.fetchone()
      if target_user:
        t_username, t_bio, t_avatar, t_privacy = target_user
        st.success(f"Usuario encontrado: @{t_username}")
        st.write(f"**Biografía:** {t_bio}")

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
                  "INSERT INTO follows (follower, followed, status) VALUES (?,"
                  " ?, ?)",
                  (cur, t_username, "accepted"),
              )
              conn.commit()
              st.success(f"¡Ahora sigues a @{t_username}!")
              st.rerun()
      else:
         st.warning("Usuario no encontrado.")
if menu_option == "👥 Siguiendo":
    st.title("👥 Personas que sigues")
    c.execute("SELECT followed FROM follows WHERE follower = ?", (st.session_state.username,))
    siguiendo = c.fetchall()
    if siguiendo:
        for s in siguiendo:
            st.write(f"• @{s[0]}")
    else:
        st.info("Aún no sigues a nadie.")
if menu_option == "💬 Mensajes":
    st.title("💬 Mensajes y Chat")
    
    # 1. Elegir con quién chatear (buscamos usuarios que no seas tú)
    c.execute("SELECT username FROM users WHERE username != ?", (st.session_state.username,))
    usuarios_disponibles = [row[0] for row in c.fetchall()]
    
    if usuarios_disponibles:
        destinatario = st.selectbox("Selecciona un usuario para chatear:", usuarios_disponibles)
        
        st.markdown("---")
        st.subheader(f"Conversación con @{destinatario}")
        
        # 2. Cargar los mensajes entre tú y el destinatario
        c.execute("""
            SELECT sender, message, timestamp FROM messages 
            WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
            ORDER BY id ASC
        """, (st.session_state.username, destinatario, destinatario, st.session_state.username))
        
        mensajes = c.fetchall()
        
        # Mostrar los mensajes en pantalla
        chat_container = st.container()
        with chat_container:
            if mensajes:
                for remitente, texto, hora in mensajes:
                    if remitente == st.session_state.username:
                        st.markdown(f"**Tú:** {texto}")
                    else:
                        st.markdown(f"**@{remitente}:** {texto}")
            else:
                st.info("No hay mensajes todavía. ¡Escribe el primero!")
                
        # 3. Caja para escribir un nuevo mensaje
        nuevo_mensaje = st.text_input("Escribe tu mensaje...", key="input_mensaje")
        if st.button("Enviar mensaje"):
            if nuevo_mensaje.strip():
                c.execute(
                    "INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                    (st.session_state.username, destinatario, nuevo_mensaje)
                )
                conn.commit()
                st.success("¡Mensaje enviado!")
                st.rerun()
            else:
                st.warning("El mensaje no puede estar vacío.")
    else:
        st.info("Todavía no hay más usuarios registrados en la app para chatear.")
        
if menu_option == "🛍️ Tienda Vibe":
    st.title("🛍️ Tienda Vibe")
    st.write("¡Gasta tus Coins en insignias exclusivas y personaliza tu perfil con estilo!")
    
    # Consultar los coins actuales y la insignia del usuario
    c.execute("SELECT coins, badge FROM users WHERE username = ?", (st.session_state.username,))
    user_data = c.fetchone()
    mis_coins = user_data[0] if user_data and user_data[0] is not None else 0
    insignia_actual = user_data[1] if user_data and user_data[1] is not None else "Ninguna"
    
    col_info1, col_info2 = st.columns([2, 1])
    with col_info1:
        st.info(f"💰 Tienes **{mis_coins} Coins** | Insignia actual: **{insignia_actual}**")
    with col_info2:
        if st.button("🪙 Recargar Coins", key="recarga_coins_tienda_vibe"):
            st.warning("💳 Próximamente disponible: Recarga de Coins con pago real.")
            
    st.markdown("---")
    
    # Catálogo limpio con los nombres correctos y un solo icono
    articulos = {
        "Oráculo Cósmico": {"precio": 10, "icono": "🔮"},
        "Rayo Nocturno": {"precio": 25, "icono": "⚡"},
        "Corazón de Neón": {"precio": 50, "icono": "🖤"},
        "Corona Cyber": {"precio": 100, "icono": "👑"},
        "Platillo Volador": {"precio": 150, "icono": "🛸"},
        "Saturno Brillante": {"precio": 200, "icono": "🪐"},
        "Astronauta Estelar": {"precio": 300, "icono": "👩‍🚀"},
        "Estrella Fugaz": {"precio": 350, "icono": "🌠"},
        "Satélite Órbita": {"precio": 400, "icono": "🛰️"},
        "Agujero Negro": {"precio": 500, "icono": "🌌"},
        "Cohete Galáctico V1": {"precio": 1000, "icono": "🚀"},
        "Emperador Alienígena": {"precio": 1000, "icono": "👽"},
        "Cometa del Fin del Mundo": {"precio": 1000, "icono": "☄️"},
        "Supernova Legendaria": {"precio": 1000, "icono": "🌟"}
    }
    
    for i, (nombre_articulo, info) in enumerate(articulos.items()):
        nombre_completo = f"{info['icono']} {nombre_articulo}"
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"### {info['icono']} {nombre_articulo}")
        with col2:
            st.markdown(f"**{info['precio']} Coins**")
        with col3:
            if insignia_actual == nombre_completo:
                st.button("✅ Equipado", disabled=True, key=f"equipado_vibe_{i}")
            else:
                if st.button("Comprar", key=f"comprar_vibe_{i}"):
                    if mis_coins >= info['precio']:
                        nuevos_coins = mis_coins - info['precio']
                        c.execute("UPDATE users SET coins = ?, badge = ? WHERE username = ?", 
                                  (nuevos_coins, nombre_completo, st.session_state.username))
                        conn.commit()
                        st.success(f"¡Has comprado y equipado {nombre_articulo}!")
                        st.rerun()
                    else:
                        st.error("¡No tienes suficientes Coins! Recarga para conseguir más.")
                        
if menu_option == "🎁 Enviar Regalo":
    st.title("🎁 Enviar Regalo en Directo")
    st.write("¡Apoya a tus creadores favoritos enviándoles regalos durante sus directos con tus Coins!")
    
    # Consultar los coins actuales del usuario
    c.execute("SELECT coins FROM users WHERE username = ?", (st.session_state.username,))
    user_data = c.fetchone()
    mis_coins = user_data[0] if user_data and user_data[0] is not None else 0
    
    st.info(f"💰 Tienes **{mis_coins} Coins** disponibles para enviar.")
    
    # Seleccionar a qué usuario/streamer se le quiere regalar
    c.execute("SELECT username FROM users WHERE username != ?", (st.session_state.username,))
    usuarios_disponibles = [row[0] for row in c.fetchall()]
    
    if not usuarios_disponibles:
        st.warning("No hay otros usuarios registrados todavía para enviarles regalos.")
    else:
        streamer_destino = st.selectbox("Selecciona al creador o usuario en directo:", usuarios_disponibles)
        
        # Catálogo de regalos estilo TikTok / Streaming con iconos visuales
        regalos_directo = {
            "🌹 Rosa Vibe": {"precio": 5, "icono": "🌹"},
            "🔮 Oráculo Místico": {"precio": 10, "icono": "🔮"},
            "⚡ Rayo Flash": {"precio": 25, "icono": "⚡"},
            "🖤 Corazón Vibe": {"precio": 50, "icono": "🖤"},
            "👑 Corona Real": {"precio": 100, "icono": "👑"},
            "🎁 Caja Sorpresa": {"precio": 200, "icono": "🎁"},
            "🚀 Cohete Espacial": {"precio": 500, "icono": "🚀"},
            "🌟 Supernova": {"precio": 1000, "icono": "🌟"}
        }
        
        st.markdown("### Selecciona el regalo:")
        
        # Mostrar los regalos en columnas bonitas con sus iconos
        selected_regalo = st.selectbox("Regalos disponibles", list(regalos_directo.keys()))
        info_regalo = regalos_directo[selected_regalo]
        costo_regalo = info_regalo['precio']
        icono_regalo = info_regalo['icono']
        
        st.write(f"Costo: **{costo_regalo} Coins** {icono_regalo}")
        
        if st.button("🎁 Enviar Regalo en el Directo", key="btn_enviar_regalo_chat"):
            if mis_coins >= costo_regalo:
                # 1. Restar coins al usuario que envía
                nuevos_coins_remitente = mis_coins - costo_regalo
                c.execute("UPDATE users SET coins = ? WHERE username = ?", (nuevos_coins_remitente, st.session_state.username))
                
                # 2. Sumar los coins al streamer que recibe el regalo
                c.execute("SELECT coins FROM users WHERE username = ?", (streamer_destino,))
                streamer_data = c.fetchone()
                coins_streamer_actuales = streamer_data[0] if streamer_data and streamer_data[0] is not None else 0
                nuevos_coins_streamer = coins_streamer_actuales + costo_regalo
                c.execute("UPDATE users SET coins = ? WHERE username = ?", (nuevos_coins_streamer, streamer_destino))
                
                # 3. Guardar el evento del regalo como un mensaje en el chat del directo/mensajes para que se vea en pantalla
                mensaje_regalo = f"🎁 ¡Ha enviado el regalo **{selected_regalo}** ({costo_regalo} Coins)! {icono_regalo}"
                c.execute(
                    "INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                    (st.session_state.username, streamer_destino, mensaje_regalo)
                )
                
                conn.commit()
                st.success(f"¡Has enviado **{selected_regalo}** a **{streamer_destino}** con éxito! 🎉")
                st.balloons()
                st.rerun()
            else:
                st.error("¡No tienes suficientes Coins para enviar este regalo! Recarga más para continuar.")
                
                
                    
if menu_option == "⚙️ Ajustes":
    st.title("⚙️ Ajustes de la cuenta")
    c.execute("SELECT theme, account_privacy, vibe FROM users WHERE username = ?", (cur,))
    u_settings = c.fetchone()

    if u_settings:
        current_theme, current_privacy, current_vibe = u_settings
        if not current_vibe:
            current_vibe = "✨ Explorando noxvibe"

        new_theme = st.selectbox("Tema", ["Claro", "Oscuro"], index=0 if current_theme == "Claro" else 1)
        new_privacy = st.selectbox("Privacidad", ["Público", "Privado"], index=0 if current_privacy == "Público" else 1)
        new_vibe = st.text_input("Tu Vibe (Estado de ánimo / Emoji)", value=current_vibe)

        if st.button("Guardar cambios"):
            c.execute("UPDATE users SET theme = ?, account_privacy = ?, vibe = ? WHERE username = ?", (new_theme, new_privacy, new_vibe, st.session_state.username))
            conn.commit()
            st.success("¡Ajustes guardados con éxito!")
            st.rerun()
