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
    .profile-avatar img {{
        border-radius: 50% !important;
        object-fit: cover !important;
        width: 110px !important;
        height: 110px !important;
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
      "SELECT coins, xp FROM users WHERE username = ?",
      (st.session_state.username,),
  )
  res_user_info = c.fetchone()
  user_coins = res_user_info[0] if res_user_info else 100
  user_xp = res_user_info[1] if res_user_info else 0

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
    r_user = st.text_input("Nombre de Usuario (para iniciar sesion)", key="r_user")
    r_nombre = st.text_input("Nombre", key="r_nombre")
    r_apellidos = st.text_input("Apellidos", key="r_apellidos")
    r_edad = st.number_input("Edad", min_value=1, max_value=120, value=18, key="r_edad")
    r_email = st.text_input("Correo Electronico", key="r_email")
    r_pass = st.text_input("Contrasena", type="password", key="r_pass")
    
    if st.button("Registrarse y Entrar"):
      if not r_user or not r_pass:
        st.warning("Por favor, introduce al menos tu usuario y contraseña.")
      else:
        try:
          c.execute(
              "INSERT INTO users (username, password, nombre, apellidos, edad, email, xp, bio, avatar, account_privacy, coins, theme) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (r_user, r_pass, r_nombre, r_apellidos, int(r_edad), r_email, 10, "¡Hola! Uso VibeVibe.", "", "Publico", 100, "")
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

  if menu_option == "🔥 Feed de Videos":
    st.title("🔥 NoxVibe Feed")
    st.write("Videos publicos de la comunidad.")

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
    c.execute("SELECT avatar, nombre, apellidos, bio FROM users WHERE username = ?", (cur,))
    user_data = c.fetchone()
    avatar_path = user_data[0] if (user_data and user_data[0]) else ""
    nombre_completo = f"{user_data[1] or ''} {user_data[2] or ''}".strip()
    if not nombre_completo:
        nombre_completo = "Javi Márquez"
    bio_texto = user_data[3] if (user_data and user_data[3]) else "¡Bienvenidos a las calles sin ley de Los Santos! Vive conmigo los golpes más locos, persecuciones policiales intensas y todas las misiones."

    col_av_img, col_av_txt = st.columns([1, 2])
    
    with col_av_img:
        st.markdown('<div class="profile-avatar">', unsafe_allow_html=True)
        if avatar_path and os.path.exists(avatar_path):
            st.image(avatar_path, width=110)
        else:
            st.markdown("""
                <div style="width: 110px; height: 110px; background-color: #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px; color: #fff; margin: 0 auto;">
                    👤
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_av_txt:
        st.markdown(f"### {nombre_completo}")
        st.markdown(f"<p style='color: #aaa; margin-top: -10px;'>@{cur}</p>", unsafe_allow_html=True)
        
        with st.expander("🖼️ Cambiar mi foto / logo"):
            new_avatar = st.file_uploader("Sube tu foto o logo", type=["jpg", "png", "jpeg"], key="upload_avatar_real")
            if new_avatar is not None:
                os.makedirs("uploads", exist_ok=True)
                av_path = os.path.join("uploads", f"avatar_{cur}_{new_avatar.name}")
                with open(av_path, "wb") as f:
                    f.write(new_avatar.getbuffer())
                c.execute("UPDATE users SET avatar = ? WHERE username = ?", (av_path, cur))
                conn.commit()
                st.success("¡Foto de perfil actualizada!")
                st.rerun()

    st.write("")

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        c.execute("SELECT COUNT(*) FROM follows WHERE followed = ? AND status = 'accepted'", (cur,))
        total_suscriptores = c.fetchone()[0]
        st.markdown(f"**👥 {total_suscriptores}** Suscriptores")
    with col_stat2:
        c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (cur,))
        total_posts = c.fetchone()[0]
        st.markdown(f"**📦 {total_posts}** Publicaciones")

    st.write(bio_texto)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📊 Estadísticas", use_container_width=True):
            st.info(f"Tus XP acumulados: {user_xp} | NoxCoins: {user_coins} 🪙")
    with col_btn2:
        if st.button("✏️ Editar canal", use_container_width=True):
            st.warning("Próximamente podrás editar los ajustes avanzados desde aquí.")

    st.markdown("---")

    tab_inicio, tab_en_directo, tab_publicaciones = st.tabs(["Inicio", "En directo", "Publicaciones"])

    with tab_inicio:
        st.write("### Bienvenida a tu canal")
        st.caption("Todo lo que publiques aparecerá aquí abajo ordenado.")
        
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

    with tab_en_directo:
        st.info("No hay emisiones en directo activas ahora mismo.")

    with tab_publicaciones:
        st.subheader("📋 Tus Publicaciones y Borrado")
        
        c.execute("SELECT * FROM posts WHERE username = ?", (cur,))
        mis_posts = c.fetchall()
        
        if mis_posts:
            for p in mis_posts:
                p_id = p[0]
                st.write(f"Publicación ID: {p_id}")
                if p[2]:
                    st.write(p[2])
                if p[3] and os.path.exists(p[3]):
                    if p[4] == 'video':
                        st.video(p[3])
                    else:
                        st.image(p[3], width=300)
                
                if st.button("🗑️ Eliminar publicación", key=f"del_post_tab_{p_id}"):
                    c.execute("DELETE FROM posts WHERE id = ?", (p_id,))
                    conn.commit()
                    st.rerun()
                st.divider()
        else:
            st.markdown("""
                <div style="text-align: center; padding: 30px; color: #888;">
                    <h3>Crea contenido en cualquier dispositivo</h3>
                    <p>Sube y graba contenido estés donde estés. Todo lo que publiques aparecerá aquí.</p>
                </div>
            """, unsafe_allow_html=True)

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
                  "INSERT INTO follows (follower, followed, status) VALUES (?, ?, 'accepted')",
                  (cur, t_username),
              )
              conn.commit()
              st.success("¡Ahora sigues a este usuario!")
              st.rerun()
      else:
        st.warning("Usuario no encontrado.")

  elif menu_option == "👥 Siguiendo":
    st.title("👥 Tus Amigos y Seguidos")
    c.execute(
        "SELECT followed FROM follows WHERE follower = ? AND status = 'accepted'",
        (cur,),
    )
    seguidos = c.fetchall()
    if not seguidos:
      st.info("No sigues a nadie todavía.")
    else:
      for s in seguidos:
        st.write(f"👤 @{s[0]}")

  elif menu_option == "📺 Explorar Canales":
    st.title("📺 Explorar Canales")
    st.info("Próximamente más canales disponibles.")

  elif menu_option == "💬 Mensajes":
    st.title("💬 Mensajes Privados")
    st.info("Próximamente disponible.")

  elif menu_option == "⚙️ Ajustes":
    st.title("⚙️ Ajustes de Cuenta")
    nuevo_tema = st.selectbox("Tema visual", ["Oscuro", "Claro", "Neon / Cyber"], index=0 if st.session_state.theme == "Oscuro" else (1 if st.session_state.theme == "Claro" else 2))
    if st.button("Guardar Ajustes"):
      c.execute("UPDATE users SET theme = ? WHERE username = ?", (nuevo_tema, cur))
      conn.commit()
      st.success("¡Ajustes guardados con éxito!")
      st.rerun()
        
