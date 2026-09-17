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

# Estilos CSS avanzados con colores dinámicos y soporte de temas
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

st.markdown(get_custom_css(st.session_state['theme']), unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- BASE DE DATOS ACTUALIZADA ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            bio TEXT DEFAULT 'Creador NoxVibe ⚡',
            city TEXT DEFAULT 'Madrid',
            lat REAL DEFAULT 40.4168,
            lon REAL DEFAULT -3.7038,
            xp INTEGER DEFAULT 100,
            notif_enabled INTEGER DEFAULT 1
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            caption TEXT,
            file TEXT,
            file_type TEXT,
            likes INTEGER,
            views INTEGER DEFAULT 0,
            vibe_tag TEXT DEFAULT 'General 🌍',
            is_story INTEGER DEFAULT 0,
            secret_pin TEXT DEFAULT '',
            is_duel INTEGER DEFAULT 0,
            duel_votes_a INTEGER DEFAULT 0,
            duel_votes_b INTEGER DEFAULT 0,
            duel_opponent TEXT DEFAULT '',
            gifts_received TEXT DEFAULT ''
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS agora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thought TEXT,
            constellation TEXT DEFAULT 'Filosofía 🌌',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS algo_votes (
            user TEXT PRIMARY KEY,
            preference TEXT
        )
    ''')

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
        c.execute("INSERT INTO challenges (title, description) VALUES (?, ?)", 
                  ("Reto #CodeMobile", "Comparte tu avance creando apps desde el móvil."))

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

# Sidebar de acceso y navegación optimizada para móvil
with st.sidebar:
    st.subheader("🔐 Acceso NoxVibe")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"])
        u_in = st.text_input("Usuario (@...)")
        p_in = st.text_input("Contraseña", type="password")
        
        if auth_mode == "Registrarse":
            if st.button("Crear Cuenta"):
                if u_in and p_in:
                    try:
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u_in, make_hashes(p_in)))
                        conn.commit()
                        st.success("¡Registrado con éxito!")
                    except sqlite3.IntegrityError:
                        st.error("El usuario ya existe.")
                else:
                    st.warning("Rellena los campos.")
        else:
            if st.button("Entrar"):
                c.execute("SELECT password FROM users WHERE username = ?", (u_in,))
                res = c.fetchone()
                if res and check_hashes(p_in, res[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u_in
                    st.success(f"¡Bienvenido, {u_in}!")
                    st.rerun()
                else:
                    st.error("Datos incorrectos.")
    else:
        st.success(f"Sesión: **{st.session_state['username']}**")
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
    st.subheader("🧭 Menú Principal")
    menu_option = st.selectbox("Selecciona sección:", [
        "📱 Feed", 
        "➕ Subir Contenido",
        "🏆 Leaderboard",
        "🗳️ AlgoDemocracia", 
        "⚔️ VibeDuels", 
        "🌌 Ágora IA", 
        "🔐 Cápsulas PIN", 
        "⏳ Historias", 
        "🌍 VibeMap", 
        "🎯 Desafíos", 
        "🔍 Buscar", 
        "# Tags", 
        "💬 Chats", 
        "🔔 Avisos", 
        "👤 Perfil", 
        "⚙️ Ajustes"
    ])
    st.markdown("---")
    st.write("Versión 9.4 - Mobile Pro")

# 1. Feed
if menu_option == "📱 Feed":
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
    for post in c.fetchall():
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag, secret_pin, gifts_received = post
        
        c.execute("SELECT xp FROM users WHERE username = ?", (user,))
        u_xp_res = c.fetchone()
        p_xp = u_xp_res[0] if u_xp_res else 100
        b_name, b_class = get_badge(p_xp)
        
        if secret_pin and secret_pin.strip() != "":
            with st.container():
                st.markdown(f"### **{user}** <span class='{b_class}'>{b_name}</span> 🔒 *[Cápsula]*", unsafe_allow_html=True)
                entered_pin = st.text_input(f"PIN para post #{post_id}", type="password", key=f"pin_{post_id}")
                if entered_pin == secret_pin:
                    st.success(caption)
                    if file_path and os.path.exists(file_path):
                        if "video" in file_type: st.video(file_path)
                        else: st.image(file_path, use_container_width=True)
                st.markdown("---")
            continue

        with st.container():
            st.markdown(f"### **{user}** <span class='{b_class}'>{b_name}</span>  `{vibe_tag}`", unsafe_allow_html=True)
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
                            st.success(f"¡Regalo enviado a @{user}!")
                            st.rerun()
                        else:
                            st.error("No tienes suficiente XP.")
            st.markdown("---")

# 2. Subir Contenido
elif menu_option == "➕ Subir Contenido":
    st.subheader("➕ Subir Contenido a NoxVibe")
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
            
            if st.form_submit_button("Publicar"):
                if cap:
                    path, f_type = None, "default"
                    if media is not None:
                        os.makedirs("uploads", exist_ok=True)
                        path = os.path.join("uploads", media.name)
                        with open(path, "wb") as f: f.write(media.getbuffer())
                        f_type = media.type
                    
                    c.execute('''
                        INSERT INTO posts (user, caption, file, file_type, likes, views, is_story, secret_pin, is_duel, duel_opponent)
                        VALUES (?, ?, ?, ?, 1, 0, ?, ?, ?, ?)
                    ''', (st.session_state['username'], cap, path, f_type, 1 if is_st else 0, pin, 1 if is_dl else 0, opp if is_dl else ""))
                    
                    c.execute("UPDATE users SET xp = xp + 10 WHERE username = ?", (st.session_state['username'],))
                    conn.commit()
                    st.success("¡Publicado con éxito! +10 XP ⚡")
                    st.rerun()
                else:
                    st.warning("Escribe algo.")
    else:
        st.warning("Inicia sesión para subir contenido.")

# 3. Leaderboard
elif menu_option == "🏆 Leaderboard":
    st.subheader("🏆 Salón de la Fama (Leaderboard)")
    st.caption("🌟 Los creadores con más experiencia (XP) de NoxVibe.")
    c.execute("SELECT username, xp, bio FROM users ORDER BY xp DESC LIMIT 10")
    leaders = c.fetchall()
    
    for idx, (l_user, l_xp, l_bio) in enumerate(leaders):
        b_name, b_class = get_badge(l_xp)
        medal = "🥇" if idx == 0 else ("🥈" if idx == 1 else ("🥉" if idx == 2 else f"#{idx+1}"))
        st.markdown(f"### {medal} @{l_user} <span class='{b_class}'>{b_name}</span>", unsafe_allow_html=True)
        st.write(f"💬 *{l_bio}*")
        st.caption(f"⚡ Puntos XP totales: **{l_xp}**")
        st.markdown("---")

# 4. AlgoDemocracia
elif menu_option == "🗳️ AlgoDemocracia":
    st.subheader("🗳️ Elige las Reglas del Algoritmo")
    if st.session_state['logged_in']:
        chosen_pref = st.radio("¿Cómo quieres que se ordene el feed?", ["Todo", "Solo Vídeos", "Solo Fotos", "Modo Sin Likes"])
        if st.button("Aplicar Voto"):
            c.execute("INSERT OR REPLACE INTO algo_votes (user, preference) VALUES (?, ?)", (st.session_state['username'], chosen_pref))
            conn.commit()
            st.success("¡Algoritmo actualizado!")
            st.rerun()
    else:
        st.warning("Inicia sesión para votar.")

# 5. VibeDuels
elif menu_option == "⚔️ VibeDuels":
    st.subheader("⚔️ VibeDuels: Batallas 1v1")
    c.execute("SELECT id, user, caption, file, file_type, duel_opponent FROM posts WHERE is_duel = 1")
    for d in c.fetchall():
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
elif menu_option == "🌌 Ágora IA":
    st.subheader("🌌 Ágora: Pensamientos Anónimos")
    if st.session_state['logged_in']:
        with st.form("ag_f", clear_on_submit=True):
            t_txt = st.text_area("Lanza una reflexión...")
            if st.form_submit_button("Publicar") and t_txt:
                c.execute("INSERT INTO agora (thought) VALUES (?)", (t_txt,))
                conn.commit()
                st.rerun()
    c.execute("SELECT thought, constellation, timestamp FROM agora ORDER BY id DESC")
    for ag in c.fetchall():
        st.markdown(f"> *\"{ag[0]}\"* \n\n 🏷️ `{ag[1]}`")
        st.markdown("---")

# 7. Cápsulas PIN
elif menu_option == "🔐 Cápsulas PIN":
    st.subheader("🔐 Cápsulas PIN")
    pin_s = st.text_input("Introduce clave secreta:")
    if pin_s:
        c.execute("SELECT user, caption, file FROM posts WHERE secret_pin = ?", (pin_s,))
        for rp in c.fetchall():
            st.success(f"@{rp[0]}: {rp[1]}")
            if rp[2] and os.path.exists(rp[2]): st.image(rp[2], use_container_width=True)

# 8. Historias
elif menu_option == "⏳ Historias":
    st.subheader("⏳ Historias (24h)")
    c.execute("SELECT user, caption, file FROM posts WHERE is_story = 1 ORDER BY id DESC")
    for st_item in c.fetchall():
        st.markdown(f"**@{st_item[0]}**")
        st.write(st_item[1])
        if st_item[2] and os.path.exists(st_item[2]): st.image(st_item[2], use_container_width=True)
        st.markdown("---")

# 9. VibeMap
elif menu_option == "🌍 VibeMap":
    st.subheader("🌍 VibeMap")
    c.execute("SELECT username, city, lat, lon FROM users")
    m_users = c.fetchall()
    if m_users:
        import pandas as pd
        st.map(pd.DataFrame(m_users, columns=['username', 'city', 'lat', 'lon'])[['lat', 'lon']])

# 10. Desafíos
elif menu_option == "🎯 Desafíos":
    st.subheader("🎯 Desafíos")
    c.execute("SELECT title, description FROM challenges")
    chal = c.fetchone()
    if chal: st.info(f"### {chal[0]}\n{chal[1]}")

# 11. Buscar
elif menu_option == "🔍 Buscar":
    st.subheader("🔍 Buscar Creadores")
    sq = st.text_input("Usuario...")
    if sq:
        c.execute("SELECT username, bio, xp FROM users WHERE username LIKE ?", (f"%{sq}%",))
        for r in c.fetchall():
            b_n, b_c = get_badge(r[2])
            st.markdown(f"### @{r[0]} <span class='{b_c}'>{b_n}</span> (XP: {r[2]})\n*{r[1]}*", unsafe_allow_html=True)

# 12. Tags
elif menu_option == "# Tags":
    st.subheader("# Tags")
    tq = st.text_input("Etiqueta...")
    if tq:
        if not tq.startswith("#"): tq = "#" + tq
        c.execute("SELECT user, caption FROM posts WHERE caption LIKE ?", (f"%{tq}%",))
        for tp in c.fetchall(): st.write(f"**@{tp[0]}**: {tp[1]}")

# 13. Chats
elif menu_option == "💬 Chats":
    st.subheader("💬 Chats")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT username FROM users WHERE username != ?", (cur,))
        others = [r[0] for r in c.fetchall()]
        if others:
            dest = st.selectbox("Hablar con:", others)
            c.execute("SELECT sender, message FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)", (cur, dest, dest, cur))
            for msg in c.fetchall(): st.text(f"@{msg[0]}: {msg[1]}")
            with st.form("dm", clear_on_submit=True):
                txt = st.text_input("Mensaje...")
                if st.form_submit_button("Enviar") and txt:
                    c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (cur, dest, txt))
                    conn.commit()
                    st.rerun()

# 14. Avisos
elif menu_option == "🔔 Avisos":
    st.subheader("🔔 Avisos")
    if st.session_state['logged_in']:
        st.info("Sin notificaciones pendientes.")

# 15. Perfil
elif menu_option == "👤 Perfil":
    st.subheader("👤 Perfil y Premios")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (cur,))
        u_info = c.fetchone()
        b_n, b_c = get_badge(u_info[2])
        st.metric("Puntos XP", u_info[2])
        st.markdown(f"**Tu Insig
