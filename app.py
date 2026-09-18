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
        profile_pic TEXT DEFAULT '',
        is_private INTEGER DEFAULT 0
    )
''')

try:
    c.execute("SELECT is_private FROM users LIMIT 1")
except sqlite3.OperationalError:
    c.execute("ALTER TABLE users ADD COLUMN is_private INTEGER DEFAULT 0")
    conn.commit()

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
if 'viewing_user' not in st.session_state:
    st.session_state['viewing_user'] = ''

def get_badge(xp):
    if xp >= 300:
        return "🔥 Creador Pro", "badge-pro"
    else:
        return "🌱 Novato", "badge-novato"

def render_post(p_id, p_user, p_cap, p_file, p_file_type, p_likes, p_tag):
    st.markdown(f"**@{p_user}** · *Tema: {p_tag}*")
    if p_cap:
        st.write(p_cap)
    if p_file and os.path.exists(p_file):
        if p_file_type == "video":
            st.video(p_file)
        else:
            st.image(p_file, use_container_width=True)
            
    if st.button("❤️ Me gusta", key=f"like_{p_id}"):
        c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (p_id,))
        conn.commit()
        st.rerun()
        
    if p_likes > 0:
        st.markdown(f"❤️ **Le gusta a {p_likes} personas**")
    else:
        st.markdown("❤️ *Sé el primero en darle Me gusta*")
        
    with st.expander("📌 Más opciones y comentarios"):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("💬 Comentar", key=f"com_{p_id}"):
                st.session_state[f"show_comments_{p_id}"] = not st.session_state.get(f"show_comments_{p_id}", False)
        with col_m2:
            st.button("🔄 Repost", key=f"rep_{p_id}")
        with col_m3:
            st.button("↗️ Compartir", key=f"sha_{p_id}")
        
        if st.session_state.get(f"show_comments_{p_id}", False):
            st.markdown("---")
            st.markdown("💬 **Comentarios:**")
            new_comment = st.text_input("Añade un comentario...", key=f"input_comm_{p_id}")
            if st.button("Publicar comentario", key=f"send_comm_{p_id}"):
                if new_comment.strip():
                    st.success("¡Comentario añadido!")
                    st.rerun()
                
    st.markdown("---")

st.title("⚡ NoxVibe")
st.caption("✨ Red social completa con XP, Canales y Perfiles.")

with st.sidebar:
    st.subheader("🧭 Menú NoxVibe")
    menu = st.radio("Ir a:", [
        "👤 Mi Perfil", 
        "👥 Siguiendo", 
        "🔍 Explorar Canales", 
        "💬 Mensajes Privados", 
        "⚙️ Ajustes"
    ])
    
    st.markdown("---")
    st.subheader("🔑 Tu Cuenta")
    if not st.session_state['logged_in']:
        auth_mode = st.radio("Modo:", ["Iniciar Sesión", "Registrarse"], key="auth_radio")
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
    st.subheader("💼 Buscar Creador")
    search_query = st.text_input("🔍 Apodo:", placeholder="Ej: Labachito")
    if st.button("Buscar"):
        clean_q = search_query.strip().replace("@", "")
        exists = c.execute("SELECT 1 FROM users WHERE username = ?", (clean_q,)).fetchone()
        if exists:
            st.session_state['viewing_user'] = clean_q
            st.success(f"¡Canal de @{clean_q} encontrado! Ve a 'Explorar Canales'.")
        else:
            st.error("Usuario no encontrado.")

if menu == "👤 Mi Perfil":
    st.subheader("👤 Tu Perfil y Canal")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        
        u_info = c.execute("SELECT bio, city, xp, profile_pic, is_private FROM users WHERE username = ?", (cur,)).fetchone()
        
        with st.expander("⚙️ Editar mi Perfil y Foto", expanded=False):
            with st.form("edit_profile_form"):
                new_bio = st.text_area("Biografía", value=u_info[0] if u_info else "")
                new_city = st.text_input("Ciudad", value=u_info[1] if u_info else "")
                new_pic = st.file_uploader("Sube nueva foto de perfil", type=["jpg", "png", "jpeg"])
                
                if st.form_submit_button("Guardar Cambios 💾"):
                    pic_path = u_info[3] if u_info else ""
                    if new_pic is not None:
                        os.makedirs("uploads", exist_ok=True)
                        pic_path = os.path.join("uploads", f"profile_{cur}_{new_pic.name}")
                        with open(pic_path, "wb") as f:
                            f.write(new_pic.getbuffer())
                    
                    c.execute("UPDATE users SET bio = ?, city = ?, profile_pic = ? WHERE username = ?", 
                              (new_bio, new_city, pic_path, cur))
                    conn.commit()
                    st.success("¡Perfil actualizado con éxito!")
                    st.rerun()

        num_posts = c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (cur,)).fetchone()[0]
        num_followers = c.execute("SELECT COUNT(*) FROM follows WHERE followed = ?", (cur,)).fetchone()[0]
        num_following = c.execute("SELECT COUNT(*) FROM follows WHERE follower = ?", (cur,)).fetchone()[0]
        
        if u_info and u_info[3] and os.path.exists(u_info[3]):
            st.image(u_info[3], width=110)
        else:
            st.markdown("📷 *Sin foto*")
            
        priv_status = "🔒 Privado" if (u_info and u_info[4] == 1) else "🌐 Público"
        st.markdown(f"### @{cur} ({priv_status})")
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; max-width: 280px; margin-bottom: 10px;">
                <div style="text-align: center; margin-right: 15px;">
                    <strong>{num_posts}</strong><br><span style="font-size: 13px; color: gray;">publicaciones</span>
                </div>
                <div style="text-align: center; margin-right: 15px;">
                    <strong>{num_followers}</strong><br><span style="font-size: 13px; color: gray;">seguidores</span>
                </div>
                <div style="text-align: center;">
                    <strong>{num_following}</strong><br><span style="font-size: 13px; color: gray;">seguidos</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
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
        st.warning("Inicia sesión en el menú lateral para gestionar tu perfil y publicar.")

elif menu == "👥 Siguiendo":
    st.subheader("👥 Actividad de Seguidos")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        following = [row[0] for row in c.execute("SELECT followed FROM follows WHERE follower = ?", (cur,)).fetchall()]
        if not following:
            st.info("Aún no sigues a nadie. Usa 'Explorar Canales' o busca perfiles en el menú lateral para ver contenido aquí.")
        else:
            for f_user in following:
                f_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (f_user,)).fetchall()
                for p in f_posts:
                    render_post(p[0], f_user, p[1], p[2], p[3], p[4], p[5])
    else:
        st.warning("Inicia sesión para ver la actividad de tus seguidos.")

elif menu == "🔍 Explorar Canales":
    st.subheader("🔍 Explorar Canales y Perfiles")
    
    all_users = [u[0] for u in c.execute("SELECT username FROM users").fetchall()]
    if all_users:
        selected_explore = st.selectbox("Selecciona un usuario para ver su canal:", all_users)
        target_user = selected_explore if selected_explore else (st.session_state.get('viewing_user') or all_users[0])
    else:
        target_user = st.session_state.get('viewing_user')
    
    if target_user:
        u_data = c.execute("SELECT username, bio, city, xp, profile_pic, is_private FROM users WHERE username = ?", (target_user,)).fetchone()
        if u_data:
            b_name, b_class = get_badge(u_data[3])
            
            t_posts = c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (target_user,)).fetchone()[0]
            t_followers = c.execute("SELECT COUNT(*) FROM follows WHERE followed = ?", (target_user,)).fetchone()[0]
            t_following = c.execute("SELECT COUNT(*) FROM follows WHERE follower = ?", (target_user,)).fetchone()[0]
            
            is_priv = (u_data[5] == 1)
            current_user = st.session_state.get('username', '')
            
            is_friend_or_owner = False
            if current_user == target_user:
                is_friend_or_owner = True
            elif is_priv and current_user:
                following_check = c.execute("SELECT 1 FROM follows WHERE follower = ? AND followed = ?", (current_user, target_user)).fetchone()
                if following_check:
                    is_friend_or_owner = True
            elif not is_priv:
                is_friend_or_owner = True

            if u_data[4] and os.path.exists(u_data[4]):
                st.image(u_data[4], width=110)
            else:
                st.markdown("📷")
                
            st.markdown(f"### @{u_data[0]} [{b_name}]" + (" 🔒 (Privado)" if is_priv else ""))
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; max-width: 280px; margin-bottom: 10px;">
                    <div style="text-align: center; margin-right: 15px;">
                        <strong>{t_posts}</strong><br><span style="font-size: 13px; color: gray;">publicaciones</span>
                    </div>
                    <div style="text-align: center; margin-right: 15px;">
                        <strong>{t_followers}</strong><br><span style="font-size: 13px; color: gray;">seguidores</span>
                    </div>
                    <div style="text-align: center;">
                        <strong>{t_following}</strong><br><span style="font-size: 13px; color: gray;">seguidos</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
                    
            st.markdown(f"**Bio:** {u_data[1]} | **Ciudad:** {u_data[2]} | **XP:** {u_data[3]}")
                
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
                            
            st.markdown("---")
            
            if is_friend_or_owner:
                user_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (target_user,)).fetchall()
                if not user_posts:
                    st.info("Este usuario aún no ha publicado nada.")
                else:
                    for p in user_posts:
                        render_post(p[0], target_user, p[1], p[2], p[3], p[4], p[5])
            else:
                st.warning("🔒 **Este canal es privado.** Debes seguir a este usuario para poder ver sus publicaciones.")
        else:
            st.info("Selecciona un usuario para ver su perfil.")
    else:
        st.info("No hay usuarios registrados todavía.")

elif menu == "💬 Mensajes Privados":
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        
        chat_conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
        chat_c = chat_conn.cursor()
        
        users_list = [u[0] for u in chat_c.execute("SELECT username FROM users WHERE username != ?", (cur,)).fetchall()]
        
        if not users_list:
            st.info("No hay más usuarios registrados para chatear.")
        else:
            partner = st.selectbox("Para:", users_list, key="chat_partner_final_definitivo")
            if partner:
                st.markdown(f"**Chat con @{partner}**")
                
                @st.fragment(run_every=3)
                def mostrar_mensajes_en_tiempo_real():
                    inner_conn = sqlite3.connect('vibefeed.db', check_same_thread=False)
                    inner_c = inner_conn.cursor()
                    
                    msgs = inner_c.execute("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY id ASC", (cur, partner, partner, cur)).fetchall()
                    
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

elif menu == "⚙️ Ajustes":
    st.subheader("⚙️ Ajustes y Privacidad")
    
    is_logged = st.session_state.get('logged_in', False)
    username = st.session_state.get('username', '')
    
    if is_logged and username:
        try:
            row_p = c.execute("SELECT is_private FROM users WHERE username = ?", (username,)).fetchone()
            cur_val = row_p[0] if row_p and row_p[0] is not None else 0
        except Exception:
            cur_val = 0
         
