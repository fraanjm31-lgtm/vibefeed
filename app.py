import streamlit as st
import os
import sqlite3
import hashlib
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="NoxVibe",
    page_icon="⚡",
    layout="centered"
)

# Estilos CSS avanzados para mantener el diseño impecable
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
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, bio TEXT DEFAULT "Creador NoxVibe ⚡", city TEXT DEFAULT "Madrid", lat REAL DEFAULT 40.4168, lon REAL DEFAULT -3.7038, xp INTEGER DEFAULT 100, notif_enabled INTEGER DEFAULT 1)')
    c.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT, PRIMARY KEY (follower, followed))')
    c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, caption TEXT, file TEXT, file_type TEXT, likes INTEGER, views INTEGER DEFAULT 0, vibe_tag TEXT DEFAULT "General 🌍", is_story INTEGER DEFAULT 0, secret_pin TEXT DEFAULT "", is_duel INTEGER DEFAULT 0, duel_votes_a INTEGER DEFAULT 0, duel_votes_b INTEGER DEFAULT 0, duel_opponent TEXT DEFAULT "", gifts_received TEXT DEFAULT "")')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS challenges (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS agora (id INTEGER PRIMARY KEY AUTOINCREMENT, thought TEXT, constellation TEXT DEFAULT "Filosofía 🌌", timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS algo_votes (user TEXT PRIMARY KEY, preference TEXT)')

    cols = [
        ("posts", "secret_pin", "TEXT DEFAULT ''"),
        ("posts", "is_duel", "INTEGER DEFAULT 0"),
        ("posts", "duel_votes_a", "INTEGER DEFAULT 0"),
        ("posts", "duel_votes_b", "INTEGER DEFAULT 0"),
        ("posts", "duel_opponent", "TEXT DEFAULT ''"),
        ("posts", "gifts_received", "TEXT DEFAULT ''"),
        ("users", "xp", "INTEGER DEFAULT 100"),
        ("users", "notif_enabled", "INTEGER DEFAULT 1")
    ]
    for table, col, defn in cols:
        try:
            c.execute(f"SELECT {col} FROM {table} LIMIT 1")
        except sqlite3.OperationalError:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")

    c.execute("SELECT COUNT(*) FROM challenges")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO challenges (title, description) VALUES (?, ?)", ("Reto #CodeMobile", "Comparte tu avance creando apps desde el móvil."))

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
st.caption("✨ Red social con Regalos XP, Leaderboard, Premios y Ajustes Pro.")

# Sidebar para el Acceso / Login y el Buscador de Canales
with st.sidebar:
    st.subheader("🔐 Acceso NoxVibe")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Apodo / Nombre de usuario (ej. labachito)")
        p_in = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if u_in and p_in:
                    clean_user = u_in.strip().replace("@", "")
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (clean_user, make_hashes(p_in)))
                        conn.commit()
                        st.success("¡Registrado con éxito! Ya puedes iniciar sesión.")
                    except sqlite3.IntegrityError:
                        st.error("Ese apodo ya está en uso. Elige otro.")
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
    st.subheader("📺 Explorar Canales")
    c.execute("SELECT username FROM users")
    all_users = [u[0] for u in c.fetchall()]
    if all_users:
        selected_search = st.selectbox("🔍 Buscar creador:", ["Selecciona..."] + all_users, key="sidebar_channel_select")
        if selected_search != "Selecciona...":
            st.session_state['viewing_user'] = selected_search
            st.success(f"Canal de @{selected_search} seleccionado. ¡Ve a la pestaña 'Canal'!")

# --- PESTAÑAS SUPERIORES HORIZONTALES ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📱 Feed", 
    "🚀 Lanzar", 
    "🏆 Top", 
    "🗳️ Algo", 
    "⚔️ Duels", 
    "🌌 Ágora", 
    "👤 Perfil", 
    "👥 Siguiendo",
    "📺 Canal",
    "⚙️ Ajustes"
])

# 1. Feed
with tab1:
    st.subheader("Feed de la Comunidad")
    if st.session_state['logged_in']:
        c.execute("SELECT preference FROM algo_votes WHERE user = ?", (st.session_state['username'],))
        res_p = c.fetchone()
        pref_mode = res_p[0] if res_p else "Todo"
    else:
        pref_mode = "Todo"
        
    query = "SELECT id, user, caption, file, file_type, likes, views, vibe_tag, secret_pin, gifts_received FROM posts WHERE is_story = 0 AND is_duel = 0"
    if pref_mode == "Solo Vídeos": query += " AND file_type LIKE '%video%'"
    elif pref_mode == "Solo Fotos": query += " AND file_type LIKE '%image%'"
    query += " ORDER BY id DESC"
    
    c.execute(query)
    posts = c.fetchall()
    
    if not posts:
        st.info("No hay publicaciones todavía. ¡Sé el primero en subir algo!")
    
    for post in posts:
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag, secret_pin, gifts_received = post
        
        c.execute("SELECT xp FROM users WHERE username = ?", (user,))
        u_xp_res = c.fetchone()
        p_xp = u_xp_res[0] if u_xp_res else 100
        b_name, b_class = get_badge(p_xp)

        with st.container():
            col_u1, col_u2 = st.columns([3, 1])
            with col_u1:
                st.markdown(f"### **@{user}** <span class='{b_class}'>{b_name}</span>  `{vibe_tag}`", unsafe_allow_html=True)
            with col_u2:
                if st.button("📺 Canal", key=f"visit_{post_id}_{user}"):
                    st.session_state['viewing_user'] = user
                    st.rerun()

            st.write(caption)
            if file_path and os.path.exists(file_path):
                if "video" in file_type: st.video(file_path)
                elif "image" in file_type: st.image(file_path, use_container_width=True)
            
            st.caption(f"❤️ {likes} likes | 👁️ {(views or 0) + 1} vistas {f'| {gifts_received}' if gifts_received else ''}")
            
            col_l, col_g = st.columns(2)
            with col_l:
                if st.button("❤️ Like", key=f"l_{post_id}"):
                    c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
                    conn.commit()
                    st.rerun()
            with col_g:
                if st.session_state['logged_in']:
                    gift_choice = st.selectbox("🎁 Regalo (-10 XP):", ["Selecciona...", "🌟 Estrellas", "💎 Gema", "☕ Café"], key=f"g_sel_{post_id}")
                    if st.button("Enviar", key=f"g_btn_{post_id}"):
                        cur = st.session_state['username']
                        c.execute("SELECT xp FROM users WHERE username = ?", (cur,))
                        my_xp = c.fetchone()[0]
                        if my_xp >= 10:
                            c.execute("UPDATE users SET xp = xp - 10 WHERE username = ?", (cur,))
                            c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (user,))
                            new_gift_str = f"{gifts_received} {gift_choice}" if gifts_received else gift_choice
                            c.execute("UPDATE posts SET gifts_received = ? WHERE id = ?", (new_gift_str, post_id))
                            conn.commit()
                            st.success(f"¡Regalo enviado al canal de @{user}!")
                            st.rerun()
                        else:
                            st.error("No tienes suficiente XP.")
            st.markdown("---")

# 2. Lanzar Contenido
with tab2:
    st.subheader("🚀 Lanzar Contenido a NoxVibe")
    if st.session_state['logged_in']:
        with st.form("up_form", clear_on_submit=True):
            cap = st.text_input("Descripción...")
            media = st.file_uploader("Multimedia", type=["mp4", "mov", "jpg", "jpeg", "png"])
            is_st = st.checkbox("⏳ Historia (24h)")
            is_dl = st.checkbox("⚔️ VibeDuel 1v1")
            c.execute("SELECT username FROM users WHERE username != ?", (st.session_state['username'],))
            opps = [r[0] for r in c.fetchall()]
            opp = st.selectbox("Rival", opps) if opps else ""
            pin = st.text_input("🔐 PIN secreto (opcional)")
            
            if st.form_submit_button("¡Lanzar Vibe! ⚡"):
                if cap or media is not None:
                    path, f_type = None, "default"
                    if media is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", media.name)
                        with open(path, "wb") as f: f.write(media.getbuffer())
                        f_type = media.type
                    
                    c.execute("INSERT INTO posts (user, caption, file, file_type, likes, views, is_story, secret_pin, is_duel, duel_opponent) VALUES (?, ?, ?, ?, 1, 0, ?, ?, ?, ?)", (st.session_state['username'], cap, path, f_type, 1 if is_st else 0, pin, 1 if is_dl else 0, opp if is_dl else ""))
                    c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (st.session_state['username'],))
                    conn.commit()
                    st.success("¡Lanzado con éxito! +10 XP ⚡")
                    st.rerun()
                else:
                    st.warning("Escribe algo o sube un archivo.")
    else:
        st.warning("Inicia sesión en el menú lateral para lanzar contenido.")

# 3. Leaderboard
with tab3:
    st.subheader("🏆 Salón de la Fama")
    c.execute("SELECT username, xp, bio FROM users ORDER BY xp DESC LIMIT 10")
    leaders = c.fetchall()
    if not leaders:
        st.info("Todavía no hay usuarios registrados.")
    for idx, (l_user, l_xp, l_bio) in enumerate(leaders):
        b_name, b_class = get_badge(l_xp)
        medal = "🥇" if idx == 0 else ("🥈" if idx == 1 else ("🥉" if idx == 2 else f"#{idx+1}"))
        
        col_l1, col_l2 = st.columns([3, 1])
        with col_l1:
            st.markdown(f"### {medal} @{l_user} <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
            st.write(f"💬 *{l_bio}*")
            st.caption(f"⚡ XP totales: **{l_xp}**")
        with col_l2:
            if st.button("📺 Canal", key=f"lead_visit_{l_user}"):
                st.session_state['viewing_user'] = l_user
                st.rerun()
        st.markdown("---")

# 4. AlgoDemocracia
with tab4:
    st.subheader("🗳️ Reglas del Algoritmo")
    if st.session_state['logged_in']:
        chosen_pref = st.radio("¿Cómo quieres ver el feed?", ["Todo", "Solo Vídeos", "Solo Fotos"])
        if st.button("Aplicar Voto"):
            c.execute("INSERT OR REPLACE INTO algo_votes (user, preference) VALUES (?, ?)", (st.session_state['username'], chosen_pref))
            conn.commit()
            st.success("¡Actualizado!")
            st.rerun()
    else:
        st.warning("Inicia sesión para votar.")

# 5. VibeDuels
with tab5:
    st.subheader("⚔️ VibeDuels 1v1")
    c.execute("SELECT id, user, caption, file, file_type, duel_opponent FROM posts WHERE is_duel = 1")
    duels = c.fetchall()
    if not duels:
        st.info("No hay duelos activos ahora mismo.")
    for d in duels:
        d_id, d_user, d_cap, d_file, d_type, d_opp = d
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**@{d_user}**")
            st.write(d_cap)
            if d_file and os.path.exists(d_file): st.image(d_file, use_container_width=True)
            if st.button(f"Votar @{d_user}", key=f"va_{d_id}"):
                c.execute("UPDATE posts SET duel_votes_a = duel_votes_a + 1 WHERE id = ?", (d_id,))
                c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (d_user,))
                conn.commit()
                st.rerun()
        with col2:
            st.markdown(f"**@{d_opp}**")
            st.write("¡En combate!")
            if st.button(f"Votar @{d_opp}", key=f"vb_{d_id}"):
                c.execute("UPDATE posts SET duel_votes_b = duel_votes_b + 1 WHERE id = ?", (d_id,))
                c.execute("UPDATE users SET xp = xp + 15 WHERE username = ?", (d_opp,))
                conn.commit()
                st.rerun()
        st.markdown("---")

# 6. Ágora IA
with tab6:
    st.subheader("🌌 Ágora: Reflexiones")
    if st.session_state['logged_in']:
        with st.form("ag_f", clear_on_submit=True):
            t_txt = st.text_area("Lanza un pensamiento...")
            if st.form_submit_button("Publicar") and t_txt:
                c.execute("INSERT INTO agora (thought) VALUES (?)", (t_txt,))
                conn.commit()
                st.rerun()
    c.execute("SELECT thought, constellation FROM agora ORDER BY id DESC")
    agoras = c.fetchall()
    if not agoras:
        st.info("No hay reflexiones en el ágora.")
    for ag in agoras:
        st.markdown(f"> *\"{ag[0]}\"* \n\n 🏷️ `{ag[1]}`")
        st.markdown("---")

# 7. Perfil
with tab7:
    st.subheader("👤 Tu Perfil")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (cur,))
        u_info = c.fetchone()
        b_n, b_c = get_badge(u_info[2])
        st.metric("Puntos XP", u_info[2])
        st.markdown(f"**Insignia:** <span class='{b_c}'>{b_n}</span>", unsafe_allow_html=True)
        
        with st.form("p_up"):
            nb = st.text_area("Bio", value=u_info[0])
            nc = st.text_input("Ciudad", value=u_info[1])
            if st.form_submit_button("Guardar"):
                c.execute("UPDATE users SET bio = ?, city = ? WHERE username = ?", (nb, nc, cur))
                conn.commit()
                st.success("¡Guardado!")
                st.rerun()
    else:
        st.warning("Inicia sesión en el menú lateral para ver tu perfil.")

# 8. Mis Siguiendo
with tab8:
    st.subheader("👥 Creadores a los que Sigues")
    if st.session_state['logged_in']:
        cur_user = st.session_state['username']
        c.execute("SELECT followed FROM follows WHERE follower = ?", (cur_user,))
        followed_list = [f[0] for f in c.fetchall()]
        
        if not followed_list:
            st.info("Todavía no sigues a nadie. ¡Visita los canales de otros creadores y dándole al botón de seguir!")
        else:
            for f_user in followed_list:
                c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (f_user,))
                f_data = c.fetchone()
                if f_data:
                    f_bio, f_city, f_xp = f_data
                    f_badge, f_bclass = get_badge(f_xp)
                    
                    col_f1, col_f2 = st.columns([3, 1])
                    with col_f1:
                        st.markdown(f"### **@{f_user}** <span class='{f_bclass}'>{f_badge}</span>", unsafe_allow_html=True)
                        st.write(f"💬 *{f_bio}*")
                        st.caption(f"⚡ XP: {f_xp}")
                    with col_f2:
                        if st.button("📺 Canal", key=f"f_visit_{f_user}"):
                            st.session_state['viewing_user'] = f_user
                            st.rerun()
                    st.markdown("---")
    else:
        st.warning("Inicia sesión para ver a tus creadores seguidos.")

# 9. Canal Personal del Creador seleccionado
with tab9:
    st.subheader("📺 Canal de Creador")
    
    if not st.session_state.get('viewing_user') and st.session_state['logged_in']:
        st.session_state['viewing_user'] = st.session_state['username']
        
    target_user = st.session_state.get('viewing_user')
    
    if not target_user:
        st.info("Usa el menú lateral izquierdo (buscador) para explorar el canal de cualquier creador.")
    else:
        c.execute("SELECT username, bio, city, xp FROM users WHERE LOWER(username) = LOWER(?)", (target_user,))
        u_data = c.fetchone()
        
        if u_data:
            real_username, u_bio, u_city, u_xp = u_data
            b_name, b_class = get_badge(u_xp)
            
            col_h1, col_h2 = st.columns([3, 1])
            with col_h1:
                st.markdown(f"## Canal de **@{real_username}** <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
                st.write(f"💬 *{u_bio or 'Creador NoxVibe'}*")
                st.caption(f"📍 Ciudad: {u_city or 'Madrid'} | ⚡ XP Totales: **{u_xp}**")
            with col_h2:
                if st.session_state['logged_in'] and st.session_state['username'].lower() != real_username.lower():
                    cur = st.session_state['username']
                    c.execute("SELECT * FROM follows WHERE follower = ? 
