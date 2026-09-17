# --- 14. AJUSTES PRO (Tema, Notificaciones, Privacidad y Zona de Peligro) ---
with menu[13]:
    st.subheader("⚙️ Panel de Ajustes y Configuración")
    
    # 1. Cambiador de Tema
    st.markdown("### 🎨 Apariencia Visual")
    selected_theme = st.selectbox("Selecciona el tema de la aplicación:", ["Modo Oscuro 🌙", "Modo Claro ☀️"], index=0 if st.session_state['theme']=="Modo Oscuro 🌙" else 1)
    if selected_theme != st.session_state['theme']:
        st.session_state['theme'] = selected_theme
        st.success("¡Tema cambiado con éxito!")
        st.rerun()
        
    st.markdown("---")
    
    if st.session_state['logged_in']:
        cur_user = st.session_state['username']
        
        # 2. Gestión de Notificaciones
        st.markdown("### 🔔 Preferencias de Notificaciones")
        c.execute("SELECT notif_enabled FROM users WHERE username = ?", (cur_user,))
        n_res = c.fetchone()
        n_status = n_res[0] if n_res else 1
        notif_toggle = st.toggle("Activar avisos y alertas en la app", value=True if n_status == 1 else False)
        if notif_toggle != (n_status == 1):
            val_to_set = 1 if notif_toggle else 0
            c.execute("UPDATE users SET notif_enabled = ? WHERE username = ?", (val_to_set, cur_user))
            conn.commit()
            st.toast("Preferencia de notificaciones actualizada", icon="🔔")
            
        st.markdown("---")
        
        # 3. Privacidad de la Cuenta (Cambio de contraseña)
        st.markdown("### 🔒 Seguridad y Privacidad")
        with st.form("change_pwd_form"):
            st.write("Cambiar contraseña de acceso")
            old_p = st.text_input("Contraseña Actual", type="password")
            new_p = st.text_input("Nueva Contraseña", type="password")
            if st.form_submit_button("Actualizar Contraseña"):
                c.execute("SELECT password FROM users WHERE username = ?", (cur_user,))
                real_pwd_res = c.fetchone()
                if real_pwd_res and check_hashes(old_p, real_pwd_res[0]):
                    if new_p:
                        c.execute("UPDATE users SET password = ? WHERE username = ?", (make_hashes(new_p), cur_user))
                        conn.commit()
                        st.success("¡Contraseña actualizada correctamente!")
                    else:
                        st.warning("Introduce una nueva contraseña válida.")
                else:
                    st.error("La contraseña actual no es correcta.")
                    
        st.markdown("---")
        
        # 4. Zona de Peligro
        st.markdown("### ⚠️ Zona de Peligro")
        st.warning("Las siguientes acciones son irreversibles o afectan directamente a tus datos.")
        
        if st.button("🧹 Vaciar caché local de archivos temporales"):
            import glob
            files = glob.glob('uploads/*')
            for f in files:
                try: os.remove(f)
                except: pass
            st.success("¡Caché de archivos vaciada con éxito!")
            
        if st.button("🗑️ Eliminar mi cuenta permanentemente", type="primary"):
            c.execute("DELETE FROM users WHERE username = ?", (cur_user,))
            c.execute("DELETE FROM posts WHERE user = ?", (cur_user,))
            conn.commit()
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.error("Tu cuenta y tus publicaciones han sido eliminadas.")
            st.rerun()
    else:
        st.info("Inicia sesión para gestionar tus ajustes personales.")
    
