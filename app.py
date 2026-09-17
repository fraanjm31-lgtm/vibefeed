import streamlit as st
import os

st.set_page_config(
    page_title="VibeFeed Pro",
    page_icon="🔥",
    layout="centered"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 VibeFeed Pro")
st.write("Tu red social vertical mejorada.")

# --- SECCIÓN 1: SUBIR NUEVO CONTENIDO ---
with st.expander("➕ Subir nuevo vídeo o foto"):
    with st.form("upload_form", clear_on_submit=True):
        username = st.text_input("Tu usuario", value="@creador")
        caption = st.text_area("Descripción del vídeo")
        uploaded_file = st.file_uploader("Sube tu archivo (MP4, MOV, JPG, PNG)", type=["mp4", "mov", "jpg", "png"])
        
        submit_button = st.form_submit_button(label="¡Publicar en el Feed!")
        
        if submit_button:
            if uploaded_file is not None:
                os.makedirs("uploads", exist_ok=True)
                file_path = os.path.join("uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if "posts" not in st.session_state:
                    st.session_state.posts = []
                
                st.session_state.posts.insert(0, {
                    "user": username,
                    "caption": caption,
                    "file": file_path,
                    "type": uploaded_file.type,
                    "likes": 0,
                    "comments": []
                })
                st.success("¡Publicado con éxito!")
            else:
                st.warning("Por favor, sube un archivo multimedia.")

# --- SECCIÓN 2: INICIALIZAR POSTS ---
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "user": "@creator_pro",
            "caption": "¡Lanzando mi nueva app web al mundo! 🚀✨",
            "file": None,
            "type": "default",
            "likes": 24,
            "comments": ["¡Qué pasada de app!", "Mucho éxito amigo."]
        },
        {
            "user": "@code_ninja",
            "caption": "Programando desde el móvil con Python 📱🐍",
            "file": None,
            "type": "default",
            "likes": 15,
            "comments": ["Increíble que se pueda hacer esto desde el teléfono."]
        }
    ]

# --- SECCIÓN 3: RENDERIZAR EL FEED ---
st.markdown("---")
st.subheader("📱 Feed en Directo")

for idx, post in enumerate(st.session_state.posts):
    st.markdown(f"### **{post['user']}**")
    st.write(post['caption'])
    
    if post['file'] and os.path.exists(post['file']):
        if "video" in post['type']:
            st.video(post['file'])
        elif "image" in post['type']:
            st.image(post['file'], use_container_width=True)
    else:
        st.info("🎬 [ Contenido multimedia interactivo VibeFeed ]")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(f"❤️ {post['likes']}", key=f"like_{idx}"):
            st.session_state.posts[idx]['likes'] += 1
            st.rerun()
            
    with st.expander(f"💬 Comentarios ({len(post['comments'])})"):
        for comment in post['comments']:
            st.text(f"• {comment}")
            
        new_comment = st.text_input("Añade un comentario...", key=f"comment_input_{idx}")
        if st.button("Enviar", key=f"send_comment_{idx}"):
            if new_comment:
                st.session_state.posts[idx]['comments'].append(new_comment)
                st.rerun()

    st.markdown("---"
