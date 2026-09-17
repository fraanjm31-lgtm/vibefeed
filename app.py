import streamlit as st
import os

st.set_page_config(
    page_title="VibeFeed Pro",
    page_icon="🔥",
    layout="centered"
)

st.title("🔥 VibeFeed Pro")
st.write("Tu red social vertical.")

# SECCIÓN 1: SUBIR CONTENIDO
with st.expander("➕ Subir nuevo vídeo o foto"):
    with st.form("up_form", clear_on_submit=True):
        user = st.text_input("Usuario", value="@creador")
        desc = st.text_area("Descripción")
        file = st.file_uploader("Archivo", type=["mp4", "mov", "jpg", "png"])
        
        btn = st.form_submit_button("Publicar")
        
        if btn:
            if file is not None:
                os.makedirs("uploads", exist_ok=True)
                path = os.path.join("uploads", file.name)
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                
                if "posts" not in st.session_state:
                    st.session_state.posts = []
                
                st.session_state.posts.insert(0, {
                    "user": user,
                    "caption": desc,
                    "file": path,
                    "type": file.type,
                    "likes": 0,
                    "comments": []
                })
                st.success("¡Publicado!")
            else:
                st.warning("Sube un archivo.")

# SECCIÓN 2: INICIALIZAR
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "user": "@creator_pro",
            "caption": "¡Lanzando app web! 🚀",
            "file": None,
            "type": "default",
            "likes": 24,
            "comments": ["¡Qué pasada!"]
        }
    ]

# SECCIÓN 3: FEED
st.markdown("---")
st.subheader("📱 Feed")

for idx, p in enumerate(st.session_state.posts):
    st.markdown(f"### **{p['user']}**")
    st.write(p['caption'])
    
    if p['file'] and os.path.exists(p['file']):
        if "video" in p['type']:
            st.video(p['file'])
        elif "image" in p['type']:
            st.image(p['file'], use_container_width=True)
    else:
        st.info("🎬 [ Clip multimedia ]")
    
    if st.button(f"❤️ {p['likes']}", key=f"l_{idx}"):
        st.session_state.posts[idx]['likes'] += 1
        st.rerun()
            
    with st.expander(f"💬 Comentarios ({len(p['comments'])})"):
        for c in p['comments']:
            st.text(f"• {c}")
        nc = st.text_input("Comentar...", key=f"nc_{idx}")
        if st.button("Enviar", key=f"sc_{idx}"):
            if nc:
                st.session_state.posts[idx]['comments'].append(nc)
                st.rerun()
    st.markdown("---")
