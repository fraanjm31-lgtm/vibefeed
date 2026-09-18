import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta
import hashlib

st.set_page_config(page_title="NoxVibe", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 14px rgba(168, 85, 247, 0.4);
    }
    div.stTextInput>div>div>input, div.stTextArea>div>div>textarea {
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    .vibe-badge {
        background: rgba(168, 85, 247, 0.15);
        border: 1px solid #a855f7;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: #d8b4fe;
    }
    </style>
""", unsafe_allow_html=True)

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
        profile_pic TEXT DEFAULT '',
        music_link TEXT DEFAULT ''
    )
''')

try:
    c.execute("ALTER TABLE users ADD COLUMN music_link TEXT DEFAULT ''")
    conn.commit()
except sqlite3.OperationalError:
    pass

c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        caption TEXT,
        file TEXT,
        file_type TEXT,
        likes INTEGER DEFAULT 0,
        vibe_tag TEXT,
        timestamp TEXT
    )
''')

try:
    c.execute("ALTER TABLE posts ADD COLUMN timestamp TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

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

c.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        username TEXT,
        post_id INTEGER
    )
''')
conn.commit()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'viewing_user' not in st.session_state:
    st.session_state['viewing_user'] = ''

def get_badge(xp):
    if xp >= 300:
        return "🔥 Creador Pro", "badge-pro"
    else:
        return "🌱 Novato", "badge-novato"

def ai_vibe_checker(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ['fiesta', 'noche', 'bailar', 'fuego', 'energy']):
        return "🎉 Fiesta", "¡Ambiente de fiesta detectado!"
    elif any(w in text_lower for w in ['triste', 'solo', 'gris', 'llorar']):
        return "🌧️ Melancólico", "Tono reflexivo detectado."
    elif any(w in text_lower for w in ['aprender', 'mente', 'pensar', 'futuro']):
        return "🧠 Filósofo", "Contenido profundo detectado."
    else:
        return "🔥 Hype", "Energía positiva detectada."

def render_post(p_id, p_user, p_cap, p_file, p_file_type, p_likes, p_tag, p_time=""):
    st.markdown(f"**@{p_user}** · <span class='vibe-badge'>{p_tag}</span> {f'· *{p_time}*' if p_time else ''}", unsafe_allow_html=True)
    if p_cap:
        st.write(p_cap)
    if p_file and os.path.exists(p_file):
        if p_file_type == "video":
            st.video(p_file)
        else:
            st.image(p_file, use_container_width=True)
            
    col_act1, col_act2 = st.columns([3, 1])
    with col_act1:
        if st.button("❤️ Me gusta", key=f"like_{p_id}"):
            c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (p_id,))
            conn.commit()
            st.rerun()
    with col_act2:
        current_user = st.session_state.get('username', '')
        is_fav = False
        if current_user:
            is_fav = c.execute("SELECT 1 FROM favorites WHERE username = ? AND post_id = ?", (current_user, p_id)).fetchone()
        
        fav_label = "🔖 Guardado" if is_fav else "📌 Guardar"
        if st.button(fav_label, key=f"fav_{p_id}"):
            if not current_user:
                st.warning("Inicia sesión.")
            else:
                if is_fav:
                    c.execute("DELETE FROM favorites WHERE username = ? AND post_id = ?", (current_user, p_id))
                    conn.commit()
                else:
                    c.execute("INSERT INTO favorites (username, post_id) VALUES (?, ?)", (current_user, p_id))
                    conn.commit()
                st.rerun()
        
    if p_likes > 0:
        st.markdown(f"❤️ **Le gusta a {p_likes} personas**")
    else:
        st.markdown("❤️ *Sé el primero en darle Me gusta*")
        
    with st.expander("📌 Más opciones"):
        if st.session_state.get('logged_in') and st.session_state['username'] == p_user:
            if st.button("🗑️ Eliminar", key=f"del_post_{p_id}"):
                c.execute("DELETE FROM posts WHERE id = ?", (p_id,))
                c.execute("DELETE FROM favorites WHERE post_id = ?", (p_id,))
                conn.commit()
                st.rerun()
        st.markdown("💬 **Comentarios**")
        st.text_input("Añade un comentario...", key=f"input_comm_{p_id}")
                
    st.markdown("---")

st.title("⚡ NoxVibe")
st.caption("✨ Red social inteligente con IA, Historias 24h y Banda Sonora.")

menu_options = [
    "👤 Mi Perfil", 
    "👥 Siguiendo", 
    "⏳ Muro 24h",
    "🔍 Explorar Canales", 
    "💬 Mensajes",
    "⚙️ Ajustes"
]

with st.sidebar:
    st.subheader("🧭 Menú")
    selected_tab = st.radio("Ir a:", menu_options, label_visibility="collapsed")
    st.markdown("---")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"], key="auth_radio")
        u_in = st.text_input("Usuario")
        p_in = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if u_in and p_in:
                    clean_user = u_in.strip().replace("@", "")
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (clean_user, make_hashes(p_in)))
                        conn.commit()
                        st.success("¡Registrado!")
                    except sqlite3.IntegrityError:
                        st.error("El usuario ya existe.")
        else:
            if st.button("Entrar"):
                clean_user = u_in.strip().replace("@", "")
                res = c.execute("SELECT password FROM users WHERE username = ?", (clean_user,)).fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = clean_user
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **@{st.session_state['username']}**")
        u_data = c.execute("SELECT xp, profile_pic FROM users WHERE username = ?", (st.session_state['username'],)).fetchone()
        if u_data and u_data[1] and os.path.exists(u_data[1]):
            st.image(u_data[1], width=80)
        st.metric("Tus XP", u_data[0] if u_data else 0)
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()

st.markdown("---")

if selected_tab == "👤 Mi Perfil":
    st.subheader("👤 Tu Perfil y Canal")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        u_info = c.execute("SELECT bio, city, xp, profile_pic, music_link FROM users WHERE username = ?", (cur,)).fetchone()
        
        with st.expander("⚙️ Editar Perfil", expanded=False):
            with st.form("edit_profile_form"):
                new_bio = st.text_area("Biografía", value=u_info[0] if u_info else "")
                new_city = st.text_input("Ciudad", value=u_info[1] if u_info else "")
                new_music = st.text_input("Enlace Musical", value=u_info[4] if u_info and len(u_info) > 4 and u_info[4] else "")
                new_pic = st.file_uploader("Foto de perfil", type=["jpg", "png", "jpeg"])
                
                if st.form_submit_button("Guardar"):
                    pic_path = u_info[3] if u_info else ""
                    if new_pic is not None:
                        os.makedirs("uploads", exist_ok=True)
                        pic_path = os.path.join("uploads", f"profile_{cur}_{new_pic.name}")
                        with open(pic_path, "wb") as f:
                            f.write(new_pic.getbuffer())
                    c.execute("UPDATE users SET bio = ?, city = ?, profile_pic = ?, music_link = ? WHERE username = ?", (new_bio, new_city, pic_path, new_music, cur))
                    conn.commit()
                    st.rerun()

        if u_info and u_info[3] and os.path.exists(u_info[3]):
            st.image(u_info[3], width=110)
        st.markdown(f"### @{cur}")
        
        st.subheader("📝 Publicar Contenido")
        with st.form("new_post_form", clear_on_submit=True):
            cap = st.text_area("¿Qué estás pensando?")
            uploaded_file = st.file_uploader("Sube foto o vídeo", type=["jpg", "png", "mp4", "mov"])
            
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
                
                c.execute("INSERT INTO posts (username, caption, file, file_type, likes, vibe_tag, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", (cur, cap, path_to_save, f_type, 0, auto_tag, now_str))
                c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (cur,))
                conn.commit()
                st.success(f"¡Publicado! {ai_msg} (+15 XP)")
                st.rerun()
                
        my_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? ORDER BY id DESC", (cur,)).fetchall()
        for p in my_posts:
            render_post(p[0], cur, p[1], p[2], p[3], p[4], p[5], p[6])
    else:
        st.warning("Inicia sesión para ver tu perfil.")

elif selected_tab == "👥 Siguiendo":
    st.subheader("👥 Actividad de Seguidos")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        following = [row[0] for row in c.execute("SELECT followed FROM follows WHERE follower = ?", (cur,)).fetchall()]
        if not following:
            st.info("Aún no sigues a nadie.")
        else:
            for f_user in following:
                f_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? ORDER BY id DESC", (f_user,)).fetchall()
                for p in f_posts:
                    render_post(p[0], f_user, p[1], p[2], p[3], p[4], p[5], p[6])
    else:
        st.warning("Inicia sesión.")

elif selected_tab == "⏳ Muro 24h":
    st.subheader("⏳ Muro Efímero (24h)")
    all_posts = c.execute("SELECT id, username, caption, file, file_type, likes, vibe_tag, timestamp FROM posts ORDER BY id DESC").fetchall()
    active_stories = []
    now = datetime.now()
    for p in all_posts:
        if p[7]:
            try:
                p_dt = datetime.strptime(p[7], "%Y-%m-%d %H:%M")
                if now - p_dt <= timedelta(hours=24):
                    active_stories.append(p)
            except ValueError:
                active_stories.append(p)
        else:
            active_stories.append(p)
            
    if not active_stories:
        st.info("No hay historias activas.")
    else:
        for p in active_stories:
            render_post(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])

elif selected_tab == "🔍 Explorar Canales":
    st.subheader("🔍 Explorar Canales")
    all_users = [u[0] for u in c.execute("SELECT username FROM users").fetchall()]
    if all_users:
        target_user = st.selectbox("Selecciona usuario:", all_users)
        if target_user:
            u_data = c.execute("SELECT username, bio, city, xp, profile_pic FROM users WHERE username = ?", (target_user,)).fetchone()
            st.markdown(f"### @{u_data[0]} (XP: {u_data[3]})")
            st.markdown(f"**Bio:** {u_data[1]} | **Ciudad:** {u_data[2]}")
            
            current_user = st.session_state.get('username', '')
            if current_user and current_user != target_user:
                is_following = c.execute("SELECT 1 FROM follows WHERE follower = ? AND followed = ?", (current_user, target_user)).fetchone()
                if is_following:
                    if st.button("❌ Dejar de seguir"):
                        c.execute("DELETE FROM follows WHERE follower = ? AND followed = ?", (current_user, target_user))
                        conn.commit()
                        st.rerun()
                else:
                    if st.button("➕ Seguir"):
                        c.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (current_user, target_user))
                        conn.commit()
                        st.rerun()
            
            ex_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag, timestamp FROM posts WHERE username = ? ORDER BY id DESC", (target_user,)).fetchall()
            for p in ex_posts:
                render_post(p[0], target_user, p[1], p[2], p[3], p[4], p[5], p[6])

elif selected_tab == "💬 Mensajes":
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        users_list = [u[0] for u in c.execute("SELECT username FROM users WHERE username != ?", (cur,)).fetchall()]
        if users_list:
            partner = st.selectbox("Para:", users_list)
            if partner:
                msgs = c.execute("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (cur, partner, partner, cur)).fetchall()
                for s, m, t in msgs:
                    st.markdown(f"**{s}:** {m} *({t})*")
                with st.form(key="chat", clear_on_submit=True):
                    txt_msg = st.text_input("Mensaje...")
                    if st.form_submit_button("Enviar"):
                        if txt_msg.strip():
                            c.execute("INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", (cur, partner, txt_msg.strip(), datetime.now().strftime("%H:%M")))
                            conn.commit()
                            st.rerun()
    else:
        st.warning("Inicia sesión.")

elif selected_tab == "⚙️ Ajustes":
    st.subheader("⚙️ Ajustes")
    st.success("NoxVibe configurado correctamente.")
    
