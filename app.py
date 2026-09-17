import streamlit as st
import os
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="NoxVibe",
    page_icon="⚡",
    layout="centered"
)

def get_custom_css(theme):
    if theme == "Modo Claro ☀️":
        bg_color = "#ffffff"
        text_color = "#0e1117"
    else:
        bg_color = "#0e1117"
        text_color = "#fafafa"
        
    return f"""
    <style>
    .main {{ background-color: {bg_color}; color: {text_color}; }}
    .stButton>button {{ width: 100%; border-radius: 20px; font-weight: bold; }}
    .badge-novato {{ background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
    .badge-pro {{ background-color: #8b5cf6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
    .badge-cuantico {{ background-color: #f59e0b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
    </style>
    """

if 'theme' not in st.session_state:
    st.session_state['theme'] = "Modo Oscuro 🌙"

if 'viewing_user' not in st.session_state:
    st.session_state['viewing_user'] = None

st.markdown(get_custom_css(st.session_state['theme']), unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password TEXT, 
                bio TEXT DEFAULT "Creador NoxVibe ⚡", 
                city TEXT DEFAULT "Madrid", xp INTEGER DEFAULT 100)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS follows (
                follower TEXT, followed TEXT, 
                PRIMARY KEY (follower, followed))''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, caption TEXT, 
                file TEXT, file_type TEXT, likes INTEGER, views INTEGER DEFAULT 0, 
                vibe_tag TEXT DEFAULT "General 🌍", is_story INTEGER DEFAULT 0, 
                secret_pin TEXT DEFAULT "", is_duel INTEGER DEFAULT 0, 
                duel_votes_a INTEGER DEFAULT 0, duel_votes_b INTEGER DEFAULT 0, 
                duel_opponent TEXT DEFAULT "", gifts_received TEXT DEFAULT "")''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS agora (
                id INTEGER PRIMARY KEY AUTOINCREMENT, thought TEXT, 
                constellation TEXT DEFAULT "Filosofía 🌌")''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS algo_votes (
                user TEXT PRIMARY KEY, preference TEXT)''')

    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

def get_badge(xp):
    if xp >= 300:
        return "⚡ Dios NoxVibe", "badge-cuantico"
    elif xp >= 180:
        return "🔥 Creador Pro", "badge-pro"
    else:
        return "🌱 Novato", "badge-novato"

st.title("⚡ NoxVibe")
st.caption("✨ Red social completa con XP, Canales y Perfiles.")

with st.sidebar:
    st.subheader("🔐 Acceso NoxVibe")
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
                c.execute("SELECT password FROM users WHERE username = ?", (clean_user,))
                res = c.fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = clean_user
                    st.success(f"¡Bienvenido, @{clean_user}!")
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **@{st.session_state['username']}**")
        c.execute("SELECT xp FROM users WHERE username = ?", (st.session_state['username'],))
        xp_val = c.fetchone()[0]
        badge_name, badge_class = get_badge(xp_val)
        st.metric("Tus Puntos XP", xp_val)
        st.markdown(f"Rango: <span class='{badge_class}'>{badge_name}</span>", unsafe_allow_html=True)
        
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown("---")
    st.subheader("📺 Explorar Perfiles")
    c.execute("SELECT username FROM users")
    all_users = [u[0] for u in c.fetchall()]
    if all_users:
        selected_search = st.selectbox("🔍 Ver perfil de:", ["Selecciona..."] + all_users)
        if selected_search != "Selecciona...":
            st.session_state['viewing_user'] = selected_search
            st.rerun()

tab_titles = [
    "📱 Feed", "🚀 Lanzar", "🏆 Top", "🗳️ Algo", "⚔️ Duels", 
    "🌌 Ágora", "👤 Mi Perfil", "👥 Siguiendo", "📺 Canal / Perfil", "⚙️ Ajustes"
]

tabs = st.tabs(tab_titles)

# 1. Feed
with tabs[0]:
    st.subheader("Feed de la Comunidad")
    c.execute("SELECT id, user, caption, file, file_type, likes, views, vibe_tag, gifts_received FROM posts WHERE is_story = 0 AND is_duel = 0 ORDER BY id DESC")
    posts = c.fetchall()
    
    if not posts:
        st.info("No hay publicaciones todavía.")
    
    for post in posts:
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag, gifts_received = post
        c.execute("SELECT xp FROM users WHERE username = ?", (user,))
        u_xp_res = c.fetchone()
        p_xp = u_xp_res[0] if u_xp_res else 100
        b_name, b_class = get_badge(p_xp)

        col_u1, col_u2 = st.columns([3, 1])
        with col_u1:
            st.markdown(f"### **@{user}** <span class='{b_class}'>{b_name}</span>  `{vibe_tag}`", unsafe_allow_html=True)
        with col_u2:
            if st.button("👤 Perfil", key=f"visit_{post_id}_{user}"):
                st.session_state['viewing_user'] = user
                st.rerun()

        st.write(caption)
        if file_path and os.path.exists(file_path):
            if "video" in file_type: st.video(file_path)
            elif "image" in file_type: st.image(file_path, use_container_width=True)
        
        st.caption(f"❤️ {likes} likes | 👁️ {(views or 0) + 1} vistas")
        
        if st.button("❤️ Like", key=f"l_{post_id}"):
            c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
            conn.commit()
            st.rerun()
        st.markdown("---")

# 2. Lanzar
with tabs[1]:
    st.subheader("🚀 Lanzar Contenido")
    if st.session_state['logged_in']:
        with st.form("up_form", clear_on_submit=True):
            cap = st.text_input("Descripción...")
            media = st.file_uploader("Multimedia", type=["mp4", "mov", "jpg", "jpeg", "png"])
            vtag = st.selectbox("Categoría Vibe", ["General 🌍", "Tecnología 💻", "Filosofía 🌌", "Arte 🎨"])
            
            if st.form_submit_button("¡Lanzar Vibe! ⚡"):
                if cap or media is not None:
                    path, f_type = None, "default"
                    if media is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", media.name)
                        with open(path, "wb") as f: f.write(media.getbuffer())
                        f_type = media.type
                    
                    c.execute("""INSERT INTO posts (user, caption, file, file_type, likes, views, vibe_tag) 
                                 VALUES (?, ?, ?, ?, 1, 0, ?)""", 
                              (st.session_state['username'], cap, path, f_type, vtag))
                    c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (st.session_state['username'],))
                    conn.commit()
                    st.success("¡Lanzado con éxito! +10 XP ⚡")
                    st.rerun()
                else:
                    st.warning("Escribe algo o sube un archivo.")
    else:
        st.warning("Inicia sesión en el menú lateral para lanzar contenido.")

# 3. Top
with tabs[2]:
    st.subheader("🏆 Salón de la Fama")
    c.execute("SELECT username, xp, bio FROM users ORDER BY xp DESC LIMIT 10")
    for idx, (l_user, l_xp, l_bio) in enumerate(c.fetchall()):
        b_name, b_class = get_badge(l_xp)
        medal = "🥇" if idx == 0 else ("🥈" if idx == 1 else ("🥉" if idx == 2 else f"#{idx+1}"))
        
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.markdown(f"### {medal} @{l_user} <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
            st.write(f"💬 *{l_bio}* | ⚡ XP: **{l_xp}**")
        with col_t2:
            if st.button("Ver Perfil", key=f"top_p_{l_user}"):
                st.session_state['viewing_user'] = l_user
                st.rerun()
        st.markdown("---")

# 4. Algo
with tabs[3]:
    st.subheader("🗳️ Reglas del Algoritmo")
    if st.session_state['logged_in']:
        pref = st.radio("Preferencia de feed:", ["Todo", "Solo Vídeos", "Solo Fotos"])
        if st.button("Guardar Voto"):
            c.execute("INSERT OR REPLACE INTO algo_votes (user, preference) VALUES (?, ?)", (st.session_state['username'], pref))
            conn.commit()
            st.success("¡Actualizado!")
    else:
        st.warning("Inicia sesión para votar.")

# 5. Duels
with tabs[4]:
    st.subheader("⚔️ VibeDuels 1v1")
    st.info("Sección de duelos activa. ¡Próximamente más novedades!")

# 6. Ágora
with tabs[5]:
    st.subheader("🌌 Ágora: Reflexiones")
    if st.session_state['logged_in']:
        t_txt = st.text_area("Lanza un pensamiento...")
        if st.button("Publicar Pensamiento") and t_txt:
            c.execute("INSERT INTO agora (thought) VALUES (?)", (t_txt,))
            conn.commit()
            st.rerun()
    for ag in c.execute("SELECT thought, constellation FROM agora ORDER BY id DESC").fetchall():
        st.markdown(f"> *\"{ag[0]}\"* \n\n 🏷️ `{ag[1]}`")
        st.markdown("---")

# 7. Mi Perfil
with tabs[6]:
    st.subheader("👤 Tu Perfil Personal")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        u_info = c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (cur,)).fetchone()
        b_n, b_c = get_badge(u_info[2])
        st.metric("Puntos XP", u_info[2])
        st.markdown(f"**Insignia:** <span class='{b_c}'>{b_n}</span>", unsafe_allow_html=True)
        
        nb = st.text_area("Edita tu Bio", value=u_info[0])
        nc = st.text_input("Edita tu Ciudad", value=u_info[1])
        if st.button("Guardar Cambios de Perfil"):
            c.execute("UPDATE users SET bio = ?, city = ? WHERE username = ?", (nb, nc, cur))
            conn.commit()
            st.success("¡Perfil actualizado con éxito!")
            st.rerun()
    else:
        st.warning("Inicia sesión para ver y editar tu perfil.")

# 8. Siguiendo
with tabs[7]:
    st.subheader("👥 Usuarios que Sigues")
    if st.session_state['logged_in']:
        following_list = c.execute("SELECT followed FROM follows WHERE follower = ?", (st.session_state['username'],)).fetchall()
        
        if not following_list:
            st.info("Aún no sigues a ningún creador. ¡Explora perfiles y comienza a seguirlos!")
        else:
            for f_user in following_list:
                fname = f_user[0]
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.markdown(f"### 👤 @{fname}")
                with col_f2:
                    if st.button("Ver Canal", key=f"btn_f_{fname}"):
                        st.session_state['viewing_user'] = fname
                        st.rerun()
                st.markdown("---")
    else:
        st.warning("Inicia sesión para ver tu lista de seguidos.")

# 9. Canal / Perfil Externo
with tabs[8]:
    st.subheader("📺 Perfil y Canal del Creador")
    target_user = st.session_state.get('viewing_user') or st.session_state.get('username')
    
    if target_user:
        u_data = c.execute("SELECT username, bio, city, xp FROM users WHERE username = ?", (target_user,)).fetchone()
        if u_data:
            real_username, u_bio, u_city, u_xp = u_data
            b_name, b_class = get_badge(u_xp)
            
            st.markdown(f"## Perfil de **@{real_username}** <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
            st.info(f"💬 **Biografía:** {u_bio} \n\n 📍 **Ciudad:** {u_city} \n\n ⚡ **Puntos XP:** {u_xp}")
            
            if st.session_state['logged_in'] and st.session_state['username'] != real_username:
                check_f = c.execute("SELECT 1 FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], real_username)).fetchone()
                
                if check_f:
                    if st.button(f"❌ Dejar de seguir a @{real_username}", key=f"unfollow_btn_{real_username}"):
                        c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], real_username))
                        conn.commit()
                        st.success(f"Has dejado de seguir a @{real_username}")
                        st.rerun()
                else:
                    if st.button(f"➕ Seguir a @{real_username}", key=f"follow_btn_{real_username}"):
                        c.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (st.session_state['username'], real_username))
                        conn.commit()
                        st.success(f"¡Ahora sigues a @{real_username}!")
                        st.rerun()

            st.markdown("### 📱 Publicaciones del Creador")
            user_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE user = ? ORDER BY id DESC", (real_username,)).fetchall()
            
            if not user_posts:
                st.write("Este usuario aún no ha publicado nada.")
            
            for upost in user_posts:
                pid, u_cap, u_file, u_ftype, u_likes, u_vtag = upost
                st.markdown(f"**Tema:** `{u_vtag}`")
                st.write(u_cap)
                if u_file and os.path.exists(u_file):
                    if "video" in u_ftype: st.video(u_file)
                    elif "image" in u_ftype: st.image(u_file, use_container_width=True)
                st.caption(f"❤️ {u_likes} likes")
                st.markdown("---")
    else:
        st.info("Selecciona un creador en el menú lateral o desde el feed para ver su perfil.")

# 10. Ajustes
with tabs[9]:
    st.subheader("⚙️ Ajustes Pro")
    sel_t = st.selectbox("Tema:", ["Modo Oscuro 🌙", "Modo Claro ☀️"])
    if sel_t != st.session_state['theme']:
        st.session_state['theme'] = sel_t
        st.rerun()
        
