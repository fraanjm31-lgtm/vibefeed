from datetime import datetime
import os
import sqlite3
import streamlit as st
import base64

def mostrar_video_con_elementos_superpuestos(video_file_path):
    try:
        with open(video_file_path, "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de video: {video_file_path}")
        return

st.set_page_config(page_title="NoxVibe", page_icon="🌹", layout="centered")

conn = sqlite3.connect("vibefeed.db", check_same_thread=False)
c = conn.cursor()

if "username" not in st.session_state:
    st.session_state.username = "Javimarquez"

if "profile_tab" not in st.session_state:
    st.session_state.profile_tab = "Fotos"

# Menú lateral completo con todas las opciones que se ven en tu app
menu_option = st.sidebar.selectbox(
    "Navegacion", 
    [
        "🔥 Feed de Videos",
        "👤 Mi Perfil",
        "🔍 Buscar Perfiles",
        "👥 Siguiendo",
        "💬 Mensajes",
        "🎁 Enviar Regalo"
    ]
)

if menu_option == "🔥 Feed de Videos":
    st.title("Feed de Videos 🎬")
    st.write("Aquí podrás ver los videos de la comunidad.")

elif menu_option == "👤 Mi Perfil":
    c.execute(
        "SELECT xp, bio, avatar, account_privacy, coins, nombre, apellido FROM users WHERE username = ?",
        (st.session_state.username,),
    )
    user_data = c.fetchone()
    xp = user_data[0] if user_data else 0
    bio = user_data[1] if user_data else ""
    avatar = user_data[2] if user_data else ""
    account_privacy = user_data[3] if user_data else "Publico"
    coins = user_data[4] if user_data else 10
    
    nombre_completo = (
        f"{user_data[5]} {user_data[6]}" if user_data and len(user_data) > 6 and user_data[5] else st.session_state.username
    )
    
    priv_badge = (
        "🔒 Cuenta Privada"
        if account_privacy == "Privado"
        else "🌐 Cuenta Publica"
    )
    st.title(f"{nombre_completo} (@{st.session_state.username})")
    st.caption(priv_badge)
    st.write(f"**Bio:** {bio}")
    st.write(f"**NoxCoins:** {coins} 🪙 | **XP:** {xp} XP")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🖼️ Ver Fotos", use_container_width=True):
            st.session_state.profile_tab = "Fotos"
    with col2:
        if st.button("🎬 Ver Videos", use_container_width=True):
            st.session_state.profile_tab = "Videos"

    st.markdown("---")

    if st.session_state.profile_tab == "Fotos":
        st.markdown("### 🖼️ Tus Fotos")
        c.execute(
            "SELECT id, caption, file, file_type, fires, thumbs, hearts, vibe_tag, timestamp FROM posts WHERE username = ? AND (file_type = 'image' OR file_type = '') ORDER BY id DESC",
            (st.session_state.username,),
        )
        posts = c.fetchall()
        if posts:
            for post in posts:
                p_id, p_cap, p_file, p_type, p_fires, p_thumbs, p_hearts, p_tag, p_time = post
                st.write(f"**{p_cap}**")
                if p_file:
                    st.image(p_file, use_column_width=True)
                st.markdown(f"🔥 {p_fires or 0} | 👍 {p_thumbs or 0} | ❤️ {p_hearts or 0}")
                st.markdown("---")
        else:
            st.info("Aún no tienes fotos publicadas.")

elif menu_option == "🔍 Buscar Perfiles":
    st.title("Buscar Perfiles 🔍")
    st.write("Busca a otros usuarios de NoxVibe aquí.")

elif menu_option == "👥 Siguiendo":
    st.title("Siguiendo 👥")
    st.write("Aquí verás las publicaciones de las personas a las que sigues.")

elif menu_option == "💬 Mensajes":
    st.title("Mensajes 💬")
    st.write("Tus conversaciones y chat privado.")

elif menu_option == "🎁 Enviar Regalo":
    st.title("Enviar Regalo 🌹")
    p_user = st.text_input("Usuario receptor:")
    
    c.execute("SELECT coins FROM users WHERE username = ?", (st.session_state.username,))
    user_c_data = c.fetchone()
    mis_c = user_c_data[0] if user_c_data and user_c_data[0] is not None else 10

    if st.button("Enviar Rosa Vibe (5 Coins)"):
        if mis_c >= 5:
            c.execute(
                "UPDATE users SET coins = ? WHERE username = ?",
                (mis_c - 5, st.session_state.username),
            )
            c.execute(
                "SELECT coins FROM users WHERE username = ?",
                (p_user,),
            )
            creador_data = c.fetchone()
            creador_c = (
                creador_data[0] if creador_data and creador_data[0] is not None else 0
            )
            c.execute(
                "UPDATE users SET coins = ? WHERE username = ?",
                (creador_c + 5, p_user),
            )
            msg_regalo = "🎁 ¡Te ha enviado un regalo: 🌹 Rosa Vibe (5 Coins)! 💌"
            c.execute(
                """
                    INSERT INTO messages (sender, receiver, message) VALUES
                    (?, ?, ?)
                """,
                (st.session_state.username, p_user, msg_regalo),
            )
            conn.commit()
            st.toast(f"Rosa enviada a @{p_user} con éxito! 🌹", icon="💌")
            st.rerun()
        else:
            st.toast(
                "¡No tienes suficientes NoxCoins para enviar la Rosa!",
                icon="⚠️",
            )
            

    if st.button("Guardar Cambios"):
      nuevo_estado = "Privado" if priv_sel else "Publico"
      c.execute(
          "UPDATE users SET theme = ?, account_privacy = ? WHERE username = ?",
          (tema_sel, nuevo_estado, cur),
      )
      conn.commit()
      st.session_state.theme = tema_sel
      st.success("¡Ajustes guardados con éxito!")
      st.rerun()
        
