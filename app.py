import streamlit as st
import sqlite3
import os
from datetime import datetime
import hashlib

st.set_page_config(page_title="NoxVibe", page_icon="⚡", layout="centered")

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashlib.sha256(str.encode(password)).hexdigest()
    return False

conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        bio TEXT DEFAULT 'Hola, uso NoxVibe.',
        city TEXT DEFAULT 'Madrid',
        xp INTEGER DEFAULT 0,
        profile_pic TEXT DEFAULT ''
    )
''')

try:
    c.execute("SELECT username, likes, vibe_tag FROM posts LIMIT 1")
except sqlite3.OperationalError:
    c.execute("DROP TABLE IF EXISTS posts")

c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        caption TEXT,
        file TEXT,
        file_type TEXT,
        likes INTEGER DEFAULT 0,
        vibe_tag TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS follows (
        follower TEXT,
        followed TEXT
    )
''')
conn.commit()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Modo Oscuro 🌙'
if 'viewing_user' not in st.session_state:
    st.session_state['viewing_user'] = ''

def get_badge(xp):
    if xp >= 300:
        return "🔥 Creador Pro", "badge-pro"
    else:
        return "🌱 Novato", "badge-novato"

# Función auxiliar para renderizar una publicación con su barra de estilo Instagram
def render_post(p_id, p_user, p_cap, p_file, p_file_type, p_likes, p_tag):
    st.markdown(f"*Tema: {p_tag}*")
    if p_cap:
        st.write(p_cap)
    if p_file and os.path.exists(p_file):
        if p_file_type == "video":
            st.video(p_file)
        else:
            st.image(p_file, use_container_width=True)
            
    # Barra de interacciones estilo Instagram[span_3](start_span)[span_3](end_span)
    col_l, col_c, col_r, col_s = st.columns([1, 1, 1, 1])
    with col_l:
        if st.button("❤️", key=f"like_btn_{p_id}"):
            c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (p_id,))
            conn.commit()
            st.rerun()
    with col_c:
        st.markdown(f"💬")
    with col_r:
        st.markdown(f"🔄")
    with col_s:
        st.markdown(f"📌")
        
    st.markdown(f"❤️ **{p_likes} Me gusta**[span_4](start_span)[span_4](end_span)")
    st.markdown("---")

st.title("⚡ NoxVibe")
st.caption("✨ Red social completa con XP, Canales y Perfiles.")

with st.sidebar:
    st.subheader("🔑 Acceso NoxVibe")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Apodo / Usuario")
        p_in = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if u_in and p_in:
                    clean_user = u_in.strip().replace("@", "")
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (clean_user, make_hashes(p_in)))
                        conn.commit()
                        st.success("¡Registrado con éxito!")
                    except sqlite3.IntegrityError:
                        st.error("Ese apodo ya está en uso.")
                else:
                    st.warning("Rellena todos los campos.")
        else:
            if st.button("Entrar"):
                clean_user = u_in.strip().replace("@", "")
                res = c.execute("SELECT password FROM users WHERE username = ?", (clean_user,)).fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = clean_user
                    st.success(f"¡Bienvenido, @{clean_user}!")
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **@{st.session_state['username']}**")
        u_data = c.execute("SELECT xp, profile_pic FROM users WHERE username = ?", (st.session_state['username'],)).fetchone()
        xp_val = u_data[0] if u_data else 0
        u_pic = u_data[1] if u_data else ''
        
        if u_pic and os.path.exists(u_pic):
            st.image(u_pic, width=80)
            
        badge_name, badge_class = get_badge(xp_val)
        st.metric("Tus Puntos XP", xp_val)
        st.markdown(f"Rango: **{badge_name}**")
        
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown("---")
    st.subheader("💼 Explorar Perfiles")
    search_query = st.text_input("🔍 Escribe el apodo:", placeholder="Ej: Labachito")
    if st.button("Buscar Usuario"):
        clean_q = search_query.strip().replace("@", "")
        exists = c.execute("SELECT 1 FROM users WHERE username = ?", (clean_q,)).fetchone()
        if exists:
            st.session_state['viewing_user'] = clean_q
            st.session_state['active_tab_idx'] = 1
            st.rerun()
        else:
            st.error("Usuario no encontrado.")

tabs = st.tabs([
    "👤 Perfil / Canal", 
    "👥 Siguiendo", 
    "📺 Canal / Perfil", 
    "💬 Mensajes", 
    "⚙️ Ajustes"
])

with tabs[0]:
    st.subheader("👤 Tu Perfil y Canal")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        u_info = c.execute("SELECT bio, city, xp, profile_pic FROM users WHERE username = ?", (cur,)).fetchone()
        
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            if u_info and u_info[3] and os.path.exists(u_info[3]):
                st.image(u_info[3], width=100)
            else:
                st.write("📷 Sin foto")
        with col_p2:
            if u_info:
                st.markdown(f"**Bio:** {u_info[0]}")
                st.markdown(f"**Ciudad:** {u_info[1]}")
                st.markdown(f"**XP:** {u_info[2]}")
            
        st.markdown("---")
        st.subheader("📝 Publicar Contenido en tu Canal")
        with st.form("new_post_form", clear_on_submit=True):
            cap = st.text_area("¿Qué estás pensando?")
            tag = st.selectbox("Vibe / Categoría", ["General", "Música", "Tecnología", "Amor", "Viajes"])
            uploaded_file = st.file_uploader("Sube foto o vídeo", type=["jpg", "png", "mp4", "mov"])
            
            if st.form_submit_button("Publicar 🚀"):
                path_to_save = ""
                f_type = ""
                if uploaded_file is not None:
                    os.makedirs("uploads", exist_ok=True)
                    path_to_save = os.path.join("uploads", uploaded_file.name)
                    with open(path_to_save, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    f_type = "video" if uploaded_file.type.startswith("video") else "image"
                
                c.execute("INSERT INTO posts (username, caption, file, file_type, likes, vibe_tag) VALUES (?, ?, ?, ?, ?, ?)",
                          (cur, cap, path_to_save, f_type, 0, tag))
                c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (cur,))
                conn.commit()
                st.success("¡Publicado con éxito! (+10 XP)")
                st.rerun()
                
        st.markdown("---")
        st.subheader("Tus publicaciones:")
        my_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (cur,)).fetchall()
        for p in my_posts:
            render_post(p[0], cur, p[1], p[2], p[3], p[4], p[5])
    else:
        st.warning("Inicia sesión para gestionar tu perfil y publicar.")

with tabs[1]:
    st.subheader("👥 Actividad de Seguidos")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        following = [row[0] for row in c.execute("SELECT followed FROM follows WHERE follower = ?", (cur,)).fetchall()]
        if not following:
            st.info("Aún no sigues a nadie. Busca perfiles en la barra lateral para ver su contenido aquí.")
        else:
            for f_user in following:
                st.markdown(f"### Canal de @{f_user}")
                f_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (f_user,)).fetchall()
                for p in f_posts:
                    render_post(p[0], f_user, p[1], p[2], p[3], p[4], p[5])
    else:
        st.warning("Inicia sesión para ver la actividad de tus seguidos.")

with tabs[2]:
    st.subheader("🔍 Canal y Perfil del Creador")
    target_user = st.session_state.get('viewing_user') or st.session_state.get('username')
    
    if target_user:
        u_data = c.execute("SELECT username, bio, city, xp, profile_pic FROM users WHERE username = ?", (target_user,)).fetchone()
        if u_data:
            b_name, b_class = get_badge(u_data[3])
            col_ping1, col_ping2 = st.columns([1, 2])
            with col_ping1:
                if u_data[4] and os.path.exists(u_data[4]):
                    st.image(u_data[4], width=100)
                else:
                    st.write("📷")
            with col_ping2:
                st.markdown(f"### @{u_data[0]} [{b_name}]")
                st.markdown(f"**Bio:** {u_data[1]} | **Ciudad:** {u_data[2]} | **XP:** {u_data[3]}")
                
                if st.session_state['logged_in'] and st.session_state['username'] != target_user:
                    is_following = c.execute("SELECT 1 FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], target_user)).fetchone()
                    if is_following:
                        if st.button("❌ Dejar de seguir"):
                            c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], target_user))
                            conn.commit()
                            st.rerun()
                    else:
                        if st.button("➕ Seguir"):
                            c.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (st.session_state['username'], target_user))
                            conn.commit()
                            st.rerun()
                            
            st.markdown("---")
            user_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (target_user,)).fetchall()
            if not user_posts:
                st.info("Este usuario aún no ha publicado nada.")
            else:
                for p in user_posts:
                    render_post(p[0], target_user, p[1], p[2], p[3], p[4], p[5])
        else:
            st.info("Busca un usuario en el menú lateral para ver su perfil.")
    else:
        st.info("Busca un usuario en el menú lateral para ver su perfil.")

with tabs[3]:
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        
        chat_conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
        chat_c = chat_conn.cursor()
        
        users_list = [u[0] for u in chat_c.execute("SELECT username FROM users WHERE username != ?", (cur,)).fetchall()]
        
        if not users_list:
            st.info("No hay más usuarios registrados.")
        else:
            partner = st.selectbox("Para:", users_list, key="chat_partner_final_definitivo")
            if partner:
                st.markdown(f"**Chat con @{partner}**")
                
                @st.fragment(run_every=3)
                def mostrar_mensajes_en_tiempo_real():
                    inner_conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
                    inner_c = inner_conn.cursor()
                    
                    msgs = inner_c.execute("""
                        SELECT sender, message, timestamp 
                        FROM messages 
                        WHERE (sender = ? AND receiver = ?) 
                           OR (sender = ? AND receiver = ?) 
                        ORDER BY id ASC
                    """, (cur, partner, partner, cur)).fetchall()
                    
                    inner_conn.close()
                    
                    if not msgs:
                        st.info("No hay mensajes aún. ¡Escribe el primero!")
                    else:
                        for s, m, t in msgs:
                            if s == cur:
                                st.markdown(f"**Tú:** {m} *({t})*")
                            else:
                                st.markdown(f"**@{s}:** {m} *({t})*")

                mostrar_mensajes_en_tiempo_real()
                
                with st.form(key=f"chat_form_final_{partner}", clear_on_submit=True):
                    txt = st.text_input("Escribe tu mensaje...", key="input_msg_final")
                    if st.form_submit_button("Enviar 🚀"):
                        if txt.strip():
                            chat_c.execute(
                                "INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", 
                                (cur, partner, txt.strip(), datetime.now().strftime("%H:%M"))
                            )
                            chat_conn.commit()
                            chat_conn.close()
                            st.rerun()
                            
        chat_conn.close()
    else:
        st.warning("Inicia sesión para chatear.")

with tabs[4]:
    st.subheader("⚙️ Ajustes")
    sel_theme = st.selectbox("Tema:", ["Modo Oscuro 🌙", "Modo Claro ☀️"], key="settings_theme_final_def")
    if sel_theme != st.session_state['theme']:
        st.session_state['theme'] = sel_theme
        st.rerun()
        
