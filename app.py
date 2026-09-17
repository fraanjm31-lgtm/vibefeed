import streamlit as st
import os
import sqlite3
import hashlib
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="VibeFeed Quantum Edition",
    page_icon="🌌",
    layout="centered"
)

# Estilos CSS avanzados con soporte dinámico para Modo Oscuro/Claro
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

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            bio TEXT DEFAULT 'Creador Cuántico 🌌',
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
            duel_opponent TEXT DEFAULT ''
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

st.title("🌌 VibeFeed Quantum Suite")
st.caption("✨ Red social descentralizada con Cápsulas PIN, Algoritmo Democrático, Duelos, Ágora IA y Ajustes Pro.")

# Sidebar de acceso
with st.sidebar:
    st.subheader("🔐 Acceso Cuántico")
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
        st.metric("Tus Puntos XP", xp_val)
        
        if st.button("Cerrar Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.rerun()
    st.markdown("---")
    st.write("Versión 9.1 - Quantum Settings Pro")

# Menú completo con todas las pestañas ordenadas exactamente
menu = st.tabs([
    "📱 Feed", 
    "🗳️ AlgoDemocracia", 
    "⚔️ VibeDuels", 
    "🌌 Ágora IA", 
    "🔐 Cápsulas PIN", 
    "⏳ Historias", 
    "🌍 VibeMap", 
    "🏆 Desafíos", 
    "🔍 Buscar", 
    "# Tags", 
    "💬 Chats", 
    "🔔 Avisos", 
    "👤 Perfil", 
    "⚙️ Ajustes",
    "➕ Subir"
])

# 1. Feed
with menu[0]:
    st.subheader("Feed de la Comunidad")
    if st.session_state['logged_in']:
        c.execute("SELECT preference FROM algo_votes WHERE user = ?", (st.session_state['username'],))
        res_p = c.fetchone()
        pref_mode = res_p[0] if res_p else "Todo"
    else:
        pref_mode = "Todo"
        
    st.caption(f"⚙️ Algoritmo actual en vigor: **{pref_mode}**")
    
    query = "SELECT id, user, caption, file, file_type, likes, views, vibe_tag, secret_pin FROM posts WHERE is_story = 0 AND is_duel = 0"
    if pref_mode == "Solo Vídeos": query += " AND file_type LIKE '%video%'"
    elif pref_mode == "Solo Fotos": query += " AND file_type LIKE '%image%'"
    query += " ORDER BY id DESC"
    
    c.execute(query)
    for post in c.fetchall():
        post_id, user, caption, file_path, file_type, likes, views, vibe_tag, secret_pin = post
        if secret_pin and secret_pin.strip() != "":
            with st.container():
                st.markdown(f"### **{user}** 🔒 *[Cápsula Protegida]*")
                entered_pin = st.text_input(f"PIN para abrir post #{post_id}", type="password", key=f"pin_{post_id}")
                if entered_pin == secret_pin:
                    st.success(caption)
                    if file_path and os.path.exists(file_path):
                        if "video" in file_type: st.video(file_path)
                        else: st.image(file_path, use_container_width=True)
                st.markdown("---")
            continue

        with st.container():
            st.markdown(f"### **{user}**  `{vibe_tag}`")
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

# 2. AlgoDemocracia
with menu[1]:
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

# 3. VibeDuels
with menu[2]:
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

# 4. Ágora IA
with menu[3]:
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

# 5. Cápsulas PIN
with menu[4]:
    st.subheader("🔐 Cápsulas PIN")
    pin_s = st.text_input("Introduce clave secreta:")
    if pin_s:
        c.execute("SELECT user, caption, file FROM posts WHERE secret_pin = ?", (pin_s,))
        for rp in c.fetchall():
            st.success(f"@{rp[0]}: {rp[1]}")
            if rp[2] and os.path.exists(rp[2]): st.image(rp[2], use_container_width=True)

# 6. Historias
with menu[5]:
    st.subheader("⏳ Historias (24h)")
    c.execute("SELECT user, caption, file FROM posts WHERE is_story = 1 ORDER BY id DESC")
    for st_item in c.fetchall():
        st.markdown(f"**@{st_item[0]}**")
        st.write(st_item[1])
        if st_item[2] and os.path.exists(st_item[2]): st.image(st_item[2], use_container_width=True)
        st.markdown("---")

# 7. VibeMap
with menu[6]:
    st.subheader("🌍 VibeMap")
    c.execute("SELECT username, city, lat, lon FROM users")
    m_users = c.fetchall()
    if m_users:
        import pandas as pd
        st.map(pd.DataFrame(m_users, columns=['username', 'city', 'lat', 'lon'])[['lat', 'lon']])

# 8. Desafíos
with menu[7]:
    st.subheader("🏆 Desafíos")
    c.execute("SELECT title, description FROM challenges")
    chal = c.fetchone()
    if chal: st.info(f"### {chal[0]}\n{chal[1]}")

# 9. Buscar
with menu[8]:
    st.subheader("🔍 Buscar")
    sq = st.text_input("Usuario...")
    if sq:
        c.execute("SELECT username, bio, xp FROM users WHERE username LIKE ?", (f"%{sq}%",))
        for r in c.fetchall():
            st.markdown(f"### @{r[0]} (XP: {r[2]})\n*{r[1]}*")

# 10. Tags
with menu[9]:
    st.subheader("# Tags")
    tq = st.text_input("Etiqueta...")
    if tq:
        if not tq.startswith("#"): tq = "#" + tq
        c.execute("SELECT user, caption FROM posts WHERE caption LIKE ?", (f"%{tq}%",))
        for tp in c.fetchall(): st.write(f"**@{tp[0]}**: {tp[1]}")

# 11. Chats
with menu[10]:
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

# 12. Avisos
with menu[11]:
    st.subheader("🔔 Avisos")
    if st.session_state['logged_in']:
        st.info("No hay nuevas notificaciones push.")

# 13. Perfil
with menu[12]:
    st.subheader("👤 Perfil")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        c.execute("SELECT bio, city, xp FROM users WHERE username = ?", (cur,))
        u_info = c.fetchone()
        st.metric("XP", u_info[2])
        with st.form("p_up"):
            nb = st.text_area("Bio", value=u_info[0])
            nc = st.text_input("Ciudad", value=u_info[1])
            if st.form_submit_button("Guardar"):
                c.execute("UPDATE users SET bio = ?, city = ? WHERE username = ?", (nb, nc, cur))
                conn.commit()
                st.success("¡Guardado!")
                st.rerun()

# 14. Ajustes Pro (¡Arreglado y operativo!)
with menu[13]:
    st.subheader("⚙️ Ajustes Pro")
    
    st.markdown("### 🎨 Apariencia")
    sel_t = st.selectbox("Tema:", ["Modo Oscuro 🌙", "Modo Claro ☀️"], index=0 if st.session_state['theme']=="Modo Oscuro 🌙" else 1)
    if sel_t != st.session_state['theme']:
        st.session_state['theme'] = sel_t
        st.success("¡Tema aplicado!")
        st.rerun()
        
    st.markdown("---")
    
    if st.session_state['logged_in']:
        cur_user = st.session_state['username']
        
        st.markdown("### 🔔 Notificaciones")
        c.execute("SELECT notif_enabled FROM users WHERE username = ?", (cur_user,))
        n_status = c.fetchone()[0]
        n_toggle = st.toggle("Activar avisos", value=True if n_status==1 else False)
        if n_toggle != (n_status == 1):
            c.execute("UPDATE users SET notif_enabled = ? WHERE username = ?", (1 if n_toggle else 0, cur_user))
            conn.commit()
            st.toast("Actualizado")
            
        st.markdown("---")
        
        st.markdown("### 🔒 Seguridad")
        with st.form("pwd_f"):
            old_p = st.text_input("Contraseña Actual", type="password")
            new_p = st.text_input("Nueva Contraseña", type="password")
            if st.form_submit_button("Cambiar Contraseña"):
                c.execute("SELECT password FROM users WHERE username = ?", (cur_user,))
                if check_hashes(old_p, c.fetchone()[0]) and new_p:
                    c.execute("UPDATE users SET password = ? WHERE username = ?", (make_hashes(new_p), cur_user))
                    conn.commit()
                    st.success("¡Contraseña cambiada!")
                else:
                    st.error("Error en los datos.")
                    
        st.markdown("---")
        st.markdown("### ⚠️ Zona de Peligro")
        if st.button("🧹 Vaciar caché temporal"):
            import glob
            for f in glob.glob('uploads/*'):
                try: os.remove(f)
                except: pass
            st.success("Caché vaciada.")
            
        if st.button("🗑️ Borrar cuenta permanentemente", type="primary"):
            c.execute("DELETE FROM users WHERE username = ?", (cur_user,))
            c.execute("DELETE FROM posts WHERE user = ?", (cur_user,))
            conn.commit()
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.success("Cuenta eliminada.")
            st.rerun()
    else:
        st.info("Inicia sesión para ver ajustes.")

# 15. Subir
with menu[14]:
    st.subheader("➕ Subir Contenido")
    if st.session_state['logged_in']:
        with st.form("up_form", clear_on_submit=True):
            cap = st.text_area("Descripción...")
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
                    st.success("¡Publicado con éxito! 🚀")
                    st.rerun()
                else:
                    st.warning("Escribe algo.")
    else:
        st.warning("Inicia sesión para subir contenido.")
    
