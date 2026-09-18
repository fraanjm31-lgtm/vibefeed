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

def render_post(p_id, p_user, p_cap, p_file, p_file_type, p_likes, p_tag):
    st.markdown(f"**@{p_user}** · *Tema: {p_tag}*")
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
                st.warning("Inicia sesión para guardar favoritos.")
            else:
                if is_fav:
                    c.execute("DELETE FROM favorites WHERE username = ? AND post_id = ?", (current_user, p_id))
                    conn.commit()
                    st.success("Eliminado de guardados.")
                else:
                    c.execute("INSERT INTO favorites (username, post_id) VALUES (?, ?)", (current_user, p_id))
                    conn.commit()
                    st.success("¡Guardado en favoritos!")
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
            
        if st.session_state.get('logged_in') and st.session_state['username'] == p_user:
            st.markdown("---")
            if st.button("🗑️ Eliminar esta publicación", key=f"del_post_{p_id}"):
                c.execute("DELETE FROM posts WHERE id = ?", (p_id,))
                c.execute("DELETE FROM favorites WHERE post_id = ?", (p_id,))
                conn.commit()
                st.success("¡Publicación eliminada!")
                st.rerun()
        
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

menu_options = [
    "👤 Mi Perfil", 
    "👥 Siguiendo", 
    "🔍 Explorar Canales", 
    "💬 Mensajes",
    "⚙️ Ajustes"
]

# Menú lateral (Intacto como pediste)
with st.sidebar:
    st.subheader("🧭 Menú Principal")
    selected_tab = st.radio("Ir a:", menu_options, label_visibility="collapsed")

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

st.markdown("---")

if selected_tab == "👤 Mi Perfil":
    st.subheader("👤 Tu Perfil y Canal")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        
        u_info = c.execute("SELECT bio, city, xp, profile_pic FROM users WHERE username = ?", (cur,)).fetchone()
        
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
            
        st.markdown(f"### @{cur}")
        
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
        
        tab_mi_fotos, tab_mi_videos, tab_mi_favs = st.tabs(["📸 Fotos", "🎥 Vídeos", "🔖 Guardados"])
        
        with tab_mi_fotos:
            my_photos = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? AND (file_type != 'video' OR file_type = '') ORDER BY id DESC", (cur,)).fetchall()
            if not my_photos:
                st.info("No tienes fotos publicadas.")
            else:
                for p in my_photos:
                    render_post(p[0], cur, p[1], p[2], p[3], p[4], p[5])
                    
        with tab_mi_videos:
            my_vids = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? AND file_type = 'video' ORDER BY id DESC", (cur,)).fetchall()
            if not my_vids:
                st.info("No tienes vídeos publicados.")
            else:
                for p in my_vids:
                    render_post(p[0], cur, p[1], p[2], p[3], p[4], p[5])

        with tab_mi_favs:
            fav_posts = c.execute("""
                SELECT p.id, p.username, p.caption, p.file, p.file_type, p.likes, p.vibe_tag 
                FROM posts p JOIN favorites f ON p.id = f.post_id 
                WHERE f.username = ? ORDER BY p.id DESC
            """, (cur,)).fetchall()
            if not fav_posts:
                st.info("No tienes publicaciones guardadas como favoritas.")
            else:
                for p in fav_posts:
                    render_post(p[0], p[1], p[2], p[3], p[4], p[5], p[6])
    else:
        st.warning("Inicia sesión para gestionar tu perfil y publicar.")

elif selected_tab == "👥 Siguiendo":
    st.subheader("👥 Actividad de Seguidos")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        following = [row[0] for row in c.execute("SELECT followed FROM follows WHERE follower = ?", (cur,)).fetchall()]
        if not following:
            st.info("Aún no sigues a nadie. Usa 'Explorar Canales' o busca perfiles para ver contenido aquí.")
        else:
            for f_user in following:
                f_posts = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? ORDER BY id DESC", (f_user,)).fetchall()
                for p in f_posts:
                    render_post(p[0], f_user, p[1], p[2], p[3], p[4], p[5])
    else:
        st.warning("Inicia sesión para ver la actividad de tus seguidos.")

elif selected_tab == "🔍 Explorar Canales":
    st.subheader("🔍 Explorar Canales y Perfiles")
    
    all_users = [u[0] for u in c.execute("SELECT username FROM users").fetchall()]
    if all_users:
        selected_explore = st.selectbox("Selecciona un usuario para ver su canal:", all_users)
        target_user = selected_explore if selected_explore else (st.session_state.get('viewing_user') or all_users[0])
    else:
        target_user = st.session_state.get('viewing_user')
    
    if target_user:
        u_data = c.execute("SELECT username, bio, city, xp, profile_pic FROM users WHERE username = ?", (target_user,)).fetchone()
        if u_data:
            b_name, b_class = get_badge(u_data[3])
            
            t_posts = c.execute("SELECT COUNT(*) FROM posts WHERE username = ?", (target_user,)).fetchone()[0]
            t_followers = c.execute("SELECT COUNT(*) FROM follows WHERE followed = ?", (target_user,)).fetchone()[0]
            t_following = c.execute("SELECT COUNT(*) FROM follows WHERE follower = ?", (target_user,)).fetchone()[0]
            
            current_user = st.session_state.get('username', '')

            if u_data[4] and os.path.exists(u_data[4]):
                st.image(u_data[4], width=110)
            else:
                st.markdown("📷")
                
            st.markdown(f"### @{u_data[0]} [{b_name}]")
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
            
            tab_ex_fotos, tab_ex_videos = st.tabs(["📸 Fotos", "🎥 Vídeos"])
            
            with tab_ex_fotos:
                ex_photos = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? AND (file_type != 'video' OR file_type = '') ORDER BY id DESC", (target_user,)).fetchall()
                if not ex_photos:
                    st.info("Este usuario no tiene fotos publicadas.")
                else:
                    for p in ex_photos:
                        render_post(p[0], target_user, p[1], p[2], p[3], p[4], p[5])
                        
            with tab_ex_videos:
                ex_vids = c.execute("SELECT id, caption, file, file_type, likes, vibe_tag FROM posts WHERE username = ? AND file_type = 'video' ORDER BY id DESC", (target_user,)).fetchall()
                if not ex_vids:
                    st.info("Este usuario no tiene vídeos publicados.")
                else:
                    for p in ex_vids:
                        render_post(p[0], target_user, p[1], p[2], p[3], p[4], p[5])
        else:
            st.info("Selecciona un usuario para ver su perfil.")
    else:
        st.info("No hay usuarios registrados todavía.")

elif selected_tab == "💬 Mensajes":
    st.subheader("💬 Mensajes Privados")
    if st.session_state['logged_in']:
        cur = st.session_state['username']
        users_list = [u[0] for u in c.execute("SELECT username FROM users WHERE username != ?", (cur,)).fetchall()]
        
        if not users_list:
            st.info("No hay más usuarios registrados para chatear.")
        else:
            partner = st.selectbox("Para:", users_list, k
