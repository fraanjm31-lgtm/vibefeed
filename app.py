from datetime import date, datetime
from email.message import EmailMessage
import os
import random
import smtplib
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
c.execute("""CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT)""")
c.execute(
    """CREATE TABLE IF NOT EXISTS post_reactions (post_id INTEGER, username TEXT, reaction_type TEXT)"""
)

columnas_usuarios = [
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

if "codigo_enviado" not in st.session_state:
  st.session_state.codigo_enviado = False
if "codigo_generado" not in st.session_state:
  st.session_state.codigo_generado = ""

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


def enviar_codigo_correo(destinatario, codigo):
  remitente = "labachito91@gmail.com"
  password = "tu_contraseña_de_16_caracteres"

  msg = EmailMessage()
  msg.set_content(
      f"¡Hola!\n\nTu código de verificación para registrarte en NoxVibe es:\n"
      f" {codigo}\n\nIntroduce este código en la aplicación para completar tu"
      " registro."
  )
  msg["Subject"] = "Código de verificación - NoxVibe"
  msg["From"] = remitente
  msg["To"] = destinatario

  try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
      smtp.login(remitente, password)
      smtp.send_message(msg)
    return True
  except Exception as e:
    print(f"Error al enviar correo: {e}")
    return False
      


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
  st.info("🔒 Registro seguro con verificación automática por correo.")

  tab_login, tab_reg = st.tabs(["🔑 Iniciar Sesion", "📝 Registrarse"])

  with tab_login:
    l_user = st.text_input("Usuario", key="l_user")
    l_pass = st.text_input("Contrasena", type="password", key="l_pass")
    if st.button("Entrar"):
      c.execute(
          "SELECT * FROM users WHERE username = ? AND password = ?",
          (l_user, l_pass),
      )
      if c.fetchone():
        st.session_state.logged_in = True
        st.session_state.username = l_user
        st.rerun()
      else:
        st.error("Usuario o contrasena incorrectos")

  with tab_reg:
    r_email = st.text_input("Correo Electronico (Obligatorio)", key="r_email")
    r_user = st.text_input("Nuevo Usuario", key="r_user")
    r_pass = st.text_input("Nueva Contrasena", type="password", key="r_pass")
    r_dob = st.date_input(
        "Fecha de nacimiento",
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        key="r_dob",
    )
    r_adult = st.checkbox(
        "Confirmo que soy mayor de 18 anos.", key="r_adult_check"
    )

    if not st.session_state.codigo_enviado:
      if st.button("Enviar código de verificación al correo"):
        today = date.today()
        age = (
            today.year
            - r_dob.year
            - ((today.month, today.day) < (r_dob.month, r_dob.day))
        )

        if not r_email or "@" not in r_email or "." not in r_email:
          st.error("Introduce un correo electronico valido.")
        elif not r_user or not r_pass:
          st.warning("Rellena el usuario y la contrasena.")
        elif age < 18:
          st.error("Debes ser mayor de 18 anos.")
        elif not r_adult:
          st.warning("Debes marcar la casilla de mayoria de edad.")
        else:
          c.execute("SELECT * FROM users WHERE username = ?", (r_user,))
          if c.fetchone():
            st.error("El nombre de usuario ya esta en uso.")
          else:
            codigo = str(random.randint(100000, 999999))
            st.session_state.codigo_generado = codigo
            exito = enviar_codigo_correo(r_email, codigo)
            if exito:
              st.session_state.codigo_enviado = True
              st.success(
                  "¡Código enviado! Revisa tu bandeja de entrada o spam."
              )
              st.rerun()
            else:
              st.error(
                  "Error al enviar el correo. Revisa la configuración SMTP."
              )

    if st.session_state.codigo_enviado:
      codigo_ingresado = st.text_input(
          "Introduce el Código recibido en tu correo", key="code_input_field"
      )
      if st.button("Validar y Crear Cuenta"):
        if codigo_ingresado == st.session_state.codigo_generado:
          try:
            c.execute(
                "INSERT INTO users (username, password, email, xp, bio, avatar,"
                " account_privacy, coins, theme) VALUES (?, ?, ?, ?, ?, ?, ?,"
                " ?, ?)",
                (
                    r_user,
                    r_pass,
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
            st.success(
                "¡Cuenta creada con exito! Ya puedes iniciar sesion arriba."
            )
            st.session_state.codigo_enviado = False
            st.session_state.codigo_generado = ""
            st.rerun()
          except Exception as ex:
            st.error(f"Error al registrar: {ex}")
        else:
          st.error("El código de verificación es incorrecto.")

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
        p_id, p_user, p_cap, p_file, p_fires, p_thumbs, p_hearts, p_tag, p_time = (
            post
        )
        val_fires = p_fires if p_fires is not None else 0
        val_thumbs = p_thumbs if p_thumbs is not None else 0
        val_hearts = p_hearts if p_hearts is not None else 0

        st.markdown(f'<div class="video-container">', unsafe_allow_html=True)
        col_vid, col_act = st.columns([4, 1])

        with col_vid:
          st.markdown(f"### @{p_user} · `{p_tag}`")
          if p_cap:
            st.write(p_cap)
          if (
              p_file
              and isinstance(p_file, str)
              and os.path.exists(p_file)
          ):
            st.video(p_file)

        with col_act:
          st.markdown("<br><br>", unsafe_allow_html=True)
          if st.button(
              f"🔥 {val_fires}",
              key=f"feed_fire_{p_id}",
              use_container_width=True,
          ):
            handle_reaction(p_id, cur, "fire")
          if st.button(
              f"👍 {val_thumbs}",
              key=f"feed_like_{p_id}",
              use_container_width=True,
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
    c.execute(
        "SELECT xp, bio, avatar, account_privacy, coins FROM users WHERE username"
        " = ?",
        (cur,),
    )
    user_data = c.fetchone()
    xp = user_data[0] if user_data else 0
    bio = user_data[1] if user_data else ""
    avatar = user_data[2] if user_data else ""
    account_privacy = user_data[3] if user_data else "Publico"
    coins = user_data[4] if user_data else 100

    priv_badge = (
        "🔒 Cuenta Privada"
        if account_privacy == "Privado"
        else "🌐 Cuenta Publica"
    )
    st.title(f"@{cur}")
    st.caption(priv_badge)

    c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (cur,))
    total_posts = c.fetchone()[0]
    c.execute(
        "SELECT COUNT(*) FROM follows WHERE followed = ? AND status = 'accepted'",
        (cur,),
    )
    total_followers = c.fetchone()[0]
    c.execute(
        "SELECT COUNT(*) FROM follows WHERE follower = ? AND status = 'accepted'",
        (cur,),
    )
    total_following = c.fetchone()[0]

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
        p_id, p_cap, p_file, p_type, p_fires, p_thumbs, p_hearts, p_tag, p_time = (
            post
        )
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
        p_id, p_cap, p_file, p_type, p_fires, p_thumbs, p_hearts, p_tag, p_time = (
            post
        )
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
        t_use
  elif menu_option == "⚙️ Ajustes":
    st.title("⚙️ Ajustes de la cuenta")

    # Intentamos leer los datos de ajustes de forma segura
    try:
      c.execute(
          "SELECT bio, avatar, theme, account_privacy FROM users WHERE"
          " username = ?",
          (cur,),
      )
      u_settings = c.fetchone()
    except:
      u_settings = None

    current_bio = u_settings[0] if u_settings and u_settings[0] else ""
    current_db_theme = (
        u_settings[2]
        if u_settings and len(u_settings) > 2 and u_settings[2]
        else "Oscuro"
    )
    current_privacy = (
        u_settings[3]
        if u_settings and len(u_settings) > 3 and u_settings[3]
        else "Publico"
    )

    with st.form("settings_bio_form"):
      new_bio = st.text_area("Actualizar tu biografia", value=current_bio)
      submit_bio = st.form_submit_button("Guardar Biografia")

    if submit_bio:
      c.execute("UPDATE users SET bio = ? WHERE username = ?", (new_bio, cur))
      conn.commit()
      st.success("¡Biografía actualizada con éxito!")
      st.rerun()

    st.markdown("---")
    st.subheader("🎨 Apariencia y Privacidad")

    new_theme = st.selectbox(
        "Tema de Colores", ["Oscuro", "Claro", "Neon / Cyber"], index=0
    )
    if new_theme != current_db_theme:
      c.execute(
          "UPDATE users SET theme = ? WHERE username = ?", (new_theme, cur)
      )
      conn.commit()
      st.session_state.theme = new_theme
      st.success(f"Tema cambiado a {new_theme}")
      st.rerun()

    is_private = st.checkbox(
        "🔒 Cuenta Privada", value=(current_privacy == "Privado")
    )
    new_priv = "Privado" if is_private else "Publico"
    if new_priv != current_privacy:
      c.execute(
          "UPDATE users SET account_privacy = ? WHERE username = ?",
          (new_priv, cur),
      )
      conn.commit()
      st.success(f"Privacidad actualizada a: {new_priv}")
      st.rerun()
        
