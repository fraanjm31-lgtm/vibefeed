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

if 'active_tab_idx' not in st.session_state:
    st.session_state['active_tab_idx'] = 0

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
                city TEXT DEFAULT "Madrid", xp INTEGER DEFAULT 100,
                profile_pic TEXT DEFAULT "")''')
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    
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
                
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, 
                message TEXT, timestamp TEXT)''')

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
        c.execute("SELECT xp, profile_pic FROM users WHERE username = ?", (st.session_state['username'],))
        u_side = c.fetchone()
        xp_val = u_side[0]
        u_pic = u_side[1]
        
        if u_pic and os.path.exists(u_pic):
            st.image(u_pic, width=80)
            
        badge_name, badge_class = get_badge(xp_val)
        st.metric("Tus Puntos XP", xp_val)
        st.markdown(f"Rango: <span class='{badge_class}'>{badge_name}</span>", unsafe_allow_html=True)
        
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown("---")
    st.subheader("📺 Explorar Perfiles")
    search_query = st.text_input("🔍 Escribe el apodo:", placeholder="Ej: Labachito")
    if st.button("🔍 Buscar Usuario"):
        if search_query:
            clean_q = search_query.strip().replace("@", "")
            exists = c.execute("SELECT 1 FROM users WHERE username = ?", (clean_q,)).fetchone()
            if exists:
                st.session_state['viewing_user'] = clean_q
                st.session_state['active_tab_idx'] = 8
                st.rerun()
            else:
                st.error("Usuario no encontrado.")
        else:
            st.warning("Escribe un nombre.")

tab_titles = [
    "📱 Feed", "🚀 Lanzar", "🏆 Top", "🗳️ Algo", "⚔️ Duels", 
    "🌌 Ágora", "👤 Mi Perfil", "👥 Siguiendo", "📺 Canal / Perfil", "💬 Mensajes", "⚙️ Ajustes"
]

if st.session_state['active_tab_idx'] >= len(tab_titles):
    st.session_state['active_tab_idx'] = 0

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
        
        c.execute("SELECT xp, profile_pic FROM users WHERE username = ?", (user,))
        u_data = c.fetchone()
        p_xp = u_data[0] if u_data else 100
        p_pic = u_data[1] if u_data else ""
        b_name, b_class = get_badge(p_xp)

        col_av, col_u1, col_u2 = st.columns([1, 4, 1.5])
        with col_av:
            if p_pic and os.path.exists(p_pic):
                st.image(p_pic, width=45)
            else:
                st.markdown("👤")
        with col_u1:
            st.markdown(f"### **@{user}** <span class='{b_class}'>{b_name}</span>  `{vibe_tag}`", unsafe_allow_html=True)
        with col_u2:
            if st.button("👤 Perfil", key=f"visit_{post_id}_{user}"):
                st.session_state['viewing_user'] = user
                st.session_state['active_tab_idx'] = 8
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
                    
                    c.execute("INSERT INTO posts (user, caption, file, file_type, likes, views, vibe_tag) VALUES (?, ?, ?, ?, 1, 0, ?)", (st.session_state['username'], cap, path, f_type, vtag))
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
    c.execute("SELECT username, xp, bio, profile_pic FROM users ORDER BY xp DESC LIMIT 10")
    for idx, (l_user, l_xp, l_bio, l_pic) in enumerate(c.fetchall()):
        b_name, b_class = get_badge(l_xp)
        medal = "🥇" if idx == 0 else ("🥈" if idx == 1 else ("🥉" if idx == 2 else f"#{idx+1}"))
        
        col_img, col_t1, col_t2 = st.columns([1, 3, 1])
        with col_img:
            if l_pic and os.path.exists(l_pic):
                st.image(l_pic, width=50)
            else:
                st.markdown("👤")
        with col_t1:
            st.markdown(f"### {medal} @{l_user} <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
            st.write(f"💬 *{l_bio}* | ⚡ XP: **{l_xp}**")
        with col_t2:
            if st.button("Ver Perfil", key=f"top_p_{l_user}"):
                st.session_state['viewing_user'] = l_user
                st.session_state['active_tab_idx'] = 8
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
        u_info = c.execute("SELECT bio, city, xp, profile_pic FROM users WHERE username = ?", (cur,)).fetchone()
        b_n, b_c = get_badge(u_info[2])
        
        col_mp1, col_mp2 = st.columns([1, 2])
        with col_mp1:
            if u_info[3] and os.path.exists(u_info[3]):
                st.image(u_info[3], width=120)
            else:
                st.info("Sin foto de perfil")
        with col_mp2:
            st.metric("Puntos XP", u_info[2])
            st.markdown(f"**Insignia:** <span class='{b_c}'>{b_n}</span>", unsafe_allow_html=True)
        
        new_pic = st.file_uploader("Cambiar Foto de Perfil", type=["jpg", "jpeg", "png"])
        nb = st.text_area("Edita tu Bio", value=u_info[0])
        nc = st.text_input("Edita tu Ciudad", value=u_info[1])
        
        if st.button("Guardar Cambios de Perfil"):
            pic_path = u_info[3]
            if new_pic is not None:
                os.makedirs("uploads", exist_ok=True)
                pic_path = os.path.join("uploads", f"profile_{cur}_{new_pic.name}")
                with open(pic_path, "wb") as f: f.write(new_pic.getbuffer())
                
            c.execute("UPDATE users SET bio = ?, city = ?, profile_pic = ? WHERE username = ?", (nb, nc, pic_path, cur))
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
                c.execute("SELECT profile_pic FROM users WHERE username = ?", (fname,))
                f_data = c.fetchone()
                f_pic = f_data[0] if f_data else ""
                
                col_fimg, col_f1, col_f2 = st.columns([1, 3, 1])
                with col_fimg:
                    if f_pic and os.path.exists(f_pic):
                        st.image(f_pic, width=45)
                    else:
                        st.markdown("👤")
                with col_f1:
                    st.markdown(f"### @{fname}")
                with col_f2:
                    if st.button("Ver Canal", key=f"btn_f_{fname}"):
                        st.session_state['viewing_user'] = fname
                        st.session_state['active_tab_idx'] = 8
                        st.rerun()
                st.markdown("---")
    else:
        st.warning("Inicia sesión para ver tu lista de seguidos.")

# 9. Canal / Perfil Externo
with tabs[8]:
    st.subheader("📺 Perfil y Canal del Creador")
    target_user = st.session_state.get('viewing_user') or st.session_state.get('username')
    
    if target_user:
        u_data = c.execute("SELECT username, bio, city, xp, profile_pic FROM users WHERE username = ?", (target_user,)).fetchone()
        if u_data:
            real_username, u_bio, u_city, u_xp, u_pic = u_data
            b_name, b_class = get_badge(u_xp)
            
            col_pimg, col_ptxt = st.columns([1, 3])
            with col_pimg:
                if u_pic and os.path.exists(u_pic):
                    st.image(u_pic, width=120)
                else:
                    st.markdown("### 👤")
            with col_ptxt:
                st.markdown(f"## **@{real_username}** &nbsp; <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
                st.info(f"💬 **Biografía:** {u_bio} \n\n 📍 **Ciudad:** {u_city} \n\n ⚡ **Puntos XP:** {u_xp}")
            
            if st.session_state['logged_in'] and st.session_state['username'] != real_username:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    check_f = c.execute("SELECT 1 FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], real_username)).fetchone()
                    if check_f:
                        if st.button(f"❌ Dejar de seguir", key=f"unfollow_btn_{real_username}"):
                            c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (st.session_state['username'], real_username))
                            conn.commit()
                            st.rerun()
                    else:
                        if st.button(f"➕ Seguir", key=f"follow_btn_{real_username}"):
                            c.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (st.session_state['username'], real_username))
                            conn.commit()
                            st.rerun()
                with col_btn2:
                    if st.button(f"💬 Enviar Mensaje", key=f"msg_btn_{real_username}"):
                        st.session_state['chat_target'] = real_username
                        st.session_state['active_tab_idx'] = 9
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
        st.info("Escribe un usuario en el menú lateral o pincha en 'Perfil' desde el feed para ver los canales.")
# 10. Mensajes Privados
with tabs[9]:
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        
        # Buscar otros usuarios para chatear
        users_list = [u[0] for u in c.execute("SELECT username FROM users WHERE username != ?", (cur,)).fetchall()]
        
        if not users_list:
            st.info("No hay más usuarios registrados para chatear.")
        else:
            partner = st.selectbox("Para:", users_list, key="chat_partner_select")
            if partner:
                st.markdown(f"**Chat con @{partner}**")
                
                # CONSULTA CORREGIDA: Trae exactamente los mensajes mutuos entre tú y tu pareja, sin errores
                query = """
                    SELECT sender, message, timestamp FROM messages 
                    WHERE (sender = ? AND receiver = ?) 
                       OR (sender = ? AND receiver = ?) 
                    ORDER BY id ASC
                """
                messages = c.execute(query, (cur, partner, partner, cur)).fetchall()
                
                if not messages:
                    st.info("No hay mensajes aún. ¡Escribe el primero!")
                else:
                    for s, m, t in messages:
                        if s == cur:
                            st.markdown(f"**Tú:** {m} *({t})*")
                        else:
                            st.markdown(f"**@{s}:** {m} *({t})*")
                
                # Formulario de envío limpio y seguro
                with st.form(key=f"chat_form_{partner}", clear_on_submit=True):
                    txt = st.text_input("Escribe tu mensaje aquí...", key="input_msg_box")
                    submit_btn = st.form_submit_button("Enviar 🚀")
                    
                    if submit_btn:
                        if txt.strip():
                            now_time = datetime.now().strftime("%H:%M")
                            c.execute(
                                "INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)",
                                (cur, partner, txt.strip(), now_time)
                            )
                            conn.commit()
                            st.rerun()
    else:
        st.warning("Inicia sesión para chatear.")

# 11. Ajustes
with tabs[10]:
    st.subheader("⚙️ Ajustes")
    sel_theme = st.selectbox("Tema:", ["Modo Oscuro 🌙", "Modo Claro ☀️"], key="settings_theme_box")
    if sel_theme != st.session_state['theme']:
        st.session_state['theme'] = sel_theme
        st.rerun()
        
