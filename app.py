import streamlit as st
import os
import sqlite3
import hashlib

st.set_page_config(page_title="NoxVibe", page_icon="⚡", layout="centered")

def get_custom_css(theme):
    bg_color = "#ffffff" if theme == "Modo Claro ☀️" else "#0e1117"
    text_color = "#0e1117" if theme == "Modo Claro ☀️" else "#fafafa"
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
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, bio TEXT DEFAULT "Creador NoxVibe ⚡", city TEXT DEFAULT "Madrid", xp INTEGER DEFAULT 100)')
    c.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT, PRIMARY KEY (follower, followed))')
    c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, vibe_tag TEXT DEFAULT "General 🌍", is_story INTEGER DEFAULT 0, is_duel INTEGER DEFAULT 0, gifts_received TEXT DEFAULT "")')
    c.execute('CREATE TABLE IF NOT EXISTS agora (id INTEGER PRIMARY KEY AUTOINCREMENT, thought TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS algo_votes (user TEXT PRIMARY KEY, preference TEXT)')
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

def get_badge(xp):
    if xp >= 300: return "⚡ Dios NoxVibe", "badge-cuantico"
    elif xp >= 180: return "🔥 Creador Pro", "badge-pro"
    return "🌱 Novato", "badge-novato"

st.title("⚡ NoxVibe")

with st.sidebar:
    st.subheader("🔐 Acceso")
    if not st.session_state['logged_in']:
        mode = st.radio("Modo:", ["Entrar", "Registro"])
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if mode == "Registro" and st.button("Crear"):
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, make_hashes(p)))
                conn.commit()
                st.success("¡Creado! Inicia sesión.")
            except: st.error("Usuario ya existe.")
        elif mode == "Entrar" and st.button("Login"):
            c.execute("SELECT password FROM users WHERE username = ?", (u,))
            res = c.fetchone()
            if res and check_hashes(p, res[0]):
                st.session_state['logged_in'] = True
                st.session_state['username'] = u
                st.rerun()
            else: st.error("Error.")
    else:
        st.success(f"@{st.session_state['username']}")
        if st.button("Salir"):
            st.session_state['logged_in'] = False
            st.rerun()

tab1, tab2, tab3 = st.tabs(["📱 Feed", "🚀 Lanzar", "📺 Canal"])

with tab1:
    st.subheader("Feed")
    c.execute("SELECT id, user, caption, file, file_type, likes, vibe_tag FROM posts ORDER BY id DESC")
    for row in c.fetchall():
        pid, user, cap, fpath, ftype, likes, vtag = row
        st.markdown(f"**@{user}** (`{vtag}`)")
        st.write(cap)
        if fpath and os.path.exists(fpath):
            if "video" in ftype: st.video(fpath)
            else: st.image(fpath)
        if st.button("❤️ Like", key=f"l_{pid}"):
            c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (pid,))
            conn.commit()
            st.rerun()
        st.markdown("---")

with tab2:
    st.subheader("Lanzar")
    if st.session_state['logged_in']:
        with st.form("up"):
            cap = st.text_input("Texto")
            file = st.file_uploader("Archivo", type=["jpg", "png", "mp4"])
            if st.form_submit_button("Publicar"):
                fpath, ftype = None, "none"
                if file:
                    os.makedirs("uploads", exist_ok=True)
                    fpath = os.path.join("uploads", file.name)
                    with open(fpath, "wb") as f: f.write(file.getbuffer())
                    ftype = file.type
                c.execute("INSERT INTO posts (user, caption, file, file_type, likes) VALUES (?, ?, ?, ?, 1)", 
                          (st.session_state['username'], cap, fpath, ftype))
                c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (st.session_state['username'],))
                conn.commit()
                st.success("¡Publicado!")
                st.rerun()
    else: st.warning("Inicia sesión.")

with tab3:
    st.subheader("Canal")
    target = st.session_state.get('username')
    if target:
        c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (target,))
        u = c.fetchone()
        if u:
            st.markdown(f"## @{target}")
            st.write(f"💬 {u[0]} | 📍 {u[1]} | ⚡ {u[2]} XP")
    else: st.warning("Inicia sesión para ver tu canal.")
        
