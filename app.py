import streamlit as st

# Configuración de la página con nuevo nombre
st.set_page_config(page_title="VibeFeed", page_icon="⚡")

st.title("⚡ VibeFeed")
st.write("¡Comparte y descubre momentos rápidos con todo el mundo!")

# Inicializar los datos en la memoria de la sesión web si no existen
if "feed" not in st.session_state:
    st.session_state.feed = [
        {
            "usuario": "@creator_pro",
            "descripcion": "¡Lanzando mi nueva app web al mundo! 🚀✨",
            "likes": 24,
            "comentarios": ["¡Mucho éxito!", "¡Brutal diseño! 🔥"]
        },
        {
            "usuario": "@code_ninja",
            "descripcion": "Programando desde el móvil con Python 📱🐍",
            "likes": 15,
            "comentarios": ["¡Qué nivelazo!", "Crack total"]
        }
    ]

# --- SECCIÓN: Tu Perfil y Publicación (Sidebar) ---
st.sidebar.header("👤 Tu Perfil")
usuario = st.sidebar.text_input("Nombre de usuario", "@tu_cuenta")

st.sidebar.markdown("---")
st.sidebar.subheader("📤 Crear nuevo Vibe")
nueva_desc = st.sidebar.text_area("¿Qué estás pensando o qué video tienes?")
if st.sidebar.button("Publicar Vibe"):
    if nueva_desc:
        nuevo_post = {
            "usuario": usuario if usuario else "@invitado",
            "descripcion": nueva_desc,
            "likes": 0,
            "comentarios": []
        }
        st.session_state.feed.append(nuevo_post)
        st.sidebar.success("¡Publicado con éxito en el feed!")
    else:
        st.sidebar.error("Escribe algo para publicar.")

# --- SECCIÓN: Feed Principal (Estilo vertical) ---
st.subheader("🔥 Feed en Directo")

for i, post in enumerate(st.session_state.feed):
    st.markdown(f"### **{post['usuario']}**")
    st.write(post['descripcion'])
    
    # Contenedor visual simulando reproductor
    st.info("▶️ [ Reproduciendo clip multimedia ]")
    
    # Botón de Likes
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"❤️ Me gusta ({post['likes']})", key=f"like_{i}"):
            st.session_state.feed[i]["likes"] += 1
            st.rerun()
            
    # Sección de comentarios desplegable
    with st.expander(f"💬 Comentarios ({len(post['comentarios'])})"):
        for com in post['comentarios']:
            st.write(f"- {com}")
            
        # Caja para dejar un comentario
        comentario_texto = st.text_input("Escribe un comentario...", key=f"com_input_{i}")
        if st.button("Enviar", key=f"btn_com_{i}"):
            if comentario_texto:
                autor = usuario if usuario else "@invitado"
                st.session_state.feed[i]["comentarios"].append(f"{autor}: {comentario_texto}")
                st.rerun()
                
    st.markdown("---")
  
