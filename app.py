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
    """CREATE_TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT)"""
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
  st.session_state.nav_tab = "Inicio"
  st.session_state.theme = "Oscuro"
if "create_menu_open" not in st.session_state:
  st.session_state.create_menu_open = False
if "create_action" not in st.session_state:
  st.session_state.create_action = None

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
        border-radius: 8px;
    }}
    .video-container {{
        position: relative;
        background: {box_bg};
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    .profile-avatar img {{
        border-radius: 50% !important;
        object-fit: cover !important;
        width: 110px !important;
        height: 110px !important;
    }}
    .creation-popup {{
        background-color: {box_bg};
        border: 1px solid {sub_text};
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-align: center;
    }}
    .stats-container {{
        display: flex;
        gap: 25px;
        margin-top: 8px;
        margin-bottom: 8px;
    }}
    .stat-box-item {{
        display: flex;
        flex-direction: column;
    }}
    .stat-num {{
        font-weight: bold;
        font-size: 16px;
    }}
    .stat-label {{
        font-size: 13px;
        color: {sub_text};
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
      "SELECT * FROM post_reactions WHERE post_id = ? AND username = ? AND reaction_type = ?",
      (p_id, user, r_type),
  )
  if not c.fetchone():
    c.execute(
        "INSERT INTO post_reactions (post_id, username, reaction_type) VALUES (?, ?, ?)",
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
if st.session_state.logged_in:
  c.execute(
      "SELECT coins, xp FROM users WHERE username = ?",
      (st.session_state.username,),
  )
  res_user_info = c.fetchone()
  user_coins = res_user_info[0] if res_user_info else 100
  user_xp = res_user_info[1] if res_user_info else 0

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
          "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
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
      if not r_user or not r_pass:
        st.warning("Por favor, introduce al menos tu usuario y contraseña.")
      else:
        try:
          c.execute(
              "INSERT INTO users (username, password, nombre, apellidos, edad, email, xp, bio, avatar, account_privacy, coins, theme) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (
                  r_user,
                  r_pass,
                  r_nombre,
                  r_apellidos,
                  int(r_edad),
                  r_email,
                  10,
                  "¡Hola! Uso NoxVibe.",
                  "",
                  "Publico",
                  100,
                  "Oscuro",
              ),
          )
          conn.commit()
          st.success("¡Cuenta creada con éxito!")
          st.session_state.logged_in = True
          st.session_state.username = r_user
          st.rerun()
        except Exception as e:
          st.error(f"Error al registrar: {e}")

else:
  cur = st.session_state.username

  c.execute("SELECT COUNT(*) FROM posts WHERE username COLLATE NOCASE = ?", (cur,))
  num_posts = c.fetchone()[0]

  c.execute(
      "SELECT COUNT(*) FROM follows WHERE followed COLLATE NOCASE = ? AND status = 'accepted'",
      (cur,),
  )
  num_followers = c.fetchone()[0]

  c.execute(
      "SELECT COUNT(*) FROM follows WHERE follower COLLATE NOCASE = ? AND status = 'accepted'",
      (cur,),
  )
  num_following = c.fetchone()[0]

  c.execute(
      "SELECT avatar, nombre, apellidos, coins FROM users WHERE username COLLATE NOCASE = ?",
      (cur,),
  )
  u_info = c.fetchone()
  u_av = u_info[0] if (u_info and u_info[0]) else ""
  u_name = f"{u_info[1] or ''} {u_info[2] or ''}".strip() if u_info else ""
  if not u_name:
    u_name = "Javi Márquez"
  u_coins = u_info[3] if u_info else 100

  col_top_img, col_top_txt = st.columns([1, 3])
  with col_top_img:
    if u_av and os.path.exists(u_av):
      st.image(u_av, width=60)
    else:
      st.markdown("👤")
  with col_top_txt:
    st.markdown(f"**{u_name}**  \n`@{cur}` | 🪙 **{u_coins} Coins**")
    st.markdown(
        f"""
        <div class="stats-container">
            <div class="stat-box-item">
                <span class="stat-num">{num_posts}</span>
                <span class="stat-label">publicaciones</span>
            </div>
            <div class="stat-box-item">
                <span class="stat-num">{num_followers}</span>
                <span class="stat-label">seguidores</span>
            </div>
            <div class="stat-box-item">
                <span class="stat-num">{num_following}</span>
                <span class="stat-label">seguidos</span>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

  st.markdown("---")

  current_nav = st.session_state.get("nav_tab", "Inicio")

  if current_nav == "Inicio":
    st.title("🏠 Feed Principal")
    st.write("Explora las últimas publicaciones y videos de la comunidad.")

    c.execute("""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag, p.timestamp 
            FROM posts p 
            JOIN users u ON p.username COLLATE NOCASE = u.username COLLATE NOCASE 
            WHERE u.account_privacy = 'Publico' 
            ORDER BY p.id DESC
        """)
    posts = c.fetchall()

    if not posts:
      st.info("No hay publicaciones todavía.")
    else:
      for post in posts:
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
        st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
        st.markdown(f"### @{p_user} · `{p_tag}`")
        if p_cap:
          st.write(p_cap)
        if p_file and os.path.exists(p_file):
          if p_file.endswith((".mp4", ".mov")):
            st.video(p_file)
          else:
            st.image(p_file, width=400)

        if p_user.lower() == cur.lower():
          if st.button("🗑️ Eliminar publicación", key=f"del_post_{p_id}"):
            if p_file and os.path.exists(p_file):
              try:
                os.remove(p_file)
              except:
                pass
            c.execute("DELETE FROM posts WHERE id = ?", (p_id,))
            c.execute("DELETE FROM post_reactions WHERE post_id = ?", (p_id,))
            conn.commit()
            st.success("¡Publicación eliminada con éxito!")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

  elif current_nav == "Shorts":
    st.title("🎞️ NoxVibe Shorts")
    st.write("Videos cortos y verticales de la comunidad.")

    c.execute("""
            SELECT p.id, p.username, p.caption, p.file, p.fires, p.thumbs, p.hearts, p.vibe_tag 
            FROM posts p 
            JOIN users u ON p.username COLLATE NOCASE = u.username COLLATE NOCASE 
            WHERE p.file_type = 'video' AND u.account_privacy = 'Publico' 
            ORDER BY p.id DESC
        """)
    videos = c.fetchall()

    if not videos:
      st.info("No hay shorts disponibles en este momento.")
    else:
      for post in videos:
        (
            p_id,
            p_user,
            p_cap,
            p_file,
            val_fires,
            val_thumbs,
            val_hearts,
            p_tag,
        ) = post
        val_fires = val_fires or 0
        val_thumbs = val_thumbs or 0
        val_hearts = val_hearts or 0

        st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
        col_vid, col_act = st.columns([4, 1])
        with col_vid:
          st.markdown(f"### @{p_user} · `{p_tag}`")
          if p_cap:
            st.write(p_cap)
          if p_file and os.path.exists(p_file):
            st.video(p_file)

          if p_user.lower() == cur.lower():
            if st.button("🗑️ Eliminar short", key=f"del_short_{p_id}"):
              if p_file and os.path.exists(p_file):
                try:
                  os.remove(p_file)
                except:
                  pass
              c.execute("DELETE FROM posts WHERE id = ?", (p_id,))
              c.execute("DELETE FROM post_reactions WHERE post_id = ?", (p_id,))
              conn.commit()
              st.success("¡Short eliminado con éxito!")
              st.rerun()

        with col_act:
          st.markdown("<br><br>", unsafe_allow_html=True)
          if st.button(
              f"🔥 {val_fires}", key=f"s_fire_{p_id}", use_container_width=True
          ):
            handle_reaction(p_id, cur, "fire")
          if st.button(
              f"👍 {val_thumbs}",
              key=f"s_thumb_{p_id}",
              use_container_width=True,
          ):
            handle_reaction(p_id, cur, "thumb")
          if st.button(
              f"❤️ {val_hearts}",
              key=f"s_heart_{p_id}",
              use_container_width=True,
          ):
            handle_reaction(p_id, cur, "heart")
        st.markdown("</div>", unsafe_allow_html=True)

  elif current_nav == "Crear":
    st.title("➕ Crear Contenido")
    st.write("Elige qué tipo de formato deseas subir o retransmitir:")

    st.markdown('<div class="creation-popup">', unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
    with c_btn1:
      if st.button("Vídeo", use_container_width=True):
        st.session_state.create_action = "Vídeo"
    with c_btn2:
      if st.button("Short", use_container_width=True):
        st.session_state.create_action = "Short"
    with c_btn3:
      if st.button("Directo", use_container_width=True):
        st.session_state.create_action = "Directo"
    with c_btn4:
      if st.button("Publicar", use_container_width=True):
        st.session_state.create_action = "Publicar"
    st.markdown("</div>", unsafe_allow_html=True)

    accion_actual = st.session_state.get("create_action", "Publicar")
    st.info(f"Modo seleccionado: **{accion_actual}**")

    with st.form("new_post_form_nav", clear_on_submit=True):
      cap = st.text_input(f"Escribe algo para tu {accion_actual.lower()}...")
      uploaded_file = st.file_uploader(
          "Sube tu archivo multimedia", type=["jpg", "png", "mp4", "mov"]
      )
      submitted = st.form_submit_button(
          f"Confirmar y {accion_actual} 🚀", use_container_width=True
      )

      if submitted:
        path_to_save = ""
        f_type = (
            "video"
            if accion_actual in ["Vídeo", "Short", "Directo"]
            else "image"
        )
        if uploaded_file is not None:
          os.makedirs("uploads", exist_ok=True)
          path_to_save = os.path.join("uploads", uploaded_file.name)
          with open(path_to_save, "wb") as f:
            f.write(uploaded_file.getbuffer())

        auto_tag, ai_msg = ai_vibe_checker(cap)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        c.execute(
            "INSERT INTO posts (username, caption, file, file_type, likes, fires, thumbs, hearts, vibe_tag, timestamp, privacy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
            "UPDATE users SET xp = xp + 15 WHERE username COLLATE NOCASE = ?",
            (cur,),
        )
        conn.commit()
        st.success(f"¡{accion_actual} creado con éxito! {ai_msg}")

  elif current_nav == "Suscripciones":
    st.title("📺 Suscripciones y Amigos")

    st.subheader("🔍 Buscar Nuevos Amigos")
    busqueda_usuario = st.text_input("Escribe el nombre de usuario...")

    if busqueda_usuario:
      c.execute(
          "SELECT username, nombre, avatar FROM users WHERE username LIKE ? AND username COLLATE NOCASE != ?",
          (f"%{busqueda_usuario}%", cur),
      )
      resultados = c.fetchall()
      if resultados:
        for r_user, r_nombre, r_av in resultados:
          col_u1, col_u2 = st.columns([3, 1])
          with col_u1:
            st.write(f"**@{r_user}** ({r_nombre or 'Sin nombre'})")
          with col_u2:
            c.execute(
                "SELECT status FROM follows WHERE follower COLLATE NOCASE = ? AND followed COLLATE NOCASE = ?",
                (cur, r_user),
            )
            estado_follow = c.fetchone()
            if not estado_follow:
              if st.button("Seguir ➕", key=f"follow_{r_user}"):
                c.execute(
                    "INSERT INTO follows (follower, followed, status) VALUES (?, ?, 'accepted')",
                    (cur, r_user),
                )
                conn.commit()
                st.success(f"¡Ahora sigues a @{r_user}!")
                st.rerun()
            else:
              st.write("✅ Siguiendo")
      else:
        st.info("No se ha encontrado a ningún usuario con ese nombre.")

    st.markdown("---")
    st.subheader("👥 Canales que sigues")
    c.execute(
        "SELECT followed FROM follows WHERE follower COLLATE NOCASE = ? AND status = 'accepted'",
        (cur,),
    )
    seguidos = c.fetchall()
    if not seguidos:
      st.info("No sigues a ningún canal todavía.")
    else:
      for s in seguidos:
        st.write(f"👤 Canal de @{s[0]}")
  elif current_nav == "Mensajes":
    st.title("💬 Mensajería Privada")
    st.write("Busca a un usuario de NoxVibe y chatea con él en tiempo real.")

    # Buscador de usuarios para chatear
    busq_chat = st.text_input(
        "🔍 Buscar usuario para enviar mensaje...", key="input_busq_chat"
    )

    amigo_seleccionado = None

    if busq_chat:
      c.execute(
          "SELECT username, nombre FROM users WHERE username LIKE ? AND username COLLATE NOCASE != ?",
          (f"%{busq_chat}%", cur),
      )
      encontrados = c.fetchall()
      if encontrados:
        for u_user, u_nom in encontrados:
          if st.button(f"Chatear con @{u_user} ({u_nom or ''})"):
            st.session_state.chat_with = u_user
            st.rerun()
      else:
        st.info("No se encontró ningún usuario con ese nombre.")

    # Si hay un chat activo seleccionado
    if "chat_with" not in st.session_state:
      st.session_state.chat_with = ""

    # Mostrar lista rápida de gente con la que ya has hablado
    c.execute(
        """
            SELECT DISTINCT CASE WHEN sender = ? THEN receiver ELSE sender END 
            FROM messages WHERE sender = ? OR receiver = ?
        """,
        (cur, cur, cur),
    )
    chats_previos = c.fetchall()

    if chats_previos and not st.session_state.chat_with:
      st.markdown("### Tus conversaciones recientes:")
      for cp in chats_previos:
        if st.button(f"💬 Chat con @{cp[0]}"):
          st.session_state.chat_with = cp[0]
          st.rerun()

    if st.session_state.chat_with:
      chat_target = st.session_state.chat_with
      st.markdown("---")
      col_ch_t1, col_ch_t2 = st.columns([3, 1])
      with col_ch_t1:
        st.subheader(f"Chat con @{chat_target}")
      with col_ch_t2:
        if st.button("❌ Cerrar chat"):
          st.session_state.chat_with = ""
          st.rerun()

      # Mostrar mensajes de la base de datos
      c.execute(
          """
                SELECT sender, message, timestamp FROM messages 
                WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) 
                ORDER BY id ASC
            """,
          (cur, chat_target, chat_target, cur),
      )
      mensajes = c.fetchall()

      chat_container = st.container()
      with chat_container:
        if not mensajes:
          st.info(
              f"No hay mensajes aún con @{chat_target}. ¡Escribe el primero!"
          )
        else:
          for m_sender, m_text, m_time in mensajes:
            if m_sender.lower() == cur.lower():
              st.markdown(
                  f"<div style='text-align: right; background-color: #1f6feb; color: white; padding: 8px 12px; border-radius: 10px; margin: 5px 0; margin-left: 20%;'><b>Tú:</b> {m_text}<br><span style='font-size: 10px; opacity: 0.7;'>{m_time}</span></div>",
                  unsafe_allow_html=True,
              )
            else:
              st.markdown(
                  f"<div style='text-align: left; background-color: #30363d; color: white; padding: 8px 12px; border-radius: 10px; margin: 5px 0; margin-right: 20%;'><b>@{m_sender}:</b> {m_text}<br><span style='font-size: 10px; opacity: 0.7;'>{m_time}</span></div>",
                  unsafe_allow_html=True,
              )

      # Caja para enviar nuevo mensaje
      with st.form("form_enviar_mensaje", clear_on_submit=True):
        nuevo_texto_msg = st.text_input("Escribe tu mensaje...")
        enviar_msg_btn = st.form_submit_button(
            "Enviar mensaje 📨", use_container_width=True
        )

        if enviar_msg_btn and nuevo_texto_msg.strip():
          t_actual = datetime.now().strftime("%H:%M")
          c.execute(
              "INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)",
              (cur, chat_target, nuevo_texto_msg.strip(), t_actual),
          )
          conn.commit()
          st.rerun()
            
  elif current_nav == "Tu":
    st.title("👤 Tu Perfil Completo")
    c.execute(
        "SELECT avatar, nombre, apellidos, bio FROM users WHERE username COLLATE NOCASE = ?",
        (cur,),
    )
    user_data = c.fetchone()
    avatar_path = user_data[0] if (user_data and user_data[0]) else ""
    nombre_completo = f"{user_data[1] or ''} {user_data[2] or ''}".strip()
    if not nombre_completo:
      nombre_completo = "Javi Márquez"
    bio_texto = (
        user_data[3]
        if (user_data and user_data[3])
        else "¡Bienvenidos a mi perfil en NoxVibe!"
    )

    col_av_img, col_av_txt = st.columns([1, 2])

    with col_av_img:
      st.markdown('<div class="profile-avatar">', unsafe_allow_html=True)
      if avatar_path and os.path.exists(avatar_path):
        st.image(avatar_path, width=110)
      else:
        st.markdown(
            """
                <div style="width: 110px; height: 110px; background-color: #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px; color: #fff; margin: 0 auto;">
                    👤
                </div>
            """,
            unsafe_allow_html=True,
        )
      st.markdown("</div>", unsafe_allow_html=True)

    with col_av_txt:
      st.markdown(f"### {nombre_completo}")
      st.markdown(
          f"<p style='color: #aaa; margin-top: -10px;'>@{cur}</p>",
          unsafe_allow_html=True,
      )

      st.markdown(
          f"""
            <div class="stats-container">
                <div class="stat-box-item">
                    <span class="stat-num">{num_posts}</span>
                    <span class="stat-label">publicaciones</span>
                </div>
                <div class="stat-box-item">
                    <span class="stat-num">{num_followers}</span>
                    <span class="stat-label">seguidores</span>
                </div>
                <div class="stat-box-item">
                    <span class="stat-num">{num_following}</span>
                    <span class="stat-label">seguidos</span>
                </div>
            </div>
        """,
          unsafe_allow_html=True,
      )

      if "edit_avatar_open" not in st.session_state:
        st.session_state.edit_avatar_open = False

      if st.button("✏️ Cambiar foto de perfil"):
        st.session_state.edit_avatar_open = (
            not st.session_state.edit_avatar_open
        )

      if st.session_state.edit_avatar_open:
        new_avatar = st.file_uploader(
            "Sube tu foto",
            type=["jpg", "png", "jpeg"],
            key="upload_avatar_real",
        )
        if new_avatar is not None:
          os.makedirs("uploads", exist_ok=True)
          av_path = os.path.join("uploads", f"avatar_{cur}_{new_avatar.name}")
          with open(av_path, "wb") as f:
            f.write(new_avatar.getbuffer())
          c.execute(
              "UPDATE users SET avatar = ? WHERE username COLLATE NOCASE = ?",
              (av_path, cur),
          )
          conn.commit()
          st.session_state.edit_avatar_open = False
          st.success("¡Foto actualizada!")
          st.rerun()

  c.execute(
      "SELECT bio FROM users WHERE username COLLATE NOCASE = ?", (cur,)
  )
  res_bio = c.fetchone()
  bio_texto = (
      res_bio[0]
      if (res_bio and res_bio[0])
      else "¡Bienvenidos a mi perfil en NoxVibe!"
  )

  st.write("")
  st.write(bio_texto)
  st.markdown("---")

  st.subheader("⚙️ Opciones de Cuenta")
  nuevo_tema = st.selectbox(
      "Tema visual",
      ["Oscuro", "Claro", "Neon / Cyber"],
      index=(
          0
          if st.session_state.get("theme", "Oscuro") == "Oscuro"
          else (1 if st.session_state.get("theme") == "Claro" else 2)
      ),
  )
  if st.button("Guardar Ajustes de Tema"):
    c.execute(
        "UPDATE users SET theme = ? WHERE username COLLATE NOCASE = ?",
        (nuevo_tema, cur),
    )
    conn.commit()
    st.success("¡Tema guardado!")
    st.rerun()

# ==========================================
# MENÚ DE NAVEGACIÓN ABAJO DEL TODO
# ==========================================
st.markdown("---")
st.markdown("### 🧭 Menú de Navegación")

col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
with col_m1:
  if st.button("🏠", use_container_width=True, help="Inicio"):
    st.session_state.nav_tab = "Inicio"
    st.rerun()
with col_m2:
  if st.button("🎞️", use_container_width=True, help="Shorts"):
    st.session_state.nav_tab = "Shorts"
    st.rerun()
with col_m3:
  if st.button("➕", use_container_width=True, help="Crear"):
    st.session_state.nav_tab = "Crear"
    st.rerun()
with col_m4:
  if st.button("📺", use_container_width=True, help="Suscripciones"):
    st.session_state.nav_tab = "Suscripciones"
    st.rerun()
with col_m5:
  if st.button("💬", use_container_width=True, help="Mensajes"):
    st.session_state.nav_tab = "Mensajes"
    st.rerun()
with col_m6:
  if st.button("👤", use_container_width=True, help="Mi Perfil"):
    st.session_state.nav_tab = "Tu"
    st.rerun()
      
      
      
